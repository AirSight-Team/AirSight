from __future__ import annotations

import html
from textwrap import dedent

import pandas as pd
import streamlit as st

from src.dashboard_logic import OperationalOutlook, format_deviation


def _escape(value) -> str:
    return html.escape(str(value))


def _html(markup: str) -> None:
    """Render dedented HTML so Markdown never treats nested tags as code blocks."""
    st.markdown(dedent(markup).strip(), unsafe_allow_html=True)


def render_sidebar() -> None:
    """Render the AirSight branding and active Overview navigation."""
    with st.sidebar:
        st.markdown(
            """
            <div class="brand">
                <div class="brand-icon">✈</div>
                <div class="brand-text">AirSight</div>
            </div>

            <div class="nav-item active">
                <span class="nav-icon" aria-hidden="true">
                    <svg viewBox="0 0 24 24" width="18" height="18" fill="none">
                        <rect x="3.5" y="3.5" width="6.5" height="6.5" rx="1.4"
                              stroke="currentColor" stroke-width="1.8"/>
                        <rect x="14" y="3.5" width="6.5" height="6.5" rx="1.4"
                              stroke="currentColor" stroke-width="1.8"/>
                        <rect x="3.5" y="14" width="6.5" height="6.5" rx="1.4"
                              stroke="currentColor" stroke-width="1.8"/>
                        <rect x="14" y="14" width="6.5" height="6.5" rx="1.4"
                              stroke="currentColor" stroke-width="1.8"/>
                    </svg>
                </span>
                <span>Overview</span>
            </div>
            """,
            unsafe_allow_html=True,
        )


def render_header(selected_origin: pd.Timestamp) -> None:
    """Render the page heading and selected KSA forecast-start timestamp."""
    _html(
        f"""
        <div class="page-header">
            <div>
                <h1>Airport Operations Outlook</h1>
                <p>Next 3 hours · King Khalid International Airport (RUH)</p>
            </div>
            <div class="header-time">
                <div class="header-time-label"><span class="clock-icon">◷</span> KSA Time (UTC+3)</div>
                <div class="header-time-value">{selected_origin.strftime('%d %b %Y, %H:%M')}</div>
            </div>
        </div>
        """
    )


def render_start_time_selector(origins):
    """Render the interactive forecast-origin selector."""
    _html('<div class="selector-label">Forecast start time</div>')

    return st.selectbox(
        "Forecast start time",
        options=origins,
        index=len(origins) - 1,
        format_func=lambda value: value.strftime("%d %b %Y  ·  %H:%M KSA"),
        label_visibility="collapsed",
        key="forecast_origin",
    )


def render_forecast_card(row: pd.Series) -> None:
    """Render one dynamic forecast card."""
    pressure = str(row["predicted_pressure"])
    pressure_class = pressure.lower()

    target = row["target_hour_local"]
    horizon_number = int(str(row["horizon"]).split("+")[1])
    horizon_label = f"+{horizon_number} {'Hour' if horizon_number == 1 else 'Hours'}"

    movement_count = int(round(float(row["forecast_movements"])))
    deviation_text = format_deviation(row)
    recommendation = _escape(row["recommendation"])

    _html(
        f"""
        <div class="forecast-card {pressure_class}">
            <div class="card-top">
                <div>
                    <div class="horizon">{_escape(horizon_label)}</div>
                    <div class="target-time">{target.strftime('%H:%M')}</div>
                    <div class="target-date">{target.strftime('%a, %d %b')}</div>
                </div>
                <div class="pressure-badge {pressure_class}">{_escape(pressure)}</div>
            </div>
            <div class="movement-row">
                <div class="movement-icon">⌁</div>
                <div class="movement-number">{movement_count}</div>
                <div class="movement-label">Forecasted movements</div>
            </div>
            <div class="deviation {pressure_class}">- &nbsp;{_escape(deviation_text)}</div>
            <div class="card-divider"></div>
            <div class="recommendation-row">
                <div class="recommendation-icon {pressure_class}">▤</div>
                <div>
                    <div class="recommendation-title">Recommended Action</div>
                    <div class="recommendation-text">{recommendation}</div>
                </div>
            </div>
        </div>
        """
    )


def render_operational_outlook(outlook: OperationalOutlook) -> None:
    """Render the dynamic three-hour operational-readiness summary."""
    pressure_class = outlook.pressure.lower()
    _html(
        f"""
        <div class="outlook-panel">
            <div class="panel-title">Operational Outlook</div>
            <div class="outlook-headline {pressure_class}">{_escape(outlook.headline)}</div>
            <div class="outlook-detail">{_escape(outlook.detail)}</div>
        </div>
        """
    )


def _table_status(row: pd.Series) -> str:
    context = str(row["traffic_context"])
    deviation = float(row["forecast_vs_expected"])

    if context == "Typical":
        return "In line with typical traffic"

    magnitude = abs(deviation)
    formatted = f"{magnitude:.1f}".rstrip("0").rstrip(".")
    if deviation > 0:
        return f"About {formatted} movements above typical"
    return f"About {formatted} movements below typical"


def render_traffic_context(forecast_window: pd.DataFrame) -> None:
    """Render the forecast-versus-typical comparison table."""
    rows_html = []

    for _, row in forecast_window.iterrows():
        status_text = _table_status(row)
        context_class = str(row["traffic_context"]).lower().replace(" ", "-")
        rows_html.append(
            dedent(
                f"""
                <div class="context-row">
                    <div class="context-time">{row['target_hour_local'].strftime('%H:%M')}</div>
                    <div>Forecast {int(round(float(row['forecast_movements'])))}</div>
                    <div class="typical-value">Typical {float(row['expected_traffic']):.1f}</div>
                    <div class="context-status {context_class}">• {_escape(status_text)}</div>
                </div>
                """
            ).strip()
        )

    _html(
        f"""
        <div class="context-panel">
            <div class="panel-title">Traffic Context</div>
            <div class="panel-subtitle">How the forecast compares with typical traffic for the same hour and day</div>
            <div class="context-header">
                <div>Time</div><div>Forecast</div><div>Typical</div><div>Status</div>
            </div>
            {''.join(rows_html)}
        </div>
        """
    )


def render_pressure_legend() -> None:
    """Render the validated movement-based operational pressure thresholds."""
    _html(
        """
        <div class="legend-panel">
            <div class="panel-title">Operational Pressure Levels</div>
            <div class="panel-subtitle">Based on real traffic patterns, not a fixed rule</div>
            <div class="legend-row">
                <div class="legend-badge normal">Normal</div>
                <div class="legend-copy">≤21 movements/hour</div>
            </div>
            <div class="legend-row">
                <div class="legend-badge high">High</div>
                <div class="legend-copy">22–34 movements/hour</div>
            </div>
            <div class="legend-row">
                <div class="legend-badge extreme">Extreme</div>
                <div class="legend-copy">≥35 movements/hour</div>
            </div>
        </div>
        """
    )
