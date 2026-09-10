"""
TradeLab - P7.2 Batch Backtesting
Runs the existing backtesting engine across all V1 validation assets
and creates one consolidated validation CSV.

Run from project root:
    python Src/validation/batch_backtest.py
"""

from pathlib import Path
import subprocess
import sys
import re
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]
BACKTEST_SCRIPT = PROJECT_ROOT / "Src" / "data" / "backtesting_test.py"
RESULT_FOLDER = PROJECT_ROOT / "result"
VALIDATION_FOLDER = RESULT_FOLDER / "validation"
VALIDATION_FOLDER.mkdir(parents=True, exist_ok=True)

ASSETS = [
    "RELIANCE",
    "GACM Technologies",
    "ETERNAL",
    "IRFC",
    "RVNL",
    "RailTel",
    "Torrent Power",
    "NIFTY 50",
    "BANK NIFTY",
    "SENSEX",
]


def extract_metric(output, pattern, default=None):
    match = re.search(pattern, output, re.MULTILINE)
    if not match:
        return default

    value = match.group(1).replace(",", "").strip()

    try:
        return float(value)
    except ValueError:
        return default


def extract_int(output, pattern, default=None):
    value = extract_metric(output, pattern, default)
    return int(value) if value is not None else default


results = []

print("\n========================================")
print("TRADELAB P7.2 BATCH VALIDATION")
print("========================================")
print(f"Assets to test: {len(ASSETS)}\n")


for number, asset in enumerate(ASSETS, start=1):

    print("----------------------------------------")
    print(f"[{number}/{len(ASSETS)}] Testing: {asset}")
    print("----------------------------------------")

    env = dict(__import__("os").environ)
    env["PYTHONIOENCODING"] = "utf-8"

    process = subprocess.run(
        [
            sys.executable,
            str(BACKTEST_SCRIPT),
            asset,
        ],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        env=env,
    )

    output = process.stdout + "\n" + process.stderr

    if process.returncode != 0:

        print("STATUS: FAILED")

        results.append(
            {
                "Asset": asset,
                "Status": "FAILED",
                "ReturnPct": None,
                "BuyHoldReturnPct": None,
                "WinRatePct": None,
                "SharpeRatio": None,
                "MaxDrawdownPct": None,
                "ProfitFactor": None,
                "TotalTrades": None,
            }
        )

        print(output[-1500:])
        continue

    result = {
        "Asset": asset,
        "Status": "SUCCESS",
        "ReturnPct": extract_metric(
            output,
            r"^Return:\s*([-+]?\d+(?:\.\d+)?)%",
        ),
        "BuyHoldReturnPct": extract_metric(
            output,
            r"^Buy & Hold Return:\s*([-+]?\d+(?:\.\d+)?)%",
        ),
        "WinRatePct": extract_metric(
            output,
            r"^Win Rate:\s*([-+]?\d+(?:\.\d+)?)%",
        ),
        "SharpeRatio": extract_metric(
            output,
            r"^Sharpe Ratio:\s*([-+]?\d+(?:\.\d+)?)",
        ),
        "MaxDrawdownPct": extract_metric(
            output,
            r"^Max Drawdown:\s*([-+]?\d+(?:\.\d+)?)%",
        ),
        "ProfitFactor": extract_metric(
            output,
            r"^Profit Factor:\s*([-+]?\d+(?:\.\d+)?)",
        ),
        "TotalTrades": extract_int(
            output,
            r"^Total Trades:\s*(\d+)",
        ),
    }

    results.append(result)

    print("STATUS: SUCCESS")
    print(f"Return: {result['ReturnPct']}%")
    print(f"Win Rate: {result['WinRatePct']}%")
    print(f"Sharpe: {result['SharpeRatio']}")
    print(f"Max Drawdown: {result['MaxDrawdownPct']}%")
    print(f"Profit Factor: {result['ProfitFactor']}")
    print(f"Trades: {result['TotalTrades']}")


# =========================================================
# CONSOLIDATED RESULTS
# =========================================================

validation_df = pd.DataFrame(results)

validation_file = (
    VALIDATION_FOLDER / "validation_results.csv"
)

validation_df.to_csv(
    validation_file,
    index=False,
)


# =========================================================
# SUMMARY
# =========================================================

successful = validation_df[
    validation_df["Status"] == "SUCCESS"
]

print("\n========================================")
print("P7.2 BATCH VALIDATION COMPLETE")
print("========================================")
print(
    f"Successful assets: "
    f"{len(successful)}/{len(validation_df)}"
)
print(f"Results saved: {validation_file}")

if not successful.empty:

    print("\n--- VALIDATION TABLE ---")
    print(
        successful[
            [
                "Asset",
                "ReturnPct",
                "BuyHoldReturnPct",
                "WinRatePct",
                "SharpeRatio",
                "MaxDrawdownPct",
                "ProfitFactor",
                "TotalTrades",
            ]
        ].to_string(index=False)
    )

print("\n========================================")
