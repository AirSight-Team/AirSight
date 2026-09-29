from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

PRESSURE_RANK = {
    "Normal": 0,
    "High": 1,
    "Extreme": 2,
}


@dataclass(frozen=True)
class OperationalOutlook:
    """Text shown in the Operational Outlook panel."""

    headline: str
    detail: str
    pressure: str


def get_forecast_window(
    dashboard_data: pd.DataFrame,
    selected_origin,
) -> pd.DataFrame:
    """Return the t+1/t+2/t+3 rows for one selected forecast origin."""
    selected_origin = pd.Timestamp(selected_origin)

    window = dashboard_data[
        dashboard_data["forecast_origin_local"] == selected_origin
    ].copy()

    window = window.sort_values("horizon").reset_index(drop=True)

    if len(window) != 3:
        raise ValueError(
            f"Expected 3 forecast horizons for {selected_origin}, found {len(window)}."
        )

    return window


def build_outlook(forecast_window: pd.DataFrame) -> OperationalOutlook:
    """
    Summarize the three-hour pressure outlook.

    This is presentation logic only. It does not create operational decisions;
    the underlying readiness recommendations remain those produced by the
    integration pipeline.
    """
    rows = forecast_window.copy()
    rows["pressure_rank"] = rows["predicted_pressure"].map(PRESSURE_RANK)

    peak_pressure = rows.loc[rows["pressure_rank"].idxmax(), "predicted_pressure"]

    if peak_pressure == "Extreme":
        first = rows[rows["predicted_pressure"] == "Extreme"].iloc[0]
        hours_ahead = int(str(first["horizon"]).split("+")[1])
        target_time = first["target_hour_local"].strftime("%H:%M")

        return OperationalOutlook(
            headline=(
                f"Extreme pressure is expected within {hours_ahead} "
                f"{'hour' if hours_ahead == 1 else 'hours'}."
            ),
            detail=f"Prepare for increased coordination before {target_time}.",
            pressure="Extreme",
        )

    if peak_pressure == "High":
        first = rows[rows["predicted_pressure"] == "High"].iloc[0]
        hours_ahead = int(str(first["horizon"]).split("+")[1])
        target_time = first["target_hour_local"].strftime("%H:%M")

        return OperationalOutlook(
            headline=(
                f"High operational pressure is expected within {hours_ahead} "
                f"{'hour' if hours_ahead == 1 else 'hours'}."
            ),
            detail=f"Maintain enhanced readiness and monitoring before {target_time}.",
            pressure="High",
        )

    return OperationalOutlook(
        headline="Operational pressure is expected to remain normal over the next 3 hours.",
        detail="Maintain standard operational monitoring.",
        pressure="Normal",
    )


def format_deviation(row: pd.Series) -> str:
    """Create concise forecast-versus-typical text for a forecast card."""
    deviation = float(row["forecast_vs_expected"])

    if row["traffic_context"] == "Typical":
        return "In line with typical traffic for this time"

    magnitude = abs(deviation)
    formatted = f"{magnitude:.1f}".rstrip("0").rstrip(".")

    if deviation > 0:
        return f"{formatted} above typical traffic"

    return f"{formatted} below typical traffic"


def pressure_css_class(pressure: str) -> str:
    """Return the CSS suffix used for pressure-aware styling."""
    return pressure.strip().lower()
