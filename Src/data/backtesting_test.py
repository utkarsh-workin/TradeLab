from backtesting import Backtest, Strategy
import pandas as pd
import numpy as np
import sqlite3
import sys
from pathlib import Path


# =========================================================
# 1. PROJECT PATHS
# =========================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

PROCESSED_FOLDER = PROJECT_ROOT / "Dataset" / "processed"
RESULT_FOLDER = PROJECT_ROOT / "result"

RESULT_FOLDER.mkdir(parents=True, exist_ok=True)


# =========================================================
# 2. SELECT STOCK
# =========================================================

# Default stock
asset = "RELIANCE"

# Allow stock name from command line
if len(sys.argv) > 1:
    asset = sys.argv[1]

ASSET_FILES = {
    "RELIANCE": "RELIANCE_NS_clean.csv",
    "GACM Technologies": "GATECH_NS_clean.csv",
    "ETERNAL": "ETERNAL_NS_clean.csv",
    "IRFC": "IRFC_NS_clean.csv",
    "RVNL": "RVNL_NS_clean.csv",
    "RailTel": "RAILTEL_NS_clean.csv",
    "Torrent Power": "TORRENTPOWER_NS_clean.csv",
    "NIFTY 50": "NIFTY50_clean.csv",
    "BANK NIFTY": "BANKNIFTY_clean.csv",
    "SENSEX": "SENSEX_clean.csv",
}

INDEX_ASSETS = {"NIFTY 50", "BANK NIFTY", "SENSEX"}

# =========================================================
# 2.1 RISK MANAGEMENT SETTINGS
# =========================================================

INITIAL_CAPITAL = 100000
RISK_PER_TRADE = 0.01       # 1% of current equity
STOP_LOSS_PCT = 0.05        # 5% stop loss
REWARD_RISK_RATIO = 2       # 1:2 risk/reward


if asset not in ASSET_FILES:

    print(
        f"ERROR: Unknown asset '{asset}'"
    )

    print(
        "Available assets:"
    )

    for name in ASSET_FILES:
        print(f"- {name}")

    sys.exit(1)


DATA_FILE = (
    PROCESSED_FOLDER /
    ASSET_FILES[asset]
)


print("\n========================================")
print("TRADELAB DYNAMIC BACKTEST")
print("========================================")
print(f"Selected Asset: {asset}")
print(f"Data File: {DATA_FILE}")


# =========================================================
# 3. LOAD DATA
# =========================================================

df = pd.read_csv(
    DATA_FILE,
    parse_dates=["Date"]
)

df = df.set_index("Date")

required_columns = ["Open", "High", "Low", "Close"]

if "Volume" not in df.columns:
    df["Volume"] = 0

df = df[required_columns + ["Volume"]].copy()
df["Volume"] = pd.to_numeric(df["Volume"], errors="coerce").fillna(0)


print(f"Rows Loaded: {len(df)}")

IS_INDEX = asset in INDEX_ASSETS
print(f"Asset Type: {'Index' if IS_INDEX else 'Stock'}")


# =========================================================
# 4. STRATEGY
# =========================================================

