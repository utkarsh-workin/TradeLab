# =========================================================
# TRADELAB P7.5 — OVERFITTING / PARAMETER SENSITIVITY CHECK
# =========================================================
#
# Purpose:
# Check whether TradeLab performance depends heavily on one
# exact parameter combination.
#
# This script DOES NOT modify the main backtesting engine.
# It runs nearby parameter variations and saves the results.
#
# Baseline:
# EMA 20 / EMA 50
# RSI threshold 50
# Stop Loss 5%
# Reward:Risk 1:2
#
# Tested values:
# Fast EMA: 15, 20, 25
# Slow EMA: 40, 50, 60
# RSI threshold: 45, 50, 55
# Stop Loss: 4%, 5%, 6%
# Reward:Risk: 1.5, 2.0, 2.5
#
# Total combinations per asset = 3^5 = 243
# 10 assets = 2430 tests
# =========================================================

from backtesting import Backtest, Strategy
import pandas as pd
import numpy as np
import sys
from pathlib import Path


# =========================================================
# 1. PROJECT PATHS
# =========================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]
PROCESSED_FOLDER = PROJECT_ROOT / "Dataset" / "processed"
RESULT_FOLDER = PROJECT_ROOT / "result" / "validation"
RESULT_FOLDER.mkdir(parents=True, exist_ok=True)


# =========================================================
# 2. ASSETS
# =========================================================

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
# 3. BASELINE PARAMETERS
# =========================================================

BASELINE = {
    "fast_ema": 20,
    "slow_ema": 50,
    "rsi_threshold": 50,
    "stop_loss_pct": 0.05,
    "reward_risk": 2.0,
}

INITIAL_CAPITAL = 100000
RISK_PER_TRADE = 0.01
COMMISSION = 0.001


# =========================================================
# 4. PARAMETER GRID
# =========================================================

FAST_EMAS = [15, 20, 25]
SLOW_EMAS = [40, 50, 60]
RSI_THRESHOLDS = [45, 50, 55]
STOP_LOSSES = [0.04, 0.05, 0.06]
REWARD_RISKS = [1.5, 2.0, 2.5]


# =========================================================
# 5. LOAD DATA
# =========================================================

def load_data(asset):
    data_file = PROCESSED_FOLDER / ASSET_FILES[asset]

    df = pd.read_csv(
        data_file,
        parse_dates=["Date"]
    )

    df = df.set_index("Date")

    required_columns = ["Open", "High", "Low", "Close"]

    if "Volume" not in df.columns:
        df["Volume"] = 0

    df = df[required_columns + ["Volume"]].copy()
    df["Volume"] = pd.to_numeric(
        df["Volume"],
        errors="coerce"
    ).fillna(0)

    return df


# =========================================================
# 6. STRATEGY FACTORY
# =========================================================

