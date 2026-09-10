# =========================================================
# TRADELAB
# Indian Stock Market Analysis & Backtesting Platform
# =========================================================


# =========================================================
# 1. IMPORTS
# =========================================================

import os
import sys
import sqlite3
import subprocess
from pathlib import Path

import pandas as pd
import streamlit as st
import plotly.graph_objects as go


# =========================================================
# 2. PROJECT PATHS
# =========================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

PROCESSED_FOLDER = PROJECT_ROOT / "Dataset" / "processed"

BACKTEST_SCRIPT = (
    PROJECT_ROOT
    / "Src"
    / "data"
    / "backtesting_test.py"
)

DB_FILE = (
    PROJECT_ROOT
    / "result"
    / "tradelab.db"
)

# Equity curve file is selected dynamically from the current asset.


# =========================================================
# 3. ASSET CONFIGURATION
# =========================================================

ASSETS = {
    # -------------------------
    # ⭐ Stocks
    # -------------------------

    "RELIANCE": {
        "type": "stock",
        "file": PROCESSED_FOLDER / "RELIANCE_NS_clean.csv",
    },

    "GACM Technologies": {
        "type": "stock",
        "file": PROCESSED_FOLDER / "GATECH_NS_clean.csv",
    },

    "ETERNAL": {
        "type": "stock",
        "file": PROCESSED_FOLDER / "ETERNAL_NS_clean.csv",
    },

    "IRFC": {
        "type": "stock",
        "file": PROCESSED_FOLDER / "IRFC_NS_clean.csv",
    },

    "RVNL": {
        "type": "stock",
        "file": PROCESSED_FOLDER / "RVNL_NS_clean.csv",
    },

    "RailTel": {
        "type": "stock",
        "file": PROCESSED_FOLDER / "RAILTEL_NS_clean.csv",
    },

    "Torrent Power": {
        "type": "stock",
        "file": PROCESSED_FOLDER / "TORRENTPOWER_NS_clean.csv",
    },


    # -------------------------
    # 📈 Indices
    # -------------------------

    "NIFTY 50": {
        "type": "index",
        "file": PROCESSED_FOLDER / "NIFTY50_clean.csv",
    },

    "BANK NIFTY": {
        "type": "index",
        "file": PROCESSED_FOLDER / "BANKNIFTY_clean.csv",
    },

    "SENSEX": {
        "type": "index",
        "file": PROCESSED_FOLDER / "SENSEX_clean.csv",
    },
}


# =========================================================
# 4. PAGE CONFIGURATION
# =========================================================

st.set_page_config(
    page_title="TradeLab",
    page_icon="📈",
    layout="wide"
)


# =========================================================
# 5. TITLE
# =========================================================

st.title(
    "Indian Stock Market Analysis & Backtesting Platform"
)

st.write(
    "Interactive platform for technical analysis, "
    "strategy testing, and backtesting."
)


# =========================================================
# 6. DATA LOADING FUNCTION
# =========================================================

@st.cache_data
def load_selected_data(data_file):

    df = pd.read_csv(data_file)

    df["Date"] = pd.to_datetime(
        df["Date"],
        errors="coerce"
    )

    df = df.dropna(subset=["Date"])

    df = df.sort_values(
        "Date"
    ).reset_index(drop=True)

    return df


# =========================================================
# 7. SIDEBAR — ASSET SELECTION
# =========================================================

st.sidebar.header(
    "📊 Asset Selection"
)

asset = st.sidebar.selectbox(
    "Select Asset",
    list(ASSETS.keys())
)

asset_type = ASSETS[asset]["type"]

DATA_FILE = ASSETS[asset]["file"]


# =========================================================
# 8. LOAD SELECTED ASSET DATA
# =========================================================

try:

    if not DATA_FILE.exists():

        st.error(
            f"Data file not found for {asset}: "
            f"{DATA_FILE}"
        )

        st.stop()

    df = load_selected_data(DATA_FILE)

    st.success(
        f"{asset} data loaded successfully!"
    )

