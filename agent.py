import os
import json
import yfinance as yf
import pandas as pd
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

# Check for API key
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise ValueError("GEMINI_API_KEY not set in environment.")

# --- TOOL 1: Financial Metrics ---
def get_peer_financials(tickers: list[str]) -> str:
    """
    Fetches core financial metrics (Revenue, Gross Margin, Operating Margin, Net Income)
    for a list of stock tickers (e.g., ['INTC', 'NVDA', 'AMD', 'TSM']).
    Returns the data formatted as a JSON string.
    """
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

# --- INITIALIZE GEMINI CLIENT ---
client = genai.Client(api_key=api_key)

SYSTEM_INSTRUCTION = """
You are an expert Equity Research Analyst specializing in the semiconductor industry.
Your role is to benchmark Intel (INTC) against its key competitors (NVDA, AMD, TSM).

Always use your tools to fetch live financial data when answering quantitative questions.
Provide clear, structured financial insights, focusing on margins, revenue growth, and market positioning.
"""

def chat_with_agent():
    # Create an interactive chat session with automatic function calling enabled
    chat = client.chats.create(
        model="gemini-2.5-flash",
        config=types.GenerateContentConfig(
            system_instruction=SYSTEM_INSTRUCTION,
            tools=[get_peer_financials],  # Handing our function directly to Gemini
            temperature=0.2
        )
    )

    print("==========================================================")
    print("Semiconductor Peer Benchmarking Agent Online!")
    print("Ask any question (e.g. 'How does Intel's gross margin compare to AMD and NVDA?')")
    print("Type 'exit' to stop.")
    print("==========================================================\n")

    while True:
        user_input = input("You: ")
        if user_input.lower() in ["exit", "quit"]:
            print("Shutting down agent session. Goodbye!")
            break

        print("\nAgent thinking & executing tools...")
        response = chat.send_message(user_input)
        print(f"\nAgent: {response.text}\n")

if __name__ == "__main__":
    chat_with_agent()
