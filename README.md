# AirSight

**Short-Term Airport Traffic Forecasting & Operational Decision Support**

AirSight is a data-driven decision-support system developed to forecast scheduled flight traffic at **King Khalid International Airport (RUH)** for the next three hours.

The system combines time-series forecasting with operational pressure analysis to transform traffic predictions into clear, interpretable insights through an interactive dashboard.

## Overview

AirSight forecasts scheduled aircraft movements for the next **1, 2, and 3 hours**, then translates these forecasts into operational pressure levels and compares them with historical traffic patterns.

The complete pipeline is:

**Traffic Forecasting → Operational Pressure → Historical Context → Readiness Recommendations → Interactive Dashboard**

## Methodology

### Traffic Forecasting

Three forecasting approaches were evaluated:

- XGBoost
- LSTM
- GRU

The **Residual LSTM** achieved the best overall performance. It uses the traffic from the same hour one week earlier as a reference and learns the expected deviation from that recurring weekly pattern.

### Operational Pressure

K-Means clustering was used to identify patterns in historical airport activity. These patterns were then translated into three interpretable pressure levels:

| Pressure Level | Scheduled Movements |
|---|---:|
| Normal | ≤ 21 movements/hour |
| High | 22–34 movements/hour |
| Extreme | ≥ 35 movements/hour |

These are data-derived activity levels and are not official airport capacity thresholds.

### Historical Context

Each forecast is compared with historically expected traffic for the same day of the week and hour of the day and classified as:

- Below Typical
- Typical
- Above Typical

This adds context to the predicted pressure by showing whether the expected activity is unusual for that specific time.

## Model Performance

| Model | MAE | RMSE | sMAPE |
|---|---:|---:|---:|
| XGBoost | 1.79 | 2.63 | 6.46% |
| **Residual LSTM** | **1.15** | **1.53** | **3.93%** |
| GRU | 2.27 | 3.08 | 8.16% |

The final pressure layer achieved approximately **90% classification accuracy** across the three forecast horizons, with **over 98% High/Extreme detection** at each horizon.

## Interactive Dashboard

AirSight includes an interactive **Streamlit dashboard** for exploring:

- Three-hour traffic forecasts
- Operational pressure levels
- Historical traffic context
- Readiness recommendations
- Operational outlook

The system is designed for **decision support** and does not make direct operational decisions such as flight delays, cancellations, gate assignments, or staffing decisions.

For dashboard implementation and setup instructions, see [`dashboard/README.md`](dashboard/README.md).

## Repository Structure

```text
AirSight/
├── AieSight_dataset.ipynb
├── AirSight_Data_Split.ipynb
├── AirSight_XGBoost_Model.ipynb
├── LSTM.ipynb
├── AirSight_GRU_Model.ipynb
├── Clustering_Operational_Pressure.ipynb
├── AirSight_Integration.ipynb
├── dashboard/
│   ├── app.py
│   ├── README.md
│   ├── requirements.txt
│   ├── assets/
│   ├── data/
│   ├── results/
│   └── src/
├── .gitignore
└── README.md