except Exception as e:

    st.error(
        f"Data loading failed: {e}"
    )

    st.stop()


# =========================================================
# 9. DATASET INFORMATION
# =========================================================

st.subheader(
    "📊 Dataset Information"
)

col1, col2, col3, col4 = st.columns(4)


with col1:

    st.metric(
        "Asset",
        asset
    )


with col2:

    st.metric(
        "Type",
        asset_type.upper()
    )


with col3:

    st.metric(
        "Rows",
        f"{len(df):,}"
    )


with col4:

    st.metric(
        "Columns",
        f"{len(df.columns):,}"
    )


# =========================================================
# 10. SIDEBAR — TECHNICAL INDICATORS
# =========================================================

st.sidebar.header(
    "Technical Indicators"
)

show_sma20 = st.sidebar.checkbox(
    "SMA 20",
    value=True
)

show_sma50 = st.sidebar.checkbox(
    "SMA 50",
    value=True
)

show_ema20 = st.sidebar.checkbox(
    "EMA 20",
    value=True
)

show_ema50 = st.sidebar.checkbox(
    "EMA 50",
    value=True
)


# =========================================================
# 11. TECHNICAL INDICATORS
# =========================================================


# -------------------------
# SMA
# -------------------------

df["SMA_20"] = (
    df["Close"]
    .rolling(20)
    .mean()
)

df["SMA_50"] = (
    df["Close"]
    .rolling(50)
    .mean()
)


# -------------------------
# EMA
# -------------------------

df["EMA_20"] = (
    df["Close"]
    .ewm(
        span=20,
        adjust=False
    )
    .mean()
)

df["EMA_50"] = (
    df["Close"]
    .ewm(
        span=50,
        adjust=False
    )
    .mean()
)


# -------------------------
# RSI
# -------------------------

delta = df["Close"].diff()

gain = delta.clip(
    lower=0
)

loss = -delta.clip(
    upper=0
)

avg_gain = (
    gain
    .rolling(14)
    .mean()
)

avg_loss = (
    loss
    .rolling(14)
    .mean()
)

rs = avg_gain / avg_loss

df["RSI_14"] = (
    100
    - (
        100 / (1 + rs)
    )
)


# -------------------------
# MACD
# -------------------------

ema12 = (
    df["Close"]
    .ewm(
        span=12,
        adjust=False
    )
    .mean()
)

ema26 = (
    df["Close"]
    .ewm(
        span=26,
        adjust=False
    )
    .mean()
)

df["MACD"] = (
    ema12 - ema26
)

df["MACD_Signal"] = (
    df["MACD"]
    .ewm(
        span=9,
        adjust=False
    )
    .mean()
)


# -------------------------
# Volume
# -------------------------

if "Volume" in df.columns:

    df["Volume_SMA_20"] = (
        df["Volume"]
        .rolling(20)
        .mean()
    )

else:

    df["Volume"] = 0

    df["Volume_SMA_20"] = 0


# =========================================================
# 12. TRADING SIGNALS
# =========================================================

# For indices, volume condition is ignored
# because index volume is not equivalent to stock volume.

if asset_type == "stock":

    df["BUY"] = (
        (df["Close"] > df["EMA_20"])
        &
        (df["EMA_20"] > df["EMA_50"])
        &
        (df["RSI_14"] > 50)
        &
        (df["MACD"] > df["MACD_Signal"])
        &
        (df["Volume"] > df["Volume_SMA_20"])
    )

else:

    df["BUY"] = (
        (df["Close"] > df["EMA_20"])
        &
        (df["EMA_20"] > df["EMA_50"])
        &
        (df["RSI_14"] > 50)
        &
        (df["MACD"] > df["MACD_Signal"])
    )


