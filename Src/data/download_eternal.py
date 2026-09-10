import yfinance as yf
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]

RAW_FOLDER = PROJECT_ROOT / "Dataset" / "raw"
RAW_FOLDER.mkdir(parents=True, exist_ok=True)

TICKER = "ETERNAL.NS"
START_DATE = "2021-07-01"
END_DATE = "2026-09-09"

print(f"Downloading ETERNAL ({TICKER})...")

try:
    df = yf.download(
        TICKER,
        start=START_DATE,
        end=END_DATE,
        auto_adjust=False,
        progress=False
    )

    if df.empty:
        print("❌ No data returned from Yahoo Finance.")
    else:

        if hasattr(df.columns, "levels"):
            df.columns = df.columns.get_level_values(0)

        df = df.reset_index()

        output_file = RAW_FOLDER / "ETERNAL_NS_raw.csv"

        df.to_csv(output_file, index=False)

        print("✅ ETERNAL downloaded successfully!")
        print(f"Rows: {len(df)}")
        print(f"Columns: {len(df.columns)}")
        print(f"Saved: {output_file}")

except Exception as e:
    print(f"❌ Error: {e}")