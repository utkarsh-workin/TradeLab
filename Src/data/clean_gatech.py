import pandas as pd
from pathlib import Path

input_file = Path("Dataset/raw/GATECH_NS_raw.csv")
output_file = Path("Dataset/processed/GATECH_NS_clean.csv")

# Load data
df = pd.read_csv(input_file, header=[0, 1], index_col=0)

# Flatten multi-level columns
df.columns = [
    col[0] if "GATECH.NS" in col[1] else f"{col[0]}_{col[1]}"
    for col in df.columns
]

# Reset index
df.reset_index(inplace=True)

# Rename Date column
df.rename(columns={"Price": "Date"}, inplace=True)

# Convert Date
df["Date"] = pd.to_datetime(df["Date"], errors="coerce")

# Remove invalid dates
df = df.dropna(subset=["Date"])

# Sort by date
df = df.sort_values("Date")

# Remove duplicate dates
df = df.drop_duplicates(subset=["Date"])

# Convert numeric columns
numeric_columns = ["Open", "High", "Low", "Close", "Adj Close", "Volume"]

for col in numeric_columns:
    if col in df.columns:
        df[col] = pd.to_numeric(df[col], errors="coerce")

# Remove rows where essential OHLC data is missing
df = df.dropna(subset=["Open", "High", "Low", "Close"])

# Create output directory
output_file.parent.mkdir(parents=True, exist_ok=True)

# Save cleaned data
df.to_csv(output_file, index=False)

print("GACM Technologies data cleaned successfully!")
print("Rows:", len(df))
print("Columns:", len(df.columns))
print("Saved to:", output_file)