df["SELL"] = (
    (df["Close"] < df["EMA_20"])
    |
    (df["EMA_20"] < df["EMA_50"])
    |
    (df["RSI_14"] < 50)
    |
    (df["MACD"] < df["MACD_Signal"])
)


df["Signal"] = "HOLD"


df.loc[
    df["BUY"],
    "Signal"
] = "BUY"


df.loc[
    (~df["BUY"]) & df["SELL"],
    "Signal"
] = "SELL"


# =========================================================
# 13. SIDEBAR — TRADING SIGNALS
# =========================================================

st.sidebar.header(
    "Trading Signals"
)

show_signals = st.sidebar.checkbox(
    "Show Buy/Sell Signals",
    value=True
)


# =========================================================
# 14. SIDEBAR — STRATEGY
# =========================================================

st.sidebar.header(
    "Strategy"
)

strategy = st.sidebar.selectbox(
    "Select Strategy",
    [
        "EMA + RSI + MACD + Volume Strategy"
    ]
)


if asset_type == "stock":

    st.sidebar.info(
        """
Strategy Rules:

BUY:
• Close > EMA 20
• EMA 20 > EMA 50
• RSI > 50
• MACD > Signal
• Volume > 20-day average

EXIT:
• Close < EMA 20
OR
• EMA 20 < EMA 50
OR
• RSI < 50
OR
• MACD < Signal
"""
    )

else:

    st.sidebar.info(
        """
Index Analysis Rules:

BUY:
• Close > EMA 20
• EMA 20 > EMA 50
• RSI > 50
• MACD > Signal

EXIT:
• Close < EMA 20
OR
• EMA 20 < EMA 50
OR
• RSI < 50
OR
• MACD < Signal

Note:
Index volume is not used.
"""
    )


# =========================================================
# 15. PRICE CHART
# =========================================================

st.subheader(
    f"📈 {asset} Price Chart"
)

fig = go.Figure()


# -------------------------
# Candlestick
# -------------------------

fig.add_trace(
    go.Candlestick(
        x=df["Date"],
        open=df["Open"],
        high=df["High"],
        low=df["Low"],
        close=df["Close"],
        name=asset
    )
)


# -------------------------
# SMA 20
# -------------------------

if show_sma20:

    fig.add_trace(
        go.Scatter(
            x=df["Date"],
            y=df["SMA_20"],
            mode="lines",
            name="SMA 20"
        )
    )


# -------------------------
# SMA 50
# -------------------------

if show_sma50:

    fig.add_trace(
        go.Scatter(
            x=df["Date"],
            y=df["SMA_50"],
            mode="lines",
            name="SMA 50"
        )
    )


# -------------------------
# EMA 20
# -------------------------

if show_ema20:

    fig.add_trace(
        go.Scatter(
            x=df["Date"],
            y=df["EMA_20"],
            mode="lines",
            name="EMA 20"
        )
    )


# -------------------------
# EMA 50
# -------------------------

if show_ema50:

    fig.add_trace(
        go.Scatter(
            x=df["Date"],
            y=df["EMA_50"],
            mode="lines",
            name="EMA 50"
        )
    )


# =========================================================
# 16. BUY / SELL MARKERS
# =========================================================

if show_signals:

    buy_df = df[
        df["BUY"]
    ]

    sell_df = df[
        (~df["BUY"]) & df["SELL"]
    ]


    # ---------------------
    # BUY
    # ---------------------

    fig.add_trace(
        go.Scatter(
            x=buy_df["Date"],
            y=buy_df["Low"] * 0.98,
            mode="markers",
            name="BUY",
            marker=dict(
                symbol="triangle-up",
                size=10
            )
        )
    )


    # ---------------------
    # SELL
    # ---------------------

    fig.add_trace(
        go.Scatter(
            x=sell_df["Date"],
            y=sell_df["High"] * 1.02,
            mode="markers",
            name="SELL",
            marker=dict(
                symbol="triangle-down",
                size=10
            )
        )
    )


