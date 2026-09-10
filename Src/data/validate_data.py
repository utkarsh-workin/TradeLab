import pandas as pd

# Load cleaned data
df = pd.read_csv(
    "Dataset/processed/RELIANCE_NS_clean.csv",
    parse_dates=["Date"]
)

print("--- DATA VALIDATION ---")

# 1. Duplicate dates
duplicate_dates = df["Date"].duplicated().sum()
print("\n1. Duplicate dates:", duplicate_dates)

# 2. Missing values
missing_values = df.isnull().sum().sum()
print("2. Total missing values:", missing_values)

# 3. OHLC consistency
invalid_ohlc = (
    (df["High"] < df["Open"]) |
    (df["High"] < df["Close"]) |
    (df["Low"] > df["Open"]) |
    (df["Low"] > df["Close"])
).sum()

print("3. Invalid OHLC rows:", invalid_ohlc)

# 4. Invalid prices
invalid_prices = (
    (df["Open"] <= 0) |
    (df["High"] <= 0) |
    (df["Low"] <= 0) |
    (df["Close"] <= 0)
).sum()

print("4. Invalid price rows:", invalid_prices)

# 5. Invalid volume
invalid_volume = (df["Volume"] < 0).sum()

print("5. Invalid volume rows:", invalid_volume)

# Date range
print("\n--- DATE RANGE ---")
print("Start:", df["Date"].min())
print("End:", df["Date"].max())

# Final validation
if (
    duplicate_dates == 0
    and missing_values == 0
    and invalid_ohlc == 0
    and invalid_prices == 0
    and invalid_volume == 0
):
    print("\n✅ DATA VALIDATION PASSED")
else:
    print("\n⚠️ DATA VALIDATION FOUND ISSUES")