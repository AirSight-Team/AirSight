from pathlib import Path

import streamlit as st

from src.components import (
    render_forecast_card,
    render_header,
    render_operational_outlook,
    render_pressure_legend,
    render_sidebar,
    render_start_time_selector,
    render_traffic_context,
)
from src.dashboard_logic import build_outlook, get_forecast_window
from src.data_loader import load_dashboard_data

BASE_DIR = Path(__file__).resolve().parent

st.set_page_config(
    page_title="AirSight",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="expanded",
)


def load_css() -> None:
    css_path = BASE_DIR / "assets" / "styles.css"
    st.markdown(f"<style>{css_path.read_text(encoding='utf-8')}</style>", unsafe_allow_html=True)


def main() -> None:
    load_css()
    dashboard_data = load_dashboard_data(BASE_DIR / "data" / "airsight_dashboard_data.csv")

    render_sidebar()

    origins = dashboard_data["forecast_origin_local"].drop_duplicates().tolist()
    header_slot = st.empty()
    selected_origin = render_start_time_selector(origins)
    with header_slot.container():
        render_header(selected_origin)

    forecast_window = get_forecast_window(dashboard_data, selected_origin)

    card_columns = st.columns(3, gap="medium")
    for column, (_, row) in zip(card_columns, forecast_window.iterrows()):
        with column:
            render_forecast_card(row)

    render_operational_outlook(build_outlook(forecast_window))

    lower_left, lower_right = st.columns([2.1, 1], gap="medium")
    with lower_left:
        render_traffic_context(forecast_window)
    with lower_right:
        render_pressure_legend()


if __name__ == "__main__":
    main()
