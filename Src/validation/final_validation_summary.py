from pathlib import Path
import pandas as pd
import numpy as np


# ============================================================
# P7.8 — FINAL VALIDATION SUMMARY
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

VALIDATION_DIR = (
    PROJECT_ROOT
    / "result"
    / "validation"
)

BATCH_FILE = (
    VALIDATION_DIR
    / "validation_results.csv"
)

PERIOD_FILE = (
    VALIDATION_DIR
    / "period_validation_results.csv"
)

OVERFIT_FILE = (
    VALIDATION_DIR
    / "overfitting_parameter_results.csv"
)

OOS_FILE = (
    VALIDATION_DIR
    / "oos_validation_results.csv"
)

ROBUSTNESS_FILE = (
    VALIDATION_DIR
    / "robustness_analysis.csv"
)

OUTPUT_FILE = (
    VALIDATION_DIR
    / "final_validation_summary.csv"
)


# ============================================================
# HELPERS
# ============================================================

def load_file(path, name):

    if not path.exists():

        print(
            f"WARNING: {name} not found:"
        )

        print(path)

        return None

    try:

        df = pd.read_csv(path)

        print(
            f"Loaded {name}: "
            f"{len(df)} rows"
        )

        return df

    except Exception as e:

        print(
            f"ERROR loading {name}: {e}"
        )

        return None


def find_column(df, names):

    if df is None:
        return None

    for name in names:

        if name in df.columns:
            return name

    return None


def numeric_mean(df, column):

    if (
        df is None
        or column is None
        or column not in df.columns
    ):
        return np.nan

    values = pd.to_numeric(
        df[column],
        errors="coerce"
    ).dropna()

    if values.empty:
        return np.nan

    return values.mean()


# ============================================================
# START
# ============================================================

print("=" * 70)
print("P7.8 — FINAL VALIDATION SUMMARY")
print("=" * 70)

print()
print(
    "This step consolidates existing validation evidence."
)

print(
    "No strategy parameters are changed."
)

print(
    "No new backtest is performed."
)

print()


# ============================================================
# LOAD ALL VALIDATION RESULTS
# ============================================================

batch = load_file(
    BATCH_FILE,
    "Batch Validation"
)

period = load_file(
    PERIOD_FILE,
    "Period Validation"
)

overfit = load_file(
    OVERFIT_FILE,
    "Overfitting Analysis"
)

oos = load_file(
    OOS_FILE,
    "Out-of-Sample Validation"
)

robustness = load_file(
    ROBUSTNESS_FILE,
    "Robustness Analysis"
)


# ============================================================
# DETERMINE ASSET LIST
# ============================================================

assets = set()

for df in [
    batch,
    period,
    oos,
    robustness
]:

    if df is None:
        continue

    asset_col = find_column(
        df,
        ["Asset", "asset"]
    )

    if asset_col:

        assets.update(
            df[asset_col]
            .dropna()
            .astype(str)
            .tolist()
        )


assets = sorted(
    assets
)


print()
print(
    f"Assets found across validation files: "
    f"{len(assets)}"
)

print()


# ============================================================
# BUILD FINAL SUMMARY
# ============================================================

summary_rows = []


