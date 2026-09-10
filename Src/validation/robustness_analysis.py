from pathlib import Path
import pandas as pd
import numpy as np


# ============================================================
# P7.7 — ROBUSTNESS ANALYSIS
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

OVERFITTING_FILE = (
    VALIDATION_DIR
    / "overfitting_parameter_results.csv"
)

OOS_FILE = (
    VALIDATION_DIR
    / "oos_validation_results.csv"
)

OUTPUT_FILE = (
    VALIDATION_DIR
    / "robustness_analysis.csv"
)


# ============================================================
# HELPERS
# ============================================================

def load_csv(path, name):
    if not path.exists():
        print(f"WARNING: {name} not found:")
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


def find_column(df, possible_names):

    for name in possible_names:

        if name in df.columns:
            return name

    return None


# ============================================================
# START
# ============================================================

print("=" * 70)
print("P7.7 — ROBUSTNESS ANALYSIS")
print("=" * 70)

print()
print("No parameter optimization is performed.")
print("This analysis evaluates existing validation results only.")
print()


# ============================================================
# LOAD DATA
# ============================================================

batch = load_csv(
    BATCH_FILE,
    "Batch Validation Results"
)

period = load_csv(
    PERIOD_FILE,
    "Period Validation Results"
)

overfit = load_csv(
    OVERFITTING_FILE,
    "Overfitting Results"
)

oos = load_csv(
    OOS_FILE,
    "OOS Results"
)


# ============================================================
# ASSET-LEVEL ROBUSTNESS
# ============================================================

asset_rows = []


if batch is not None:

    print()
    print("-" * 70)
    print("ASSET-LEVEL ROBUSTNESS")
    print("-" * 70)

    asset_col = find_column(
        batch,
        ["Asset", "asset"]
    )

    return_col = find_column(
        batch,
        ["Return", "ReturnPct", "return"]
    )

    sharpe_col = find_column(
        batch,
        ["Sharpe", "SharpeRatio"]
    )

    dd_col = find_column(
        batch,
        [
            "Max Drawdown",
            "MaxDrawdownPct",
            "MaxDrawdown"
        ]
    )

    pf_col = find_column(
        batch,
        [
            "Profit Factor",
            "ProfitFactor"
        ]
    )

    trades_col = find_column(
        batch,
        [
            "Total Trades",
            "TotalTrades",
            "Trades"
        ]
    )

    if asset_col:

        for asset, group in batch.groupby(
            asset_col
        ):

            row = {
                "Asset": asset
            }

            if return_col:
                values = pd.to_numeric(
                    group[return_col],
                    errors="coerce"
                ).dropna()

                if len(values):
                    row["Batch_Return"] = values.mean()

            if sharpe_col:
                values = pd.to_numeric(
                    group[sharpe_col],
                    errors="coerce"
                ).dropna()

                if len(values):
                    row["Batch_Sharpe"] = values.mean()

            if dd_col:
                values = pd.to_numeric(
                    group[dd_col],
                    errors="coerce"
                ).dropna()

                if len(values):
                    row["Batch_MaxDD"] = values.mean()

            if pf_col:
                values = pd.to_numeric(
                    group[pf_col],
                    errors="coerce"
                ).dropna()

                if len(values):
                    row["Batch_PF"] = values.mean()

            if trades_col:
                values = pd.to_numeric(
                    group[trades_col],
                    errors="coerce"
                ).dropna()

                if len(values):
                    row["Batch_Trades"] = values.mean()

            asset_rows.append(row)


# ============================================================
# PERIOD ROBUSTNESS
# ============================================================

if period is not None:

    print()
    print("-" * 70)
    print("PERIOD ROBUSTNESS")
    print("-" * 70)

    asset_col = find_column(
        period,
        ["Asset", "asset"]
    )

    return_col = find_column(
        period,
        ["Return", "ReturnPct", "return"]
    )

    sharpe_col = find_column(
        period,
        ["Sharpe", "SharpeRatio"]
    )

    dd_col = find_column(
        period,
        [
            "Max Drawdown",
            "MaxDrawdownPct",
            "MaxDrawdown"
        ]
    )

    pf_col = find_column(
        period,
        [
            "Profit Factor",
            "ProfitFactor"
        ]
    )

    if asset_col:

        period_summary = (
            period
            .groupby(asset_col)
            .agg(
                Periods_Tested=(
                    asset_col,
                    "count"
                )
            )
            .reset_index()
        )

        positive_counts = (
            period
            .assign(
                _return=pd.to_numeric(
                    period[return_col],
                    errors="coerce"
                )
            )
            .groupby(asset_col)["_return"]
            .apply(
                lambda x: (x > 0).sum()
            )
        )

        negative_counts = (
            period
            .assign(
                _return=pd.to_numeric(
                    period[return_col],
                    errors="coerce"
                )
            )
            .groupby(asset_col)["_return"]
            .apply(
                lambda x: (x < 0).sum()
            )
        )

        for row in asset_rows:

            asset = row["Asset"]

            if asset in positive_counts.index:

                row["Positive_Periods"] = int(
                    positive_counts.loc[asset]
                )

                row["Negative_Periods"] = int(
                    negative_counts.loc[asset]
                )

                total = (
                    row["Positive_Periods"]
                    + row["Negative_Periods"]
                )

                if total > 0:

                    row["Positive_Period_Rate"] = (
                        row["Positive_Periods"]
                        / total
                    ) * 100