# =========================================================
# 17. CHART LAYOUT
# =========================================================

fig.update_layout(
    height=650,
    xaxis_title="Date",
    yaxis_title="Price",
    xaxis_rangeslider_visible=False,
    hovermode="x unified"
)


st.plotly_chart(
    fig,
    width="stretch"
)


# =========================================================
# 18. CURRENT TRADING SIGNAL
# =========================================================

st.subheader(
    "🎯 Current Trading Signal"
)

latest_signal = df.iloc[-1]["Signal"]


signal_col1, signal_col2, signal_col3 = (
    st.columns(3)
)


with signal_col1:

    st.metric(
        "Current Signal",
        latest_signal
    )


with signal_col2:

    st.metric(
        "Latest Close",
        f"₹{df.iloc[-1]['Close']:.2f}"
    )


with signal_col3:

    st.metric(
        "RSI",
        f"{df.iloc[-1]['RSI_14']:.2f}"
    )


# =========================================================
# 19. SIGNAL SUMMARY
# =========================================================

st.subheader(
    "📌 Signal Summary"
)

sig1, sig2, sig3 = (
    st.columns(3)
)


with sig1:

    st.metric(
        "BUY Signals",
        int(
            (df["Signal"] == "BUY")
            .sum()
        )
    )


with sig2:

    st.metric(
        "SELL Signals",
        int(
            (df["Signal"] == "SELL")
            .sum()
        )
    )


with sig3:

    st.metric(
        "HOLD Signals",
        int(
            (df["Signal"] == "HOLD")
            .sum()
        )
    )


# =========================================================
# 20. BACKTESTING
# =========================================================

st.subheader(
    "🧪 Backtesting"
)

if asset_type == "index":

    st.info(
        "Backtesting for indices will be enabled "
        "after the dynamic backtesting engine is updated."
    )