class TradeLabStrategy(Strategy):

    def init(self):

        # -------------------------
        # EMA 20
        # -------------------------
        self.ema20 = self.I(
            lambda x: pd.Series(x).ewm(
                span=20,
                adjust=False
            ).mean(),
            self.data.Close
        )

        # -------------------------
        # EMA 50
        # -------------------------
        self.ema50 = self.I(
            lambda x: pd.Series(x).ewm(
                span=50,
                adjust=False
            ).mean(),
            self.data.Close
        )

        # -------------------------
        # RSI 14
        # -------------------------
        def calculate_rsi(close):

            delta = pd.Series(close).diff()

            gain = delta.clip(lower=0)
            loss = -delta.clip(upper=0)

            avg_gain = gain.rolling(14).mean()
            avg_loss = loss.rolling(14).mean()

            rs = avg_gain / avg_loss

            return 100 - (100 / (1 + rs))

        self.rsi = self.I(
            calculate_rsi,
            self.data.Close
        )

        # -------------------------
        # MACD
        # -------------------------
        def calculate_macd(close):

            series = pd.Series(close)

            ema12 = series.ewm(
                span=12,
                adjust=False
            ).mean()

            ema26 = series.ewm(
                span=26,
                adjust=False
            ).mean()

            return ema12 - ema26

        self.macd = self.I(
            calculate_macd,
            self.data.Close
        )

        # -------------------------
        # MACD Signal
        # -------------------------
        self.macd_signal = self.I(
            lambda x: pd.Series(x).ewm(
                span=9,
                adjust=False
            ).mean(),
            self.macd
        )

        # -------------------------
        # Volume SMA 20
        # -------------------------
        self.volume_sma20 = self.I(
            lambda x: pd.Series(x).rolling(20).mean(),
            self.data.Volume
        )

        # Track whether the strategy has already
        # submitted a position on the current signal.
        self.pending_entry = False

    # =====================================================
    # NEXT
    # =====================================================

    def next(self):

        # =================================================
        # 1. EXIT RULES
        # =================================================

        if self.position:

            exit_condition = (
                self.data.Close[-1] < self.ema20[-1]
                or self.ema20[-1] < self.ema50[-1]
                or self.rsi[-1] < 50
                or self.macd[-1] < self.macd_signal[-1]
            )

            if exit_condition:
                self.position.close()
                return

        # =================================================
        # 2. ENTRY CONDITION
        # =================================================

        volume_condition = (
            True
            if IS_INDEX
            else (
                self.data.Volume[-1]
                > self.volume_sma20[-1]
            )
        )

        entry_condition = (
            self.data.Close[-1] > self.ema20[-1]
            and self.ema20[-1] > self.ema50[-1]
            and self.rsi[-1] > 50
            and self.macd[-1] > self.macd_signal[-1]
            and volume_condition
        )

        if (
            entry_condition
            and not self.position
            and not self.pending_entry
        ):

            # Estimate risk from the signal price only to
            # determine the number of units. SL/TP are later
            # re-anchored to the actual filled entry price.
            signal_price = float(self.data.Close[-1])

            estimated_stop = (
                signal_price
                * (1 - STOP_LOSS_PCT)
            )

            estimated_risk_per_unit = (
                signal_price - estimated_stop
            )

            risk_amount = (
                float(self.equity)
                * RISK_PER_TRADE
            )

            position_size = int(
                np.floor(
                    risk_amount
                    / estimated_risk_per_unit
                )
            )

            position_size = max(1, position_size)

            self.buy(size=position_size)

            self.pending_entry = True

        # =================================================
        # 3. ATTACH SL/TP AFTER ACTUAL ENTRY
        # =================================================

        if self.position:

            # Backtesting.py stores the actual fill price
            # on the active Trade object, not Position.
            if self.trades:
                active_trade = self.trades[-1]

                actual_entry_price = float(
                    active_trade.entry_price
                )

                actual_stop_loss = (
                    actual_entry_price
                    * (1 - STOP_LOSS_PCT)
                )

                risk_per_unit = (
                    actual_entry_price
                    - actual_stop_loss
                )

                actual_target = (
                    actual_entry_price
                    + (
                        risk_per_unit
                        * REWARD_RISK_RATIO
                    )
                )

                # Set SL/TP from the actual filled price.
                active_trade.sl = actual_stop_loss
                active_trade.tp = actual_target

                self.pending_entry = False

# =========================================================
# 5. BACKTEST FUNCTION
# =========================================================

def run_backtest(
    commission=0.001
):

    bt = Backtest(
        df,
        TradeLabStrategy,
        cash=INITIAL_CAPITAL,
        commission=commission
    )

    return bt.run()


# =========================================================
# 6. MAIN BACKTEST
# =========================================================

print("\n--- RISK MANAGEMENT SETTINGS ---")
print(f"Initial Capital: {INITIAL_CAPITAL:.2f}")
print(f"Risk Per Trade: {RISK_PER_TRADE * 100:.1f}%")
print(f"Stop Loss: {STOP_LOSS_PCT * 100:.1f}%")
print(f"Reward : Risk: 1 : {REWARD_RISK_RATIO}")

stats = run_backtest(
    commission=0.001
)


# =========================================================
# 7. BACKTEST RESULTS
# =========================================================

print(
    "\n--- TRADELAB BACKTEST RESULTS ---"
)