for asset in assets:

    row = {
        "Asset": asset
    }


    # ========================================================
    # BATCH VALIDATION
    # ========================================================

    if batch is not None:

        asset_col = find_column(
            batch,
            ["Asset", "asset"]
        )

        if asset_col:

            batch_asset = batch[
                batch[asset_col].astype(str)
                == asset
            ]

            if not batch_asset.empty:

                return_col = find_column(
                    batch_asset,
                    [
                        "Return",
                        "ReturnPct"
                    ]
                )

                sharpe_col = find_column(
                    batch_asset,
                    [
                        "Sharpe",
                        "SharpeRatio"
                    ]
                )

                dd_col = find_column(
                    batch_asset,
                    [
                        "Max Drawdown",
                        "MaxDrawdown",
                        "MaxDrawdownPct"
                    ]
                )

                pf_col = find_column(
                    batch_asset,
                    [
                        "Profit Factor",
                        "ProfitFactor"
                    ]
                )

                trades_col = find_column(
                    batch_asset,
                    [
                        "Total Trades",
                        "TotalTrades",
                        "Trades"
                    ]
                )

                row[
                    "Batch_Return"
                ] = numeric_mean(
                    batch_asset,
                    return_col
                )

                row[
                    "Batch_Sharpe"
                ] = numeric_mean(
                    batch_asset,
                    sharpe_col
                )

                row[
                    "Batch_MaxDD"
                ] = numeric_mean(
                    batch_asset,
                    dd_col
                )

                row[
                    "Batch_ProfitFactor"
                ] = numeric_mean(
                    batch_asset,
                    pf_col
                )

                row[
                    "Batch_Trades"
                ] = numeric_mean(
                    batch_asset,
                    trades_col
                )


    # ========================================================
    # PERIOD VALIDATION
    # ========================================================

    if period is not None:

        asset_col = find_column(
            period,
            ["Asset", "asset"]
        )

        if asset_col:

            period_asset = period[
                period[asset_col].astype(str)
                == asset
            ]

            row[
                "Periods_Tested"
            ] = len(
                period_asset
            )

            return_col = find_column(
                period_asset,
                [
                    "Return",
                    "ReturnPct"
                ]
            )

            if return_col:

                returns = pd.to_numeric(
                    period_asset[return_col],
                    errors="coerce"
                ).dropna()

                row[
                    "Positive_Periods"
                ] = int(
                    (returns > 0).sum()
                )

                row[
                    "Negative_Periods"
                ] = int(
                    (returns < 0).sum()
                )

                if len(returns) > 0:

                    row[
                        "Positive_Period_Rate"
                    ] = (
                        (returns > 0).sum()
                        / len(returns)
                    ) * 100


    # ========================================================
    # OOS VALIDATION
    # ========================================================

    if oos is not None:

        asset_col = find_column(
            oos,
            ["Asset", "asset"]
        )

        if asset_col:

            oos_asset = oos[
                oos[asset_col].astype(str)
                == asset
            ]

            if not oos_asset.empty:

                return_col = find_column(
                    oos_asset,
                    [
                        "ReturnPct",
                        "Return"
                    ]
                )

                sharpe_col = find_column(
                    oos_asset,
                    [
                        "SharpeRatio",
                        "Sharpe"
                    ]
                )

                dd_col = find_column(
                    oos_asset,
                    [
                        "MaxDrawdownPct",
                        "Max Drawdown"
                    ]
                )

                pf_col = find_column(
                    oos_asset,
                    [
                        "ProfitFactor",
                        "Profit Factor"
                    ]
                )

                trades_col = find_column(
                    oos_asset,
                    [
                        "TotalTrades",
                        "Total Trades",
                        "Trades"
                    ]
                )

                row[
                    "OOS_Return"
                ] = numeric_mean(
                    oos_asset,
                    return_col
                )

                row[
                    "OOS_Sharpe"
                ] = numeric_mean(
                    oos_asset,
                    sharpe_col
                )

                row[
                    "OOS_MaxDD"
                ] = numeric_mean(
                    oos_asset,
                    dd_col
                )

                row[
                    "OOS_ProfitFactor"
                ] = numeric_mean(
                    oos_asset,
                    pf_col
                )

                row[
                    "OOS_Trades"
                ] = numeric_mean(
                    oos_asset,
                    trades_col
                )

                row[
                    "OOS_Available"
                ] = "YES"

            else:

                row[
                    "OOS_Available"
                ] = "NO"


    # ========================================================
    # ROBUSTNESS
    # ========================================================

    if robustness is not None:

        asset_col = find_column(
            robustness,
            ["Asset", "asset"]
        )

        if asset_col:

            robustness_asset = robustness[
                robustness[asset_col].astype(str)
                == asset
            ]

            if not robustness_asset.empty:

                oos_status_col = find_column(
                    robustness_asset,
                    ["OOS_Status"]
                )

                period_status_col = find_column(
                    robustness_asset,
                    ["Period_Status"]
                )

                if oos_status_col:

                    row[
                        "Robustness_OOS_Status"
                    ] = str(
                        robustness_asset[
                            oos_status_col
                        ].iloc[0]
                    )

                if period_status_col:

                    row[
                        "Robustness_Period_Status"
                    ] = str(
                        robustness_asset[
                            period_status_col
                        ].iloc[0]
                    )


    # ========================================================
    # OVERFITTING COVERAGE
    # ========================================================

    if overfit is not None:

        asset_col = find_column(
            overfit,
            ["Asset", "asset"]
        )

        if asset_col:

            overfit_asset = overfit[
                overfit[asset_col].astype(str)
                == asset
            ]

            row[
                "Parameter_Tests"
            ] = len(
                overfit_asset
            )


    # ========================================================
    # ASSET VALIDATION CLASSIFICATION
    # ========================================================

    oos_return = row.get(
        "OOS_Return",
        np.nan
    )

    oos_pf = row.get(
        "OOS_ProfitFactor",
        np.nan
    )

    oos_sharpe = row.get(
        "OOS_Sharpe",
        np.nan
    )

    positive_rate = row.get(
        "Positive_Period_Rate",
        np.nan
    )


    if pd.isna(oos_return):

        row[
            "Validation_Status"
        ] = "OOS_DATA_UNAVAILABLE"

    elif (
        oos_return > 0
        and oos_pf > 1
        and oos_sharpe > 0
    ):

        row[
            "Validation_Status"
        ] = "POSITIVE_OOS"

    else:

        row[
            "Validation_Status"
        ] = "WEAK_OR_NEGATIVE_OOS"


    # --------------------------------------------------------
    # Period stability label
    # --------------------------------------------------------

    if pd.isna(positive_rate):

        row[
            "Period_Stability"
        ] = "NOT_AVAILABLE"

    elif positive_rate >= 66.67:

        row[
            "Period_Stability"
        ] = "RELATIVELY_STABLE"

    elif positive_rate >= 33.33:

        row[
            "Period_Stability"
        ] = "MIXED"

    else:

        row[
            "Period_Stability"
        ] = "WEAK"


    summary_rows.append(
        row
    )


