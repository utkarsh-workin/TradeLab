import pandas as pd
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]

RAW_FOLDER = PROJECT_ROOT / "Dataset" / "raw"
PROCESSED_FOLDER = PROJECT_ROOT / "Dataset" / "processed"

PROCESSED_FOLDER.mkdir(parents=True, exist_ok=True)

indices = {
    "NIFTY50": "NIFTY50_raw.csv",
    "BANKNIFTY": "BANKNIFTY_raw.csv",
    "SENSEX": "SENSEX_raw.csv",
}

for index_name, filename in indices.items():

    print(f"\nCleaning {index_name}...")

    input_file = RAW_FOLDER / filename

    try:
        df = pd.read_csv(input_file)

        # Convert Date
        df["Date"] = pd.to_datetime(df["Date"], errors="coerce")

        # Keep standard OHLC columns
        required_columns = [
            "Date",
            "Open",
            "High",
            "Low",
            "Close"
        ]

        # Volume is optional for indices
        if "Volume" in df.columns:
            required_columns.append("Volume")

        df = df[required_columns]

        # Convert numeric columns
        numeric_columns = [
            "Open",
            "High",
            "Low",
            "Close"
        ]

        if "Volume" in df.columns:
            numeric_columns.append("Volume")

        for column in numeric_columns:
            df[column] = pd.to_numeric(
                df[column],
                errors="coerce"
            )

        # Remove missing values
        df = df.dropna(subset=[
            "Date",
            "Open",
            "High",
            "Low",
            "Close"
        ])

        # Remove duplicate dates
        df = df.drop_duplicates(subset=["Date"])

        # Sort by date
        df = df.sort_values("Date").reset_index(drop=True)

        # OHLC validation
        df = df[
            (df["High"] >= df["Low"]) &
            (df["High"] >= df["Open"]) &
            (df["High"] >= df["Close"]) &
            (df["Low"] <= df["Open"]) &
            (df["Low"] <= df["Close"])
        ]

        # Remove invalid prices
        df = df[
            (df["Open"] > 0) &
            (df["High"] > 0) &
            (df["Low"] > 0) &
            (df["Close"] > 0)
        ]

        # Remove negative volume if available
        if "Volume" in df.columns:
            df = df[df["Volume"] >= 0]

        output_file = (
            PROCESSED_FOLDER /
            f"{index_name}_clean.csv"
        )

        df.to_csv(output_file, index=False)

        print(f"✅ {index_name} cleaned")
        print(f"Rows: {len(df)}")
        print(f"Columns: {len(df.columns)}")
        print(f"Saved: {output_file}")

    except Exception as e:
        print(f"❌ Error cleaning {index_name}: {e}")

print("\n========== INDEX CLEANING COMPLETE ==========")