import pandas as pd
from pathlib import Path


# ============================================================
# TECHNICAL ANALYSIS FUNCTION
# ============================================================

def analyze_stock(input_file):

    # =========================
    # Load Processed Dataset
    # =========================

    df = pd.read_csv(
        input_file,
        parse_dates=["Date"]
    )


    # =========================
    # 1. SMA - Simple Moving Average
    # =========================

    df["SMA_20"] = df["Close"].rolling(window=20).mean()
    df["SMA_50"] = df["Close"].rolling(window=50).mean()


    # =========================
    # 2. EMA - Exponential Moving Average
    # =========================

    df["EMA_20"] = df["Close"].ewm(
        span=20,
        adjust=False
    ).mean()

    df["EMA_50"] = df["Close"].ewm(
        span=50,
        adjust=False
    ).mean()


    # =========================
    # 3. RSI - Relative Strength Index
    # =========================

    delta = df["Close"].diff()

    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)

    avg_gain = gain.rolling(window=14).mean()
    avg_loss = loss.rolling(window=14).mean()

    rs = avg_gain / avg_loss

    df["RSI_14"] = 100 - (100 / (1 + rs))


    # =========================
    # 4. MACD
    # =========================

    ema_12 = df["Close"].ewm(
        span=12,
        adjust=False
    ).mean()

    ema_26 = df["Close"].ewm(
        span=26,
        adjust=False
    ).mean()

    df["MACD"] = ema_12 - ema_26

    df["MACD_Signal"] = df["MACD"].ewm(
        span=9,
        adjust=False
    ).mean()

    df["MACD_Histogram"] = (
        df["MACD"] - df["MACD_Signal"]
    )


    # =========================
    # 5. Volume Analysis
    # =========================

    df["Volume_SMA_20"] = df["Volume"].rolling(
        window=20
    ).mean()

    df["Volume_Signal"] = (
        df["Volume"] > df["Volume_SMA_20"]
    )


    # =========================
    # 6. Technical Signal Score
    # =========================

    df["Bullish_Score"] = (
        (df["Close"] > df["EMA_20"]).astype(int)
        + (df["EMA_20"] > df["EMA_50"]).astype(int)
        + (df["RSI_14"] > 50).astype(int)
        + (df["MACD"] > df["MACD_Signal"]).astype(int)
        + (df["Volume_Signal"]).astype(int)
    )

    df["Bearish_Score"] = (
        (df["Close"] < df["EMA_20"]).astype(int)
        + (df["EMA_20"] < df["EMA_50"]).astype(int)
        + (df["RSI_14"] < 50).astype(int)
        + (df["MACD"] < df["MACD_Signal"]).astype(int)
        + (df["Volume_Signal"]).astype(int)
    )


    # =========================
    # 7. Final Technical Signal
    # =========================

    df["Technical_Signal"] = "Neutral"

    df.loc[
        df["Bullish_Score"] >= 4,
        "Technical_Signal"
    ] = "Bullish"

    df.loc[
        df["Bearish_Score"] >= 4,
        "Technical_Signal"
    ] = "Bearish"


    # =========================
    # 8. Entry Rule
    # =========================

    df["Entry_Signal"] = (
        (df["Close"] > df["EMA_20"]) &
        (df["EMA_20"] > df["EMA_50"]) &
        (df["RSI_14"] > 50) &
        (df["MACD"] > df["MACD_Signal"]) &
        (df["Volume"] > df["Volume_SMA_20"])
    )


    # =========================
    # 9. Exit Rule
    # =========================

    df["Exit_Signal"] = (
        (df["Close"] < df["EMA_20"]) |
        (df["EMA_20"] < df["EMA_50"]) |
        (df["RSI_14"] < 50) |
        (df["MACD"] < df["MACD_Signal"])
    )


    # =========================
    # 10. Stop Loss
    # =========================

    df["Stop_Loss_Percent"] = 0.05

    df["Stop_Loss_Price"] = (
        df["Close"] * (1 - df["Stop_Loss_Percent"])
    )


    # =========================
    # 11. Target Price
    # =========================

    risk_per_share = (
        df["Close"] - df["Stop_Loss_Price"]
    )

    df["Target_Price"] = (
        df["Close"] + (risk_per_share * 2)
    )


    # =========================
    # 12. Position Sizing
    # =========================

    INITIAL_CAPITAL = 100000
    RISK_PER_TRADE = 0.01

    df["Risk_Amount"] = (
        INITIAL_CAPITAL * RISK_PER_TRADE
    )

    df["Risk_Per_Share"] = (
        df["Close"] - df["Stop_Loss_Price"]
    )

    df["Position_Size"] = (
        df["Risk_Amount"] /
        df["Risk_Per_Share"]
    ).astype(int)


    # =========================
    # 13. Risk : Reward Ratio
    # =========================

    df["Reward_Per_Share"] = (
        df["Target_Price"] - df["Close"]
    )

    df["Risk_Reward_Ratio"] = (
        df["Reward_Per_Share"] /
        df["Risk_Per_Share"]
    )


    return df


# ============================================================
# TEST BOTH STOCKS
# ============================================================

stocks = {
    "RELIANCE": "Dataset/processed/RELIANCE_NS_clean.csv",
    "GACM Technologies": "Dataset/processed/GATECH_NS_clean.csv"
}


for stock_name, file_path in stocks.items():

    if Path(file_path).exists():

        stock_df = analyze_stock(file_path)

        print("\n========================================")
        print(stock_name)
        print("========================================")

        print(
            stock_df[
                [
                    "Date",
                    "Close",
                    "SMA_20",
                    "SMA_50",
                    "EMA_20",
                    "EMA_50",
                    "RSI_14",
                    "MACD",
                    "MACD_Signal",
                    "MACD_Histogram",
                    "Volume",
                    "Volume_SMA_20",
                    "Volume_Signal",
                    "Bullish_Score",
                    "Bearish_Score",
                    "Technical_Signal",
                    "Entry_Signal",
                    "Exit_Signal",
                    "Stop_Loss_Price",
                    "Target_Price",
                    "Risk_Amount",
                    "Risk_Per_Share",
                    "Position_Size",
                    "Reward_Per_Share",
                    "Risk_Reward_Ratio"
                ]
            ].tail(10)
        )

    else:
        print(f"\nFile not found: {file_path}")