else:

    st.write(
        "Run the selected strategy on the historical dataset."
    )


    if st.button(
        "▶️ Run Backtest",
        width="stretch"
    ):

        env = os.environ.copy()

        env["PYTHONIOENCODING"] = "utf-8"


        try:

            result = subprocess.run(

                [
                    sys.executable,
                    str(BACKTEST_SCRIPT),
                    asset
                ],

                cwd=PROJECT_ROOT,

                capture_output=True,

                text=True,

                encoding="utf-8",

                errors="replace",

                env=env
            )


            # =================================================
            # BACKTEST SUCCESS
            # =================================================

            if result.returncode == 0:

                st.success(
                    f"{asset} backtest completed successfully!"
                )

                output = result.stdout


                with st.expander(
                    "View Raw Backtest Output"
                ):

                    st.text(
                        output
                    )


                # =============================================
                # INITIALIZE METRICS
                # =============================================

                return_value = None
                buy_hold_return = None
                win_rate = None
                sharpe = None
                max_drawdown = None
                profit_factor = None
                total_trades = None


                # =============================================
                # PARSE BACKTEST OUTPUT
                # =============================================

                for line in output.splitlines():

                    line = line.strip()


                    if (
                        line.startswith("Return")
                        and "%" in line
                    ):

                        try:

                            return_value = float(
                                line
                                .split()[-1]
                                .replace("%", "")
                            )

                        except ValueError:

                            pass


                    if line.startswith(
                        "Buy & Hold Return"
                    ):

                        try:

                            buy_hold_return = float(
                                line
                                .split()[-1]
                                .replace("%", "")
                            )

                        except ValueError:

                            pass


                    if line.startswith(
                        "Win Rate"
                    ):

                        try:

                            win_rate = float(
                                line
                                .split()[-1]
                                .replace("%", "")
                            )

                        except ValueError:

                            pass


                    if line.startswith(
                        "Sharpe Ratio"
                    ):

                        try:

                            sharpe = float(
                                line.split()[-1]
                            )

                        except ValueError:

                            pass


                    if line.startswith(
                        "Max. Drawdown"
                    ):

                        try:

                            max_drawdown = float(
                                line
                                .split()[-1]
                                .replace("%", "")
                            )

                        except ValueError:

                            pass


                    if line.startswith(
                        "Profit Factor"
                    ):

                        try:

                            profit_factor = float(
                                line.split()[-1]
                            )

                        except ValueError:

                            pass


                    if line.startswith(
                        "# Trades"
                    ):

                        try:

                            total_trades = int(
                                float(
                                    line.split()[-1]
                                )
                            )

                        except ValueError:

                            pass


                # =================================================
                # BACKTEST PERFORMANCE
                # =================================================

                st.subheader(
                    "📊 Backtest Performance"
                )


                m1, m2, m3 = (
                    st.columns(3)
                )

                m4, m5, m6 = (
                    st.columns(3)
                )


                with m1:

                    st.metric(
                        "Return",
                        f"{return_value:.2f}%"
                        if return_value is not None
                        else "N/A"
                    )


                with m2:

                    st.metric(
                        "Win Rate",
                        f"{win_rate:.2f}%"
                        if win_rate is not None
                        else "N/A"
                    )


                with m3:

                    st.metric(
                        "Sharpe Ratio",
                        f"{sharpe:.2f}"
                        if sharpe is not None
                        else "N/A"
                    )


                with m4:

                    st.metric(
                        "Max Drawdown",
                        f"{max_drawdown:.2f}%"
                        if max_drawdown is not None
                        else "N/A"
                    )


                with m5:

                    st.metric(
                        "Profit Factor",
                        f"{profit_factor:.2f}"
                        if profit_factor is not None
                        else "N/A"
                    )


                with m6:

                    st.metric(
                        "Total Trades",
                        total_trades
                        if total_trades is not None
                        else "N/A"
                    )


                # =================================================
                # STRATEGY VS BUY & HOLD
                # =================================================

                st.subheader(
                    "📊 Strategy vs Buy & Hold"
                )

                compare1, compare2 = (
                    st.columns(2)
                )


                with compare1:

                    st.metric(
                        "TradeLab Strategy",
                        f"{return_value:.2f}%"
                        if return_value is not None
                        else "N/A"
                    )


                with compare2:

                    st.metric(
                        "Buy & Hold",
                        f"{buy_hold_return:.2f}%"
                        if buy_hold_return is not None
                        else "N/A"
                    )


            # =================================================
            # BACKTEST FAILURE
            # =================================================

            else:

                st.error(
                    "Backtest failed."
                )

                if result.stderr:

                    st.code(
                        result.stderr,
                        language="text"
                    )


                if result.stdout:

                    with st.expander(
                        "View Backtest Output"
                    ):

                        st.text(
                            result.stdout
                        )


        except Exception as e:

            st.error(
                f"Error while running backtest: {e}"
            )


# =========================================================
# 21. TRADE HISTORY
# =========================================================

st.subheader(
    "📋 Trade History"
)

if asset_type == "index":

    st.info(
        "Trade history will be available for indices "
        "after dynamic index backtesting is implemented."
    )

elif DB_FILE.exists():

    try:

        conn = sqlite3.connect(DB_FILE)

        # Load only trades belonging to the selected asset.
        trades_df = pd.read_sql_query(
            "SELECT * FROM trades WHERE Asset = ?",
            conn,
            params=(asset,)
        )

        conn.close()

        if not trades_df.empty:

            preferred_columns = [
                "Asset",
                "EntryTime",
                "ExitTime",
                "EntryPrice",
                "ExitPrice",
                "Size",
                "PnL",
                "ReturnPct",
                "EntryBar",
                "ExitBar"
            ]

            available_columns = [
                column
                for column in preferred_columns
                if column in trades_df.columns
            ]

            display_df = (
                trades_df[available_columns].copy()
                if available_columns
                else trades_df.copy()
            )

            st.write(
                f"Total Trades for **{asset}**: **{len(display_df)}**"
            )

            st.dataframe(
                display_df,
                width="stretch",
                hide_index=True
            )

        else:

            st.info(
                f"No trades found for {asset}. Run the backtest first."
            )

    except Exception as e:

        st.error(
            f"Unable to load trade history for {asset}: {e}"
        )

