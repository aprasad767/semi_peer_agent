from edgar import Company, set_identity
import pandas as pd

# SEC EDGAR requires user identification (Name and Email)
set_identity("Aditya Prasad aditya.prasad@example.com")

TICKERS = ["INTC", "AMD", "NVDA"]

def get_latest_sec_filings(tickers):
    """
    Fetches details on the latest 10-K and 10-Q filings for each ticker.
    """
    filing_records = []
    
    for ticker in tickers:
        print(f"Querying SEC EDGAR for {ticker}...")
        try:
            comp = Company(ticker)
            
            # Fetch recent 10-K and 10-Q filings
            ten_k = comp.get_filings(form="10-K").latest()
            ten_q = comp.get_filings(form="10-Q").latest()
            
            if ten_k:
                filing_records.append({
                    "Ticker": ticker,
                    "Form": "10-K (Annual)",
                    "Filing Date": ten_k.filing_date,
                    "Accession No": ten_k.accession_no
                })
            
            if ten_q:
                filing_records.append({
                    "Ticker": ticker,
                    "Form": "10-Q (Quarterly)",
                    "Filing Date": ten_q.filing_date,
                    "Accession No": ten_q.accession_no
                })
        except Exception as e:
            print(f"Error fetching SEC data for {ticker}: {e}")

    return pd.DataFrame(filing_records)

if __name__ == "__main__":
    df_sec = get_latest_sec_filings(TICKERS)
    
    print("\n=== RECENT SEC FILINGS ===")
    print(df_sec.to_string(index=False))
    
    # Save filing metadata locally
    df_sec.to_json("sec_filings.json", orient="records", indent=4)
    print("\nSaved SEC filing metadata to 'sec_filings.json'")
