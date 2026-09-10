import yfinance as yf
from pathlib import Path

ticker = "GATECH.NS"

start = "2015-01-01"
end = "2026-09-09"

data = yf.download(
    ticker,
    start=start,
    end=end,
    auto_adjust=False,
    progress=False
)

output_dir = Path("Dataset/raw")
output_dir.mkdir(parents=True, exist_ok=True)

output_file = output_dir / "GATECH_NS_raw.csv"

data.to_csv(output_file)

print("GACM Technologies data downloaded successfully!")
print("Rows:", len(data))
print("Columns:", len(data.columns))
print("Saved to:", output_file)