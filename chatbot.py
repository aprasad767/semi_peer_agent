import os
import json
import streamlit as st
import yfinance as yf
from google import genai
from google.genai import types

st.set_page_config(page_title="Semiconductor Analyst Chatbot", page_icon="🤖", layout="wide")

st.title("🤖 Semiconductor Peer Benchmarking Chatbot")
st.caption("Ask questions about INTC, NVDA, AMD, and TSM financial metrics.")

api_key = st.secrets.get("GEMINI_API_KEY") or os.getenv("GEMINI_API_KEY")

if not api_key:
    st.error("Please set GEMINI_API_KEY in your environment or Streamlit secrets.")
    st.stop()

client = genai.Client(api_key=api_key)

def get_peer_financials(tickers: list[str]) -> str:
    """Fetches live revenue, margins, and net income for tickers."""
    summary_data = []
    for ticker in tickers:
        try:
            stock = yf.Ticker(ticker)
            info = stock.info
            revenue = info.get("totalRevenue", None)
            gross_margins = info.get("grossMargins", None)
            net_income = info.get("netIncomeToCommon", None)
            operating_margins = info.get("operatingMargins", None)

            summary_data.append({
                "Ticker": ticker,
                "Company": info.get("shortName", ticker),
                "Revenue ($B)": round(revenue / 1e9, 2) if revenue else "N/A",
                "Gross Margin (%)": round(gross_margins * 100, 2) if gross_margins else "N/A",
                "Operating Margin (%)": round(operating_margins * 100, 2) if operating_margins else "N/A",
                "Net Income ($B)": round(net_income / 1e9, 2) if net_income else "N/A"
            })
        except Exception as e:
            summary_data.append({"Ticker": ticker, "Error": str(e)})

    return json.dumps(summary_data, indent=2)

SYSTEM_INSTRUCTION = """
You are an expert Equity Research Analyst specializing in the semiconductor industry.
Benchmarking Intel (INTC) against NVDA, AMD, and TSM.
Always fetch financial data using your tools when asked quantitative questions.
"""

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

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if user_prompt := st.chat_input("Ask about Intel's margins vs competitors..."):
    st.chat_message("user").markdown(user_prompt)
    st.session_state.messages.append({"role": "user", "content": user_prompt})

    with st.chat_message("assistant"):
        with st.spinner("Analyzing semiconductor data..."):
            response = st.session_state.chat.send_message(user_prompt)
            st.markdown(response.text)
            st.session_state.messages.append({"role": "assistant", "content": response.text})
