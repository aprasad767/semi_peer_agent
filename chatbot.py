import os
import json
import streamlit as st
import yfinance as yf
from google import genai
from google.genai import types

# Page setup
st.set_page_config(page_title="Semiconductor Analyst Chatbot", page_icon="🤖", layout="wide")

st.title("🤖 Semiconductor Peer Benchmarking Chatbot")
st.caption("Ask questions about INTC, NVDA, AMD, and TSM financial metrics.")

# Safely resolve API Key from Streamlit secrets or environment variables
api_key = None

try:
    if "GEMINI_API_KEY" in st.secrets:
        api_key = st.secrets["GEMINI_API_KEY"]
except Exception:
    pass

if not api_key:
    api_key = os.getenv("GEMINI_API_KEY")

# Initialize Gemini client
client = genai.Client(api_key=api_key)

# Define live market data tool with full valuation metrics
def get_peer_financials(tickers: list[str]) -> str:
    """Fetches comprehensive live valuation and financial performance metrics for tickers."""
    summary_data = []
    for ticker in tickers:
        try:
            stock = yf.Ticker(ticker)
            info = stock.info
            
            # Helper function for clean numeric rounding
            def format_num(val, divisor=1, is_percent=False):
                if val is None or val == "N/A":
                    return "N/A"
                if is_percent:
                    return f"{round(val * 100, 2)}%"
                return round(val / divisor, 2)

            summary_data.append({
                "Ticker": ticker,
                "Company": info.get("shortName", ticker),
                # Valuation Metrics
                "Market Cap ($B)": format_num(info.get("marketCap"), 1e9),
                "Forward P/E": format_num(info.get("forwardPE")),
                "Trailing P/E": format_num(info.get("trailingPE")),
                "PEG Ratio": format_num(info.get("pegRatio")),
                "EV/EBITDA": format_num(info.get("enterpriseToEbitda")),
                "Price to Book": format_num(info.get("priceToBook")),
                # Profitability & Margins
                "Revenue ($B)": format_num(info.get("totalRevenue"), 1e9),
                "Gross Margin": format_num(info.get("grossMargins"), is_percent=True),
                "Operating Margin": format_num(info.get("operatingMargins"), is_percent=True),
                "Profit Margin": format_num(info.get("profitMargins"), is_percent=True),
                "Net Income ($B)": format_num(info.get("netIncomeToCommon"), 1e9),
                # Balance Sheet & Growth
                "Free Cash Flow ($B)": format_num(info.get("freeCashflow"), 1e9),
                "Total Debt ($B)": format_num(info.get("totalDebt"), 1e9),
                "Revenue Growth (YoY)": format_num(info.get("revenueGrowth"), is_percent=True)
            })
        except Exception as e:
            summary_data.append({"Ticker": ticker, "Error": str(e)})

    return json.dumps(summary_data, indent=2)

SYSTEM_INSTRUCTION = """
You are an expert Equity Research Analyst specializing in the semiconductor industry.
You benchmark Intel (INTC) against NVDA, AMD, and TSM.
Always fetch live financial data using your tools when answering quantitative questions.
"""

# Initialize persistent chat session in Streamlit
if "chat" not in st.session_state:
    st.session_state.chat = client.chats.create(
        model="gemini-2.5-flash",
        config=types.GenerateContentConfig(
            system_instruction=SYSTEM_INSTRUCTION,
            tools=[get_peer_financials],
            temperature=0.2
        )
    )

if "messages" not in st.session_state:
    st.session_state.messages = []

# Display prior chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# User prompt handling
if user_prompt := st.chat_input("Ask about Intel's margins vs competitors..."):
    st.chat_message("user").markdown(user_prompt)
    st.session_state.messages.append({"role": "user", "content": user_prompt})

    with st.chat_message("assistant"):
        with st.spinner("Analyzing semiconductor data..."):
            response = st.session_state.chat.send_message(user_prompt)
            st.markdown(response.text)
            st.session_state.messages.append({"role": "assistant", "content": response.text})
