import pandas as pd

input_file = "Dataset/processed/RELIANCE_NS_clean.csv"

df = pd.read_csv(input_file, parse_dates=["Date"])

print("--- FINAL DATASET ---")
print("Rows:", len(df))
print("Columns:", len(df.columns))
print("Date Range:", df["Date"].min(), "to", df["Date"].max())

print("\nColumns:")
print(list(df.columns))

print("\nMissing Values:")
print(df.isnull().sum())

print("\nFirst 5 Rows:")
print(df.head())

print("\nLast 5 Rows:")
print(df.tail())

print("\n✅ P1 DATA PIPELINE COMPLETE")