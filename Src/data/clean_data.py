import pandas as pd

# Load raw data
df = pd.read_csv(
    "Dataset/raw/RELIANCE_NS_raw.csv",
    header=[0, 1],
    index_col=0
)

# Convert Date index
df.index = pd.to_datetime(df.index)
df.index.name = "Date"

# Keep only the required ticker level
df.columns = df.columns.get_level_values(0)

# Convert columns to numeric
for col in df.columns:
    df[col] = pd.to_numeric(df[col], errors="coerce")

# Check missing values
print("\n--- Missing Values Before Cleaning ---")
print(df.isnull().sum())

# Remove rows with missing OHLCV values
df = df.dropna(subset=["Open", "High", "Low", "Close", "Volume"])

# Remove duplicate dates
df = df[~df.index.duplicated(keep="first")]

# Sort by date
df = df.sort_index()

# Save cleaned dataset
df.to_csv("Dataset/processed/RELIANCE_NS_clean.csv")

print("\n--- Cleaning Complete ---")
print("Shape:", df.shape)
print("Columns:", list(df.columns))
print("\n--- Missing Values After Cleaning ---")
print(df.isnull().sum())
print("\nCleaned data saved successfully.")