def create_strategy(
    fast_ema,
    slow_ema,
    rsi_threshold,
    stop_loss_pct,
    reward_risk,
    is_index,
):

    class SensitivityStrategy(Strategy):

        def init(self):

            self.fast_ema = self.I(
                lambda x: pd.Series(x).ewm(
                    span=fast_ema,
                    adjust=False
                ).mean(),
                self.data.Close
            )

            self.slow_ema = self.I(
                lambda x: pd.Series(x).ewm(
                    span=slow_ema,
                    adjust=False
                ).mean(),
                self.data.Close
            )

            def calculate_rsi(close):

                series = pd.Series(close)
                delta = series.diff()

                gain = delta.clip(lower=0)
                loss = -delta.clip(upper=0)

                avg_gain = gain.rolling(14).mean()
                avg_loss = loss.rolling(14).mean()

                rs = avg_gain / avg_loss

                return 100 - (
                    100 / (1 + rs)
                )

            self.rsi = self.I(
                calculate_rsi,
                self.data.Close
            )

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

            self.macd_signal = self.I(
                lambda x: pd.Series(x).ewm(
                    span=9,
                    adjust=False
                ).mean(),
                self.macd
            )

            self.volume_sma20 = self.I(
                lambda x: pd.Series(x).rolling(20).mean(),
                self.data.Volume
            )

            self.pending_entry = False


        def next(self):

            # -------------------------
            # Exit
            # -------------------------

            if self.position:

                exit_condition = (
                    self.data.Close[-1] < self.fast_ema[-1]
                    or self.fast_ema[-1] < self.slow_ema[-1]
                    or self.rsi[-1] < rsi_threshold
                    or self.macd[-1] < self.macd_signal[-1]
                )

                if exit_condition:
                    self.position.close()
                    return


            # -------------------------
            # Entry
            # -------------------------

            volume_condition = (
                True
                if is_index
                else (
                    self.data.Volume[-1]
                    > self.volume_sma20[-1]
                )
            )

            entry_condition = (
                self.data.Close[-1] > self.fast_ema[-1]
                and self.fast_ema[-1] > self.slow_ema[-1]
                and self.rsi[-1] > rsi_threshold
                and self.macd[-1] > self.macd_signal[-1]
                and volume_condition
            )

            if (
                entry_condition
                and not self.position
                and not self.pending_entry
            ):

                signal_price = float(
                    self.data.Close[-1]
                )

                estimated_stop = (
                    signal_price
                    * (1 - stop_loss_pct)
                )

                risk_per_unit = (
                    signal_price - estimated_stop
                )

                risk_amount = (
                    float(self.equity)
                    * RISK_PER_TRADE
                )

                position_size = int(
                    np.floor(
                        risk_amount / risk_per_unit
                    )
                )

                position_size = max(
                    1,
                    position_size
                )

                self.buy(
                    size=position_size
                )

                self.pending_entry = True


            # -------------------------
            # Attach actual SL / TP
            # -------------------------

            if self.position:

                if self.trades:

                    active_trade = self.trades[-1]

                    actual_entry_price = float(
                        active_trade.entry_price
                    )

                    actual_stop_loss = (
                        actual_entry_price
                        * (1 - stop_loss_pct)
                    )

                    actual_risk = (
                        actual_entry_price
                        - actual_stop_loss
                    )

                    actual_target = (
                        actual_entry_price
                        + (
                            actual_risk
                            * reward_risk
                        )
                    )

                    active_trade.sl = actual_stop_loss
                    active_trade.tp = actual_target

                    self.pending_entry = False


    return SensitivityStrategy


# =========================================================
# 7. RUN ONE TEST
# =========================================================

def run_test(
    df,
    asset,
    fast_ema,
    slow_ema,
    rsi_threshold,
    stop_loss_pct,
    reward_risk,
):

    # Invalid EMA relationship is not a valid baseline-style
    # configuration for this strategy.
    if fast_ema >= slow_ema:
        return None

    strategy_class = create_strategy(
        fast_ema=fast_ema,
        slow_ema=slow_ema,
        rsi_threshold=rsi_threshold,
        stop_loss_pct=stop_loss_pct,
        reward_risk=reward_risk,
        is_index=(asset in INDEX_ASSETS),
    )

    try:

        bt = Backtest(
            df,
            strategy_class,
            cash=INITIAL_CAPITAL,
            commission=COMMISSION,
        )

        stats = bt.run()

        return {
            "Asset": asset,
            "FastEMA": fast_ema,
            "SlowEMA": slow_ema,
            "RSIThreshold": rsi_threshold,
            "StopLossPct": stop_loss_pct * 100,
            "RewardRisk": reward_risk,
            "ReturnPct": float(
                stats["Return [%]"]
            ),
            "BuyHoldReturnPct": float(
                stats["Buy & Hold Return [%]"]
            ),
            "SharpeRatio": float(
                stats["Sharpe Ratio"]
            ),
            "MaxDrawdownPct": float(
                stats["Max. Drawdown [%]"]
            ),
            "ProfitFactor": float(
                stats["Profit Factor"]
            ),
            "TotalTrades": int(
                stats["# Trades"]
            ),
            "WinRatePct": float(
                stats["Win Rate [%]"]
            ),
        }

    except Exception as error:

        print(
            f"ERROR | {asset} | "
            f"EMA {fast_ema}/{slow_ema} | "
            f"RSI {rsi_threshold} | "
            f"SL {stop_loss_pct:.2f} | "
            f"RR {reward_risk} | "
            f"{error}"
        )

        return None


# =========================================================
# 8. MAIN
# =========================================================

print("\n========================================")
print("TRADELAB P7.5 OVERFITTING CHECK")
print("========================================")

print(
    "Each asset: 243 parameter combinations"
)

print(
    "Assets: 10"
)

print(
    "Maximum tests: 2430"
)

print(
    f"Baseline: EMA {BASELINE['fast_ema']}/"
    f"{BASELINE['slow_ema']}, "
    f"RSI {BASELINE['rsi_threshold']}, "
    f"SL {BASELINE['stop_loss_pct'] * 100:.0f}%, "
    f"RR 1:{BASELINE['reward_risk']}"
)


