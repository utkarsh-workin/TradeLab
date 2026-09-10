import yfinance as yf
from pathlib import Path

# Project root
PROJECT_ROOT = Path(__file__).resolve().parents[2]

# Raw data folder
RAW_FOLDER = PROJECT_ROOT / "Dataset" / "raw"
RAW_FOLDER.mkdir(parents=True, exist_ok=True)

# Stocks
stocks = {
    "ETERNAL": "ETERNAL.NS",
    "IRFC": "IRFC.NS",
    "RVNL": "RVNL.NS",
    "RAILTEL": "RAILTEL.NS",
    "TORRENTPOWER": "TORNTPOWER.NS",
}

START_DATE = "2015-01-01"
END_DATE = "2026-09-09"

for name, ticker in stocks.items():

    print(f"\nDownloading {name} ({ticker})...")

    try:
        df = yf.download(
            ticker,
            start=START_DATE,
            end=END_DATE,
            auto_adjust=False,
            progress=False
        )

        if df.empty:
            print(f"❌ No data found for {name}")
            continue

        # Handle yfinance MultiIndex columns
        if hasattr(df.columns, "levels"):
            df.columns = df.columns.get_level_values(0)

        df = df.reset_index()

        output_file = RAW_FOLDER / f"{name}_NS_raw.csv"
        df.to_csv(output_file, index=False)

        print(f"✅ {name} downloaded")
        print(f"Rows: {len(df)}")
        print(f"Columns: {len(df.columns)}")
        print(f"Saved: {output_file}")

    except Exception as e:
        print(f"❌ Error downloading {name}: {e}")

print("\n========== DOWNLOAD COMPLETE ==========")