else:

    st.info(
        "Trade database not found. Run the backtest first."
    )


# =========================================================
# 22. EQUITY CURVE
# =========================================================

st.subheader(
    "📈 Equity Curve"
)

if asset_type == "index":

    st.info(
        "Equity curve will be available for indices "
        "after dynamic index backtesting is implemented."
    )

else:

    # Asset-specific equity curve file.
    EQUITY_FILE = (
        PROJECT_ROOT
        / "result"
        / f"{asset}_equity_curve.csv"
    )

    if EQUITY_FILE.exists():

        try:

            equity_df = pd.read_csv(EQUITY_FILE)

            if "Date" in equity_df.columns:
                date_column = "Date"
            elif "index" in equity_df.columns:
                date_column = "index"
            else:
                date_column = equity_df.columns[0]

            equity_df[date_column] = pd.to_datetime(
                equity_df[date_column],
                errors="coerce"
            )

            equity_df = equity_df.dropna(
                subset=[date_column]
            )

            equity_column = None

            for column in equity_df.columns:
                if column.lower() == "equity":
                    equity_column = column
                    break

            if equity_column is None:
                for column in equity_df.columns:
                    if "equity" in column.lower():
                        equity_column = column
                        break

            if equity_column is not None:

                fig_equity = go.Figure()

                fig_equity.add_trace(
                    go.Scatter(
                        x=equity_df[date_column],
                        y=equity_df[equity_column],
                        mode="lines",
                        name=f"{asset} Portfolio Equity"
                    )
                )

                fig_equity.update_layout(
                    height=500,
                    title=f"{asset} — Equity Curve",
                    xaxis_title="Date",
                    yaxis_title="Portfolio Value",
                    hovermode="x unified"
                )

                st.plotly_chart(
                    fig_equity,
                    width="stretch"
                )

            else:

                st.warning(
                    f"Equity column not found in {asset}_equity_curve.csv"
                )

        except Exception as e:

            st.error(
                f"Unable to load {asset} equity curve: {e}"
            )

    else:

        st.info(
            f"No equity curve found for {asset}. Run the backtest first."
        )


# =========================================================
# 23. HISTORICAL WHAT-IF CALCULATOR
# =========================================================

st.divider()

st.subheader(
    "📊 Historical What-If"
)

st.write(
    "Check what your investment could have returned "
    "between two historical dates."
)


# ---------------------------------------------------------
# 23.1 INPUTS
# ---------------------------------------------------------

whatif_col1, whatif_col2 = st.columns(2)


with whatif_col1:

    investment_amount = st.number_input(
        "Investment Amount (₹)",
        min_value=1.0,
        value=50000.0,
        step=1000.0
    )

    buy_date = st.date_input(
        "Buy Date",
        value=df["Date"].min().date(),
        min_value=df["Date"].min().date(),
        max_value=df["Date"].max().date()
    )


with whatif_col2:

    sell_date = st.date_input(
        "Sell Date",
        value=df["Date"].max().date(),
        min_value=df["Date"].min().date(),
        max_value=df["Date"].max().date()
    )


# ---------------------------------------------------------
# 23.2 CALCULATE BUTTON
# ---------------------------------------------------------