# Optional command-line asset
if len(sys.argv) > 1:

    requested_asset = sys.argv[1]

    if requested_asset not in ASSET_FILES:

        print(
            f"ERROR: Unknown asset '{requested_asset}'"
        )

        print("Available assets:")

        for name in ASSET_FILES:
            print(f"- {name}")

        sys.exit(1)

    assets_to_test = [requested_asset]

else:

    assets_to_test = list(
        ASSET_FILES.keys()
    )


results = []


# =========================================================
# 9. PARAMETER SWEEP
# =========================================================

for asset in assets_to_test:

    print("\n----------------------------------------")
    print(f"Asset: {asset}")
    print("----------------------------------------")

    df = load_data(asset)

    test_number = 0

    for fast_ema in FAST_EMAS:

        for slow_ema in SLOW_EMAS:

            if fast_ema >= slow_ema:
                continue

            for rsi_threshold in RSI_THRESHOLDS:

                for stop_loss_pct in STOP_LOSSES:

                    for reward_risk in REWARD_RISKS:

                        test_number += 1

                        result = run_test(
                            df=df,
                            asset=asset,
                            fast_ema=fast_ema,
                            slow_ema=slow_ema,
                            rsi_threshold=rsi_threshold,
                            stop_loss_pct=stop_loss_pct,
                            reward_risk=reward_risk,
                        )

                        if result is not None:
                            results.append(result)

    print(
        f"Completed: {test_number} tests"
    )


# =========================================================
# 10. SAVE RESULTS
# =========================================================

results_df = pd.DataFrame(results)

output_file = (
    RESULT_FOLDER
    / "overfitting_parameter_results.csv"
)

results_df.to_csv(
    output_file,
    index=False
)


# =========================================================
# 11. BASELINE IDENTIFICATION
# =========================================================

baseline_rows = results_df[
    (results_df["FastEMA"] == BASELINE["fast_ema"])
    & (results_df["SlowEMA"] == BASELINE["slow_ema"])
    & (
        results_df["RSIThreshold"]
        == BASELINE["rsi_threshold"]
    )
    & (
        results_df["StopLossPct"]
        == BASELINE["stop_loss_pct"] * 100
    )
    & (
        results_df["RewardRisk"]
        == BASELINE["reward_risk"]
    )
].copy()


# =========================================================
# 12. SUMMARY
# =========================================================

print("\n========================================")
print("P7.5 OVERFITTING CHECK COMPLETE")
print("========================================")

print(
    f"Successful tests: {len(results_df)}"
)

print(
    f"Results saved: {output_file}"
)


if not baseline_rows.empty:

    baseline_row = baseline_rows.iloc[0]

    print("\n--- BASELINE RESULT ---")

    print(
        f"Return: "
        f"{baseline_row['ReturnPct']:.2f}%"
    )

    print(
        f"Sharpe: "
        f"{baseline_row['SharpeRatio']:.3f}"
    )

    print(
        f"Max Drawdown: "
        f"{baseline_row['MaxDrawdownPct']:.2f}%"
    )

    print(
        f"Profit Factor: "
        f"{baseline_row['ProfitFactor']:.2f}"
    )

    print(
        f"Trades: "
        f"{int(baseline_row['TotalTrades'])}"
    )


# =========================================================
# 13. TOP CONFIGURATIONS
# =========================================================

if not results_df.empty:

    top_results = (
        results_df
        .sort_values(
            by="ReturnPct",
            ascending=False
        )
        .head(10)
    )

    print("\n--- TOP 10 CONFIGURATIONS BY RETURN ---")

    print(
        top_results[
            [
                "Asset",
                "FastEMA",
                "SlowEMA",
                "RSIThreshold",
                "StopLossPct",
                "RewardRisk",
                "ReturnPct",
                "SharpeRatio",
                "MaxDrawdownPct",
                "ProfitFactor",
                "TotalTrades",
            ]
        ].to_string(index=False)
    )


# =========================================================
# 14. IMPORTANT NOTE
# =========================================================

print("\n--- INTERPRETATION ---")

print(
    "Do NOT select the best configuration from this "
    "file and call it the final strategy."
)

print(
    "The purpose of P7.5 is sensitivity analysis: "
    "we want to see whether nearby parameter values "
    "produce broadly similar behaviour."
)

print(
    "A narrow peak around one parameter combination "
    "can indicate overfitting."
)

print(
    "A relatively stable region of results is stronger "
    "evidence of parameter robustness."
)