print(stats)


# =========================================================
# 8. EQUITY CURVE
# =========================================================

equity_curve = (
    stats["_equity_curve"]
    .copy()
    .reset_index()
)


equity_file = (
    RESULT_FOLDER /
    f"{asset.replace(' ', '_')}_equity_curve.csv"
)


equity_curve.to_csv(
    equity_file,
    index=False
)


# Also maintain common dashboard file
common_equity_file = (
    RESULT_FOLDER /
    "equity_curve.csv"
)


equity_curve.to_csv(
    common_equity_file,
    index=False
)


print(
    f"\nEquity curve saved: {equity_file}"
)


# =========================================================
# 9. TRADE DETAILS
# =========================================================

trades = stats["_trades"]


print(
    "\n--- TRADE DETAILS ---"
)


if not trades.empty:

    print(
        trades[
            [
                "EntryTime",
                "ExitTime",
                "EntryPrice",
                "ExitPrice",
                "Size",
                "PnL",
                "ReturnPct"
            ]
        ].to_string(
            index=False
        )
    )

else:

    print(
        "No trades generated."
    )


# =========================================================
# 10. P&L ANALYSIS
# =========================================================

total_pnl = (
    trades["PnL"].sum()
    if not trades.empty
    else 0
)


winning_trades = (
    (trades["PnL"] > 0).sum()
    if not trades.empty
    else 0
)


losing_trades = (
    (trades["PnL"] < 0).sum()
    if not trades.empty
    else 0
)


average_pnl = (
    trades["PnL"].mean()
    if not trades.empty
    else 0
)


print(
    "\n--- P&L SUMMARY ---"
)

print(
    f"Total P&L: {total_pnl:.2f}"
)

print(
    f"Winning Trades: {winning_trades}"
)

print(
    f"Losing Trades: {losing_trades}"
)

print(
    f"Average P&L per Trade: {average_pnl:.2f}"
)


# =========================================================
# 11. TRADE HISTORY
# =========================================================

trade_history_file = (
    RESULT_FOLDER /
    f"{asset.replace(' ', '_')}_trade_history.csv"
)


trades.to_csv(
    trade_history_file,
    index=False
)


# Dashboard-compatible trade history
common_trade_file = (
    RESULT_FOLDER /
    "latest_trade_history.csv"
)


trades.to_csv(
    common_trade_file,
    index=False
)


print(
    f"\nTrade history saved: "
    f"{trade_history_file}"
)


# =========================================================
# 12. WIN RATE
# =========================================================

total_trades = len(
    trades
)


win_rate = (

    winning_trades
    /
    total_trades
    *
    100

    if total_trades > 0

    else 0
)


print(
    "\n--- WIN RATE ---"
)

print(
    f"Total Trades: {total_trades}"
)

print(
    f"Winning Trades: {winning_trades}"
)

print(
    f"Losing Trades: {losing_trades}"
)

print(
    f"Win Rate: {win_rate:.2f}%"
)


# =========================================================
# 13. PROFIT FACTOR
# =========================================================

gross_profit = (

    trades.loc[
        trades["PnL"] > 0,
        "PnL"
    ].sum()

    if not trades.empty

    else 0
)


gross_loss = (

    trades.loc[
        trades["PnL"] < 0,
        "PnL"
    ].sum()

    if not trades.empty

    else 0
)


profit_factor = (

    gross_profit /
    abs(gross_loss)

    if gross_loss != 0

    else float("inf")
)


print(
    "\n--- PROFIT FACTOR ---"
)

print(
    f"Gross Profit: {gross_profit:.2f}"
)

print(
    f"Gross Loss: {gross_loss:.2f}"
)

print(
    f"Profit Factor: {profit_factor:.2f}"
)


# =========================================================
# 14. DRAWDOWN
# =========================================================

equity = (
    stats["_equity_curve"]["Equity"]
)


running_peak = (
    equity.cummax()
)


drawdown = (
    (
        equity -
        running_peak
    )
    /
    running_peak
) * 100


max_drawdown = (
    drawdown.min()
)


print(
    "\n--- DRAWDOWN ---"
)

print(
    f"Maximum Drawdown: "
    f"{max_drawdown:.2f}%"
)


