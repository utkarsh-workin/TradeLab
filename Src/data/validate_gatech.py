import pandas as pd
from pathlib import Path

input_file = Path("Dataset/processed/GATECH_NS_clean.csv")

df = pd.read_csv(input_file)

df["Date"] = pd.to_datetime(df["Date"], errors="coerce")

print("========== GACM DATA VALIDATION ==========")

print("\nRows:", len(df))
print("Columns:", len(df.columns))

print("\nMissing Values:")
print(df.isnull().sum())

print("\nDuplicate Dates:", df["Date"].duplicated().sum())

print("\nDate Sorted:", df["Date"].is_monotonic_increasing)

print("\nInvalid High < Low:", (df["High"] < df["Low"]).sum())

print("\nInvalid Close <= 0:", (df["Close"] <= 0).sum())

print("\nInvalid Volume < 0:", (df["Volume"] < 0).sum())

print("\nDate Range:")
print("Start:", df["Date"].min().date())
print("End:", df["Date"].max().date())

print("\n========== VALIDATION COMPLETE ==========")