import pandas as pd
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]

PROCESSED_FOLDER = PROJECT_ROOT / "Dataset" / "processed"

stocks = {
    "ETERNAL": "ETERNAL_NS_clean.csv",
    "IRFC": "IRFC_NS_clean.csv",
    "RVNL": "RVNL_NS_clean.csv",
    "RAILTEL": "RAILTEL_NS_clean.csv",
    "TORRENTPOWER": "TORRENTPOWER_NS_clean.csv",
}

for stock, filename in stocks.items():

    print(f"\n========== {stock} ==========")

    file_path = PROCESSED_FOLDER / filename

    try:
        df = pd.read_csv(file_path)

        df["Date"] = pd.to_datetime(df["Date"])

        print(f"Rows: {len(df)}")
        print(f"Columns: {len(df.columns)}")
        print(f"Start Date: {df['Date'].min().date()}")
        print(f"End Date: {df['Date'].max().date()}")

        # Missing values
        missing = df.isnull().sum().sum()
        print(f"Missing Values: {missing}")

        # Duplicate dates
        duplicates = df["Date"].duplicated().sum()
        print(f"Duplicate Dates: {duplicates}")

        # Date sorting
        sorted_correctly = df["Date"].is_monotonic_increasing
        print(f"Date Sorted: {sorted_correctly}")

        # Price validation
        invalid_prices = (
            (df["Open"] <= 0) |
            (df["High"] <= 0) |
            (df["Low"] <= 0) |
            (df["Close"] <= 0)
        ).sum()

        print(f"Invalid Prices: {invalid_prices}")

        # OHLC validation
        invalid_ohlc = (
            (df["High"] < df["Low"]) |
            (df["High"] < df["Open"]) |
            (df["High"] < df["Close"]) |
            (df["Low"] > df["Open"]) |
            (df["Low"] > df["Close"])
        ).sum()

        print(f"Invalid OHLC Rows: {invalid_ohlc}")

        # Volume validation
        negative_volume = (df["Volume"] < 0).sum()
        print(f"Negative Volume: {negative_volume}")

        if (
            missing == 0
            and duplicates == 0
            and sorted_correctly
            and invalid_prices == 0
            and invalid_ohlc == 0
            and negative_volume == 0
        ):
            print("✅ VALIDATION PASSED")
        else:
            print("⚠️ VALIDATION NEEDS ATTENTION")

    except Exception as e:
        print(f"❌ Error: {e}")

print("\n========== VALIDATION COMPLETE ==========")