import pandas as pd
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]

RAW_FOLDER = PROJECT_ROOT / "Dataset" / "raw"
PROCESSED_FOLDER = PROJECT_ROOT / "Dataset" / "processed"

PROCESSED_FOLDER.mkdir(parents=True, exist_ok=True)

stocks = {
    "ETERNAL": "ETERNAL_NS_raw.csv",
    "IRFC": "IRFC_NS_raw.csv",
    "RVNL": "RVNL_NS_raw.csv",
    "RAILTEL": "RAILTEL_NS_raw.csv",
    "TORRENTPOWER": "TORRENTPOWER_NS_raw.csv",
}

for stock, filename in stocks.items():

    print(f"\nCleaning {stock}...")

    input_file = RAW_FOLDER / filename

    try:
        df = pd.read_csv(input_file)

        # Convert Date
        df["Date"] = pd.to_datetime(df["Date"], errors="coerce")

        # Required columns
        required_columns = [
            "Date",
            "Open",
            "High",
            "Low",
            "Close",
            "Volume"
        ]

        df = df[required_columns]

        # Convert numeric columns
        numeric_columns = [
            "Open",
            "High",
            "Low",
            "Close",
            "Volume"
        ]

        for column in numeric_columns:
            df[column] = pd.to_numeric(
                df[column],
                errors="coerce"
            )

        # Remove invalid rows
        df = df.dropna(subset=required_columns)

        # Remove duplicate dates
        df = df.drop_duplicates(subset=["Date"])

        # Sort by date
        df = df.sort_values("Date").reset_index(drop=True)

        # Basic OHLC validation
        df = df[
            (df["High"] >= df["Low"]) &
            (df["High"] >= df["Open"]) &
            (df["High"] >= df["Close"]) &
            (df["Low"] <= df["Open"]) &
            (df["Low"] <= df["Close"]) &
            (df["Volume"] >= 0)
        ]

        output_file = PROCESSED_FOLDER / f"{stock}_NS_clean.csv"

        df.to_csv(output_file, index=False)

        print(f"✅ {stock} cleaned")
        print(f"Rows: {len(df)}")
        print(f"Saved: {output_file}")

    except Exception as e:
        print(f"❌ Error cleaning {stock}: {e}")

print("\n========== CLEANING COMPLETE ==========")