# ============================================================
# OOS ROBUSTNESS
# ============================================================

if oos is not None:

    print()
    print("-" * 70)
    print("OUT-OF-SAMPLE ROBUSTNESS")
    print("-" * 70)

    asset_col = find_column(
        oos,
        ["Asset", "asset"]
    )

    return_col = find_column(
        oos,
        ["ReturnPct", "Return"]
    )

    sharpe_col = find_column(
        oos,
        ["SharpeRatio", "Sharpe"]
    )

    dd_col = find_column(
        oos,
        [
            "MaxDrawdownPct",
            "Max Drawdown"
        ]
    )

    pf_col = find_column(
        oos,
        [
            "ProfitFactor",
            "Profit Factor"
        ]
    )

    if asset_col:

        for _, row_oos in oos.iterrows():

            asset = row_oos[
                asset_col
            ]

            matching = [
                x for x in asset_rows
                if x["Asset"] == asset
            ]

            if not matching:
                continue

            row = matching[0]

            if return_col:
                row["OOS_Return"] = pd.to_numeric(
                    row_oos[return_col],
                    errors="coerce"
                )

            if sharpe_col:
                row["OOS_Sharpe"] = pd.to_numeric(
                    row_oos[sharpe_col],
                    errors="coerce"
                )

            if dd_col:
                row["OOS_MaxDD"] = pd.to_numeric(
                    row_oos[dd_col],
                    errors="coerce"
                )

            if pf_col:
                row["OOS_PF"] = pd.to_numeric(
                    row_oos[pf_col],
                    errors="coerce"
                )


# ============================================================
# ROBUSTNESS FLAGS
# ============================================================

for row in asset_rows:

    positive_period_rate = row.get(
        "Positive_Period_Rate",
        np.nan
    )

    oos_return = row.get(
        "OOS_Return",
        np.nan
    )

    oos_pf = row.get(
        "OOS_PF",
        np.nan
    )

    oos_sharpe = row.get(
        "OOS_Sharpe",
        np.nan
    )


    # --------------------------------------------------------
    # OOS status
    # --------------------------------------------------------

    if pd.isna(oos_return):

        oos_status = "NO_OOS_DATA"

    elif (
        oos_return > 0
        and oos_pf > 1
        and oos_sharpe > 0
    ):

        oos_status = "POSITIVE_OOS"

    else:

        oos_status = "WEAK_OOS"


    # --------------------------------------------------------
    # Period consistency
    # --------------------------------------------------------

    if pd.isna(
        positive_period_rate
    ):

        period_status = "NO_PERIOD_DATA"

    elif positive_period_rate >= 66.67:

        period_status = "CONSISTENT"

    elif positive_period_rate >= 33.33:

        period_status = "MIXED"

    else:

        period_status = "INCONSISTENT"


    row["OOS_Status"] = oos_status

    row["Period_Status"] = period_status


# ============================================================
# CREATE DATAFRAME
# ============================================================

robustness_df = pd.DataFrame(
    asset_rows
)


# ============================================================
# SAVE
# ============================================================

if not robustness_df.empty:

    robustness_df.to_csv(
        OUTPUT_FILE,
        index=False
    )

    print()
    print("=" * 70)
    print("P7.7 ANALYSIS COMPLETE")
    print("=" * 70)

    print()
    print(
        f"Assets analyzed: "
        f"{len(robustness_df)}"
    )

    print()
    print(
        "Results saved to:"
    )

    print(
        OUTPUT_FILE
    )

    print()
    print(
        robustness_df.to_string(
            index=False
        )
    )

else:

    print()
    print("=" * 70)
    print("NO ROBUSTNESS RESULTS GENERATED")
    print("=" * 70)


print()
print("=" * 70)
print("IMPORTANT")
print("=" * 70)
print(
    "No strategy parameters were changed."
)

print(
    "No optimization was performed."
)

print(
    "This is an analytical robustness check."
)

print("=" * 70)