if st.button(
    "🧮 Calculate Historical Return",
    width="stretch"
):

    buy_date = pd.Timestamp(
        buy_date
    )

    sell_date = pd.Timestamp(
        sell_date
    )


    # -----------------------------------------------------
    # Validate dates
    # -----------------------------------------------------

    if buy_date >= sell_date:

        st.error(
            "Sell Date must be after Buy Date."
        )

    else:

        # -------------------------------------------------
        # Find nearest available trading dates
        # -------------------------------------------------

        buy_data = df[
            df["Date"] >= buy_date
        ]

        sell_data = df[
            df["Date"] <= sell_date
        ]


        if buy_data.empty or sell_data.empty:

            st.error(
                "No trading data available for "
                "the selected dates."
            )

        else:

            buy_row = buy_data.iloc[0]

            sell_row = sell_data.iloc[-1]


            actual_buy_date = buy_row["Date"]

            actual_sell_date = sell_row["Date"]


            buy_price = float(
                buy_row["Close"]
            )

            sell_price = float(
                sell_row["Close"]
            )


            # -------------------------------------------------
            # Investment calculation
            # -------------------------------------------------

            quantity = (
                investment_amount /
                buy_price
            )

            final_value = (
                quantity *
                sell_price
            )

            profit_loss = (
                final_value -
                investment_amount
            )

            return_percent = (
                profit_loss /
                investment_amount
            ) * 100

            holding_days = (
                actual_sell_date -
                actual_buy_date
            ).days


            # -------------------------------------------------
            # Results
            # -------------------------------------------------

            st.success(
                "Historical calculation completed!"
            )


            st.caption(
                f"Actual trading dates used: "
                f"{actual_buy_date.strftime('%d %b %Y')} → "
                f"{actual_sell_date.strftime('%d %b %Y')}"
            )


            result1, result2, result3 = st.columns(3)

            result4, result5, result6 = st.columns(3)


            with result1:

                st.metric(
                    "Buy Price",
                    f"₹{buy_price:,.2f}"
                )


            with result2:

                st.metric(
                    "Sell Price",
                    f"₹{sell_price:,.2f}"
                )


            with result3:

                st.metric(
                    "Quantity",
                    f"{quantity:.2f}"
                )


            with result4:

                st.metric(
                    "Final Value",
                    f"₹{final_value:,.2f}"
                )


            with result5:

                st.metric(
                    "Profit / Loss",
                    f"₹{profit_loss:,.2f}"
                )


            with result6:

                st.metric(
                    "Return",
                    f"{return_percent:.2f}%"
                )


            st.info(
                f"⏱️ Holding Period: "
                f"{holding_days} days"
            )


            # -------------------------------------------------
            # Selected period chart
            # -------------------------------------------------

            st.subheader(
                "📈 Historical Price Movement"
            )


            chart_df = df[
                (df["Date"] >= actual_buy_date)
                &
                (df["Date"] <= actual_sell_date)
            ].copy()


            fig_whatif = go.Figure()


            # Price line
            fig_whatif.add_trace(
                go.Scatter(
                    x=chart_df["Date"],
                    y=chart_df["Close"],
                    mode="lines",
                    name=asset
                )
            )


            # Buy marker
            fig_whatif.add_trace(
                go.Scatter(
                    x=[actual_buy_date],
                    y=[buy_price],
                    mode="markers",
                    name="BUY",
                    marker=dict(
                        symbol="triangle-up",
                        size=14
                    )
                )
            )


            # Sell marker
            fig_whatif.add_trace(
                go.Scatter(
                    x=[actual_sell_date],
                    y=[sell_price],
                    mode="markers",
                    name="SELL",
                    marker=dict(
                        symbol="triangle-down",
                        size=14
                    )
                )
            )


            fig_whatif.update_layout(
                height=500,
                xaxis_title="Date",
                yaxis_title="Price",
                hovermode="x unified"
            )


            st.plotly_chart(
                fig_whatif,
                width="stretch"
            )


# =========================================================
# 24. FOOTER
# =========================================================

st.divider()

st.caption(
    "TradeLab — Indian Stock Market Analysis & Backtesting Platform"
)