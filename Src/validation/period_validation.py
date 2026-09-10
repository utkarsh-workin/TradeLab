"""
TradeLab - P7.3 Multiple Time Period Validation

Runs the existing TradeLab backtest on multiple historical periods
without changing strategy parameters.

Run from project root:
    python Src/validation/period_validation.py
"""

from pathlib import Path
import subprocess
import sys
import os
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


# The validation periods are deliberately fixed before looking at results.
PERIODS = [
    ("2020-01-01", "2021-12-31", "2020-2021"),
    ("2022-01-01", "2023-12-31", "2022-2023"),
    ("2024-01-01", "2025-12-31", "2024-2025"),
]


def extract_metric(output, pattern, default=None):
    match = re.search(pattern, output, re.MULTILINE)
    if not match:
        return default

    try:
        return float(match.group(1).replace(",", "").strip())
    except ValueError:
        return default


def extract_int(output, pattern, default=None):
    value = extract_metric(output, pattern, default)
    return int(value) if value is not None else default


def create_period_file(asset, start_date, end_date, period_name):
    """
    Create a temporary processed CSV containing only the requested period.

    The original processed dataset is never modified.
    """
    # Read the same mapping used by the project engine.
    asset_files = {
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

    source = PROJECT_ROOT / "Dataset" / "processed" / asset_files[asset]
    df = pd.read_csv(source, parse_dates=["Date"])

    mask = (
        (df["Date"] >= pd.Timestamp(start_date))
        & (df["Date"] <= pd.Timestamp(end_date))
    )

    period_df = df.loc[mask].copy()

    temp_dir = VALIDATION_FOLDER / "temp_period_data"
    temp_dir.mkdir(parents=True, exist_ok=True)

    safe_asset = asset.replace(" ", "_")
    temp_file = temp_dir / f"{safe_asset}_{period_name}.csv"

    period_df.to_csv(temp_file, index=False)

    return temp_file, len(period_df)


def run_engine_with_temp_data(
    asset,
    temp_file,
    period_name,
):
    """
    Run the existing engine without changing its source code by temporarily
    swapping the selected processed CSV, then restoring it.
    """

    asset_files = {
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

    original_file = PROJECT_ROOT / "Dataset" / "processed" / asset_files[asset]
    backup_file = original_file.with_suffix(".period_backup.csv")

    original_file.replace(backup_file)

    try:
        pd.read_csv(temp_file).to_csv(original_file, index=False)

        env = os.environ.copy()
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

        return process

    finally:
        if original_file.exists():
            original_file.unlink()

        backup_file.replace(original_file)


results = []

print("\n========================================")
print("TRADELAB P7.3 PERIOD VALIDATION")
print("========================================")
print(f"Assets: {len(ASSETS)}")
print(f"Periods: {len(PERIODS)}")
print(f"Total tests: {len(ASSETS) * len(PERIODS)}")


for asset in ASSETS:

    for start_date, end_date, period_name in PERIODS:

        print("\n----------------------------------------")
        print(f"Asset: {asset}")
        print(f"Period: {period_name}")
        print(f"Dates: {start_date} → {end_date}")
        print("----------------------------------------")

        temp_file, row_count = create_period_file(
            asset,
            start_date,
            end_date,
            period_name,
        )

        if row_count < 60:
            print(f"STATUS: SKIPPED — only {row_count} rows")

            results.append(
                {
                    "Asset": asset,
                    "Period": period_name,
                    "StartDate": start_date,
                    "EndDate": end_date,
                    "Rows": row_count,
                    "Status": "SKIPPED",
                    "ReturnPct": None,
                    "BuyHoldReturnPct": None,
                    "WinRatePct": None,
                    "SharpeRatio": None,
                    "MaxDrawdownPct": None,
                    "ProfitFactor": None,
                    "TotalTrades": None,
                }
            )
            continue

        process = run_engine_with_temp_data(
            asset,
            temp_file,
            period_name,
        )

        output = process.stdout + "\n" + process.stderr

        if process.returncode != 0:

            print("STATUS: FAILED")
            print(output[-1200:])

            results.append(
                {
                    "Asset": asset,
                    "Period": period_name,
                    "StartDate": start_date,
                    "EndDate": end_date,
                    "Rows": row_count,
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
            continue

        result = {
            "Asset": asset,
            "Period": period_name,
            "StartDate": start_date,
            "EndDate": end_date,
            "Rows": row_count,
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
        print(f"Rows: {row_count}")
        print(f"Return: {result['ReturnPct']}%")
        print(f"Win Rate: {result['WinRatePct']}%")
        print(f"Sharpe: {result['SharpeRatio']}")
        print(f"Max Drawdown: {result['MaxDrawdownPct']}%")
        print(f"Profit Factor: {result['ProfitFactor']}")
        print(f"Trades: {result['TotalTrades']}")


results_df = pd.DataFrame(results)

output_file = (
    VALIDATION_FOLDER / "period_validation_results.csv"
)

results_df.to_csv(
    output_file,
    index=False,
)

print("\n========================================")
print("P7.3 PERIOD VALIDATION COMPLETE")
print("========================================")
print(f"Results saved: {output_file}")

successful = results_df[
    results_df["Status"] == "SUCCESS"
]

print(
    f"Successful tests: "
    f"{len(successful)}/{len(results_df)}"
)

if not successful.empty:
    print("\n--- PERIOD VALIDATION TABLE ---")
    print(successful.to_string(index=False))

print("\n========================================")