# ============================================================
# FINAL DATAFRAME
# ============================================================

summary_df = pd.DataFrame(
    summary_rows
)


# ============================================================
# OVERALL SUMMARY
# ============================================================

if not summary_df.empty:

    positive_oos = (
        summary_df[
            "Validation_Status"
        ]
        == "POSITIVE_OOS"
    ).sum()

    weak_oos = (
        summary_df[
            "Validation_Status"
        ]
        == "WEAK_OR_NEGATIVE_OOS"
    ).sum()

    unavailable = (
        summary_df[
            "Validation_Status"
        ]
        == "OOS_DATA_UNAVAILABLE"
    ).sum()


    # ========================================================
    # SAVE
    # ========================================================

    summary_df.to_csv(
        OUTPUT_FILE,
        index=False
    )


    # ========================================================
    # PRINT FINAL TABLE
    # ========================================================

    print()
    print("=" * 70)
    print("FINAL VALIDATION SUMMARY")
    print("=" * 70)

    print()

    print(
        summary_df.to_string(
            index=False
        )
    )


    # ========================================================
    # HIGH-LEVEL COUNTS
    # ========================================================

    print()
    print("-" * 70)
    print("VALIDATION COVERAGE")
    print("-" * 70)

    print(
        f"Total assets analyzed : "
        f"{len(summary_df)}"
    )

    print(
        f"Positive OOS assets   : "
        f"{positive_oos}"
    )

    print(
        f"Weak/negative OOS     : "
        f"{weak_oos}"
    )

    print(
        f"OOS unavailable       : "
        f"{unavailable}"
    )

    print()

    print(
        "Parameter combinations tested: "
        f"{len(overfit) if overfit is not None else 0}"
    )

    print()

    print(
        "Final summary saved to:"
    )

    print(
        OUTPUT_FILE
    )


else:

    print()
    print("=" * 70)
    print("NO FINAL SUMMARY GENERATED")
    print("=" * 70)


# ============================================================
# IMPORTANT
# ============================================================

print()
print("=" * 70)
print("P7.8 COMPLETE")
print("=" * 70)

print()
print(
    "No strategy parameters were changed."
)

print(
    "No new backtest was performed."
)

print(
    "This file consolidates the existing validation evidence."
)

print("=" * 70)