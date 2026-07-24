import yfinance as yf
import pandas as pd
import json

# Define our peer group
TICKERS = ["INTC", "TSM", "AMD", "NVDA"]

def fetch_financial_metrics(tickers):
    """
    Fetches revenue, gross margins, and net income for a list of stock tickers.
    """
    summary_data = []

    for ticker in tickers:
        print(f"Fetching data for {ticker}...")
        stock = yf.Ticker(ticker)
        info = stock.info

        # Extract core fundamental metrics
        revenue = info.get("totalRevenue", None)
        gross_margins = info.get("grossMargins", None)
        net_income = info.get("netIncomeToCommon", None)
        operating_margins = info.get("operatingMargins", None)

        summary_data.append({
            "Ticker": ticker,
            "Company Name": info.get("shortName", ticker),
            "Revenue ($B)": round(revenue / 1e9, 2) if revenue else "N/A",
            "Gross Margin (%)": round(gross_margins * 100, 2) if gross_margins else "N/A",
            "Operating Margin (%)": round(operating_margins * 100, 2) if operating_margins else "N/A",
            "Net Income ($B)": round(net_income / 1e9, 2) if net_income else "N/A"
        })

    return pd.DataFrame(summary_data)

if __name__ == "__main__":
    df = fetch_financial_metrics(TICKERS)
    
    # Print clean summary table to console
    print("\n=== SEMICONDUCTOR PEER BENCHMARKING ===")
    print(df.to_string(index=False))

    # Save to local file so we don't re-download every time
    df.to_json("peer_financials.json", orient="records", indent=4)
    print("\nSaved financial data to 'peer_financials.json'")
