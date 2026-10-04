from pathlib import Path

import pandas as pd
import streamlit as st

REQUIRED_COLUMNS = {
    "forecast_origin_local",
    "target_hour_local",
    "horizon",
    "forecast_movements",
    "predicted_pressure",
    "expected_traffic",
    "forecast_vs_expected",
    "traffic_zscore",
    "traffic_context",
    "recommendation",
}

EXPECTED_HORIZONS = {"t+1", "t+2", "t+3"}
EXPECTED_PRESSURES = {"Normal", "High", "Extreme"}


@st.cache_data(show_spinner=False)
def load_dashboard_data(path: Path) -> pd.DataFrame:
    """Load and validate the dashboard-ready AirSight dataset."""
    df = pd.read_csv(path)

    missing_columns = REQUIRED_COLUMNS.difference(df.columns)
    if missing_columns:
        raise ValueError(
            "Dashboard data is missing required columns: "
            + ", ".join(sorted(missing_columns))
        )

    df = df.copy()
    df["forecast_origin_local"] = pd.to_datetime(df["forecast_origin_local"])
    df["target_hour_local"] = pd.to_datetime(df["target_hour_local"])

    horizon_order = pd.CategoricalDtype(
        categories=["t+1", "t+2", "t+3"],
        ordered=True,
    )
    df["horizon"] = df["horizon"].astype(horizon_order)

    if df[list(REQUIRED_COLUMNS)].isna().any().any():
        null_columns = df.columns[df.isna().any()].tolist()
        raise ValueError(
            "Dashboard data contains missing values in: "
            + ", ".join(null_columns)
        )

    invalid_pressures = set(df["predicted_pressure"]) - EXPECTED_PRESSURES
    if invalid_pressures:
        raise ValueError(
            "Unexpected pressure levels: "
            + ", ".join(sorted(invalid_pressures))
        )

    group_sizes = df.groupby("forecast_origin_local", observed=True).size()
    invalid_groups = group_sizes[group_sizes != 3]
    if not invalid_groups.empty:
        raise ValueError(
            "Each forecast origin must contain exactly three horizons."
        )

    horizons_per_origin = (
        df.groupby("forecast_origin_local", observed=True)["horizon"]
        .apply(lambda values: set(values.dropna().astype(str)))
    )
    if not horizons_per_origin.map(lambda value: value == EXPECTED_HORIZONS).all():
        raise ValueError(
            "Each forecast origin must contain t+1, t+2, and t+3."
        )

    return (
        df.sort_values(["forecast_origin_local", "horizon"])
        .reset_index(drop=True)
    )