# =========================================================
# 15. SHARPE RATIO
# =========================================================

daily_returns = (
    equity
    .pct_change()
    .dropna()
)


risk_free_rate = 0.0


excess_returns = (
    daily_returns -
    (
        risk_free_rate /
        252
    )
)


if (
    len(excess_returns) > 1
    and
    excess_returns.std() != 0
):

    sharpe_ratio = (
        excess_returns.mean()
        /
        excess_returns.std()
    ) * (
        252 ** 0.5
    )

else:

    sharpe_ratio = 0


print(
    "\n--- SHARPE RATIO ---"
)

print(
    f"Sharpe Ratio: "
    f"{sharpe_ratio:.3f}"
)


# =========================================================
# 16. TRANSACTION COST COMPARISON
# =========================================================

stats_no_cost = run_backtest(
    commission=0
)


stats_with_cost = run_backtest(
    commission=0.001
)


print(
    "\n--- TRANSACTION COST COMPARISON ---"
)


print(
    f"Return without costs: "
    f"{stats_no_cost['Return [%]']:.2f}%"
)


print(
    f"Return with costs: "
    f"{stats_with_cost['Return [%]']:.2f}%"
)


print(
    f"Final equity without costs: "
    f"{stats_no_cost['Equity Final [$]']:.2f}"
)


print(
    f"Final equity with costs: "
    f"{stats_with_cost['Equity Final [$]']:.2f}"
)


# =========================================================
# 17. SQLITE TRADE STORAGE
# =========================================================

connection = sqlite3.connect(
    RESULT_FOLDER /
    "tradelab.db"
)


if not trades.empty:

    sqlite_trades = trades.copy()

    for column in sqlite_trades.columns:
        if pd.api.types.is_timedelta64_dtype(sqlite_trades[column]):
            sqlite_trades[column] = (
                sqlite_trades[column].dt.total_seconds() / 86400
            )

    sqlite_trades.insert(0, "Asset", asset)

    table_exists = pd.read_sql(
        "SELECT name FROM sqlite_master "
        "WHERE type='table' AND name='trades'",
        connection
    ).shape[0] > 0

    if table_exists:
        existing_columns = pd.read_sql(
            "PRAGMA table_info(trades)",
            connection
        )["name"].tolist()

        if "Asset" not in existing_columns:
            connection.execute("DROP TABLE trades")
            connection.commit()
            table_exists = False

    if table_exists:
        connection.execute(
            "DELETE FROM trades WHERE Asset = ?",
            (asset,)
        )
        connection.commit()

        sqlite_trades.to_sql(
            "trades",
            connection,
            if_exists="append",
            index=False
        )
    else:
        sqlite_trades.to_sql(
            "trades",
            connection,
            if_exists="replace",
            index=False
        )


connection.close()


print(
    "\nTrades saved to SQLite successfully."
)


# =========================================================
# 18. VERIFY SQLITE
# =========================================================

connection = sqlite3.connect(
    RESULT_FOLDER /
    "tradelab.db"
)


stored_trades = pd.read_sql(
    "SELECT * FROM trades WHERE Asset = ?",
    connection,
    params=(asset,)
)


connection.close()


print(
    "\n--- STORED TRADES ---"
)

print(
    stored_trades.head()
)

print(
    "\nTotal stored trades:",
    len(stored_trades)
)


# =========================================================
# 19. FINAL SUMMARY
# =========================================================

print(
    "\n========================================"
)

print(
    "BACKTEST COMPLETE"
)

print(
    f"Asset: {asset}"
)

print(
    f"Return: "
    f"{stats['Return [%]']:.2f}%"
)

print(
    f"Buy & Hold Return: "
    f"{stats['Buy & Hold Return [%]']:.2f}%"
)

print(
    f"Win Rate: "
    f"{win_rate:.2f}%"
)

print(
    f"Sharpe Ratio: "
    f"{sharpe_ratio:.3f}"
)

print(
    f"Max Drawdown: "
    f"{max_drawdown:.2f}%"
)

print(
    f"Profit Factor: "
    f"{profit_factor:.2f}"
)

print(
    f"Total Trades: "
    f"{total_trades}"
)

print(
    "========================================"
)