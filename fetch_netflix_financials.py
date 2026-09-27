"""
Netflix Financial Statement Data Extraction
---------------------------------------------
Pulls historical Income Statement, Balance Sheet, and Cash Flow Statement
data for Netflix (NFLX) from Yahoo Finance using the yfinance library,
and saves each as a clean CSV file for later analysis in Python/Power BI.

Requirements:
    pip install yfinance pandas
"""

import yfinance as yf
import pandas as pd
import os

# Ticker symbol for the company we're analyzing
TICKER = "NFLX"

# Folder where the raw financial statement CSVs will be saved
OUTPUT_DIR = "netflix_financials"


def create_output_folder(path: str) -> None:
    """Create the output directory if it doesn't already exist."""
    os.makedirs(path, exist_ok=True)


def fetch_financial_statements(ticker_symbol: str) -> dict:
    """
    Fetch the three core financial statements for a given ticker.

    yfinance returns annual data by default (last ~4 years) via these
    properties. Rows = line items (e.g. Total Revenue), Columns = fiscal years.

    Returns a dict of {statement_name: DataFrame}.
    """
    ticker = yf.Ticker(ticker_symbol)

    statements = {
        "income_statement": ticker.financials,        # Income Statement
        "balance_sheet": ticker.balance_sheet,         # Balance Sheet
        "cash_flow": ticker.cashflow,                  # Cash Flow Statement
    }

    return statements


def save_statements_to_csv(statements: dict, output_dir: str) -> None:
    """Save each financial statement DataFrame as a separate CSV file."""
    for name, df in statements.items():
        if df.empty:
            print(f"Warning: '{name}' came back empty — check the ticker or try again later.")
            continue

        file_path = os.path.join(output_dir, f"{name}.csv")
        df.to_csv(file_path)
        print(f"Saved: {file_path}  ({df.shape[0]} line items x {df.shape[1]} years)")


def main():
    create_output_folder(OUTPUT_DIR)

    print(f"Fetching financial statements for {TICKER}...")
    statements = fetch_financial_statements(TICKER)

    save_statements_to_csv(statements, OUTPUT_DIR)

    print("\nDone. Files are ready in:", os.path.abspath(OUTPUT_DIR))


if __name__ == "__main__":
    main()
