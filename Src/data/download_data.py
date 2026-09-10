import yfinance as yf

ticker = "RELIANCE.NS"

data = yf.download(
    ticker,
    start="2020-01-01",
    end="2025-01-01",
    auto_adjust=False
)

print("\n--- SHAPE ---")
print(data.shape)

print("\n--- COLUMNS ---")
print(data.columns)

print("\n--- DATA TYPES ---")
print(data.dtypes)

print("\n--- DATE RANGE ---")
print("Start:", data.index.min())
print("End:", data.index.max())

print("\n--- MISSING VALUES ---")
print(data.isnull().sum())

print("\n--- FIRST 5 ROWS ---")
print(data.head())

print("\n--- LAST 5 ROWS ---")
print(data.tail())