"""
Netflix Financial Ratio Analysis
---------------------------------
Reads the Income Statement, Balance Sheet, and Cash Flow CSVs produced by
fetch_netflix_financials.py, and calculates key financial ratios across
the available fiscal years:

    Profitability : Gross Margin, Net Margin, ROE, ROA
    Liquidity     : Current Ratio, Quick Ratio
    Leverage      : Debt-to-Equity
    Growth        : Revenue Growth YoY

Output: netflix_financials/financial_ratios_summary.csv
        (rows = ratios, columns = fiscal years)

Requirements:
    pip install pandas
"""

import pandas as pd
import os

INPUT_DIR = "netflix_financials"
OUTPUT_FILE = os.path.join(INPUT_DIR, "financial_ratios_summary.csv")


def load_statement(filename: str) -> pd.DataFrame:
    """Load a financial statement CSV with line items as the row index."""
    path = os.path.join(INPUT_DIR, filename)
    df = pd.read_csv(path, index_col=0)
    return df


def get_row(df: pd.DataFrame, possible_labels: list) -> pd.Series:
    """
    Look up a line item by trying several possible label spellings,
    since yfinance's exact naming can vary between versions.
    Returns a Series of values across years, or None if not found.
    """
    for label in possible_labels:
        if label in df.index:
            return df.loc[label]
    print(f"Warning: none of {possible_labels} found in statement.")
    return None


def calculate_ratios(income: pd.DataFrame, balance: pd.DataFrame, cash_flow: pd.DataFrame) -> pd.DataFrame:
    """Calculate profitability, liquidity, leverage, growth, EPS, and free cash flow."""

    # --- Pull the raw line items we need ---
    revenue = get_row(income, ["Total Revenue"])
    gross_profit = get_row(income, ["Gross Profit"])
    net_income = get_row(income, ["Net Income"])
    diluted_eps = get_row(income, ["Diluted EPS"])

    total_assets = get_row(balance, ["Total Assets"])
    total_equity = get_row(balance, ["Stockholders Equity", "Total Stockholder Equity"])
    total_liabilities = get_row(balance, ["Total Liabilities Net Minority Interest", "Total Liab"])
    current_assets = get_row(balance, ["Current Assets", "Total Current Assets"])
    current_liabilities = get_row(balance, ["Current Liabilities", "Total Current Liabilities"])
    inventory = get_row(balance, ["Inventory"])

    operating_cash_flow = get_row(cash_flow, ["Operating Cash Flow", "Total Cash From Operating Activities"])
    capital_expenditure = get_row(cash_flow, ["Capital Expenditure", "Capital Expenditures"])

    ratios = pd.DataFrame(index=revenue.index)

    # --- Profitability ---
    ratios["Gross Margin %"] = (gross_profit / revenue) * 100
    ratios["Net Margin %"] = (net_income / revenue) * 100
    ratios["ROE %"] = (net_income / total_equity) * 100
    ratios["ROA %"] = (net_income / total_assets) * 100

    # --- Liquidity ---
    ratios["Current Ratio"] = current_assets / current_liabilities
    if inventory is not None:
        ratios["Quick Ratio"] = (current_assets - inventory) / current_liabilities
    else:
        # Netflix has no meaningful inventory line, so Quick Ratio ~= Current Ratio
        ratios["Quick Ratio"] = current_assets / current_liabilities

    # --- Leverage ---
    ratios["Debt-to-Equity"] = total_liabilities / total_equity

    # --- Growth (Year-over-Year revenue growth) ---
    # Note: yfinance columns are usually ordered most-recent-year first,
    # so we reverse before computing pct_change, then reverse back.
    revenue_chrono = revenue[::-1]
    growth_chrono = revenue_chrono.pct_change() * 100
    ratios["Revenue Growth YoY %"] = growth_chrono[::-1]

    # --- Per-share and cash generation ---
    if diluted_eps is not None:
        ratios["Diluted EPS ($)"] = diluted_eps

    if operating_cash_flow is not None and capital_expenditure is not None:
        # Capital Expenditure is usually stored as a negative number (cash outflow),
        # so Free Cash Flow = Operating Cash Flow + Capital Expenditure
        ratios["Free Cash Flow ($M)"] = (operating_cash_flow + capital_expenditure) / 1_000_000

    # Round for readability
    ratios = ratios.round(2)

    return ratios.transpose()  # ratios as rows, years as columns


def main():
    print("Loading financial statements...")
    income = load_statement("income_statement.csv")
    balance = load_statement("balance_sheet.csv")
    cash_flow = load_statement("cash_flow.csv")

    print("Calculating ratios...")
    ratios_summary = calculate_ratios(income, balance, cash_flow)

    ratios_summary.to_csv(OUTPUT_FILE)
    print(f"\nSaved ratio summary to: {os.path.abspath(OUTPUT_FILE)}")
    print("\nPreview:")
    print(ratios_summary)


if __name__ == "__main__":
    main()