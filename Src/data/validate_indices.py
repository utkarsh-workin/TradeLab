import pandas as pd
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]

PROCESSED_FOLDER = PROJECT_ROOT / "Dataset" / "processed"

indices = {
    "NIFTY50": "NIFTY50_clean.csv",
    "BANKNIFTY": "BANKNIFTY_clean.csv",
    "SENSEX": "SENSEX_clean.csv",
}

for index_name, filename in indices.items():

    print(f"\n========== {index_name} ==========")

    file_path = PROCESSED_FOLDER / filename

    try:
        df = pd.read_csv(file_path)

        df["Date"] = pd.to_datetime(df["Date"])

        print(f"Rows: {len(df)}")
        print(f"Columns: {len(df.columns)}")
        print(f"Start Date: {df['Date'].min().date()}")
        print(f"End Date: {df['Date'].max().date()}")

        missing = df.isnull().sum().sum()
        duplicates = df["Date"].duplicated().sum()
        sorted_correctly = df["Date"].is_monotonic_increasing

        invalid_prices = (
            (df["Open"] <= 0) |
            (df["High"] <= 0) |
            (df["Low"] <= 0) |
            (df["Close"] <= 0)
        ).sum()

        invalid_ohlc = (
            (df["High"] < df["Low"]) |
            (df["High"] < df["Open"]) |
            (df["High"] < df["Close"]) |
            (df["Low"] > df["Open"]) |
            (df["Low"] > df["Close"])
        ).sum()

        print(f"Missing Values: {missing}")
        print(f"Duplicate Dates: {duplicates}")
        print(f"Date Sorted: {sorted_correctly}")
        print(f"Invalid Prices: {invalid_prices}")
        print(f"Invalid OHLC Rows: {invalid_ohlc}")

        if (
            missing == 0
            and duplicates == 0
            and sorted_correctly
            and invalid_prices == 0
            and invalid_ohlc == 0
        ):
            print("✅ VALIDATION PASSED")
        else:
            print("⚠️ VALIDATION NEEDS ATTENTION")

    except Exception as e:
        print(f"❌ Error: {e}")

print("\n========== INDEX VALIDATION COMPLETE ==========")