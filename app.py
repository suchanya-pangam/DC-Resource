import streamlit as st
import pandas as pd
import plotly.express as px

# --------------------
# Page Config
# --------------------
st.set_page_config(
    page_title="GeoSentinel AI",
    page_icon="🌍",
    layout="wide"
)

# --------------------
# Load Data
# --------------------
df = pd.read_csv("geosentinel_dashboard_data.csv")

# --------------------
# Title
# --------------------
st.title("🌍 GeoSentinel AI")
st.caption("Satellite-Powered Environmental Early Warning System for Data Centers")

# --------------------
# KPI Section
# --------------------
col1, col2, col3, col4 = st.columns(4)

col1.metric(
    "Monitored Data Centers",
    len(df)
)

col2.metric(
    "Average ECI",
    round(df["ECI"].mean(), 2)
)

col3.metric(
    "Average ESS",
    round(df["ESS"].mean(), 2)
)

col4.metric(
    "Critical Sites",
    len(df[df["risk_level"] == "Critical"])
)

st.divider()

# --------------------
# Risk Map
# --------------------
st.subheader("🗺 Risk Map")

fig = px.scatter_mapbox(
    df,
    lat="lat",
    lon="lon",
    color="risk_level",
    hover_name="data_center",
    hover_data=["ECI", "ESS"],
    zoom=3,
    height=500
)

fig.update_layout(
    mapbox_style="carto-darkmatter",
    margin=dict(l=0, r=0, t=0, b=0)
)

st.plotly_chart(fig, use_container_width=True)

# --------------------
# Ranking
# --------------------
left, right = st.columns(2)

with left:
    st.subheader("🔥 Top ECI")
    st.dataframe(
        df.sort_values(
            "ECI",
            ascending=False
        )[
            ["data_center", "ECI", "risk_level"]
        ],
        use_container_width=True
    )

with right:
    st.subheader("⚠ Top ESS")
    st.dataframe(
        df.sort_values(
            "ESS",
            ascending=False
        )[
            ["data_center", "ESS", "risk_level"]
        ],
        use_container_width=True
    )

st.divider()

# --------------------
# Hotspot Detail
# --------------------
st.subheader("📍 Hotspot Detail")

selected_dc = st.selectbox(
    "Select Data Center",
    df["data_center"]
)

row = df[df["data_center"] == selected_dc].iloc[0]

c1, c2, c3 = st.columns(3)

c1.metric(
    "LST (°C)",
    round(row["mean_LST_C"], 2)
)

c2.metric(
    "NDWI",
    round(row["mean_NDWI"], 3)
)

c3.metric(
    "Soil Moisture",
    round(row["mean_soil_moisture"], 3)
)

c4, c5, c6 = st.columns(3)

c4.metric(
    "ECI",
    round(row["ECI"], 2)
)

c5.metric(
    "ESS",
    round(row["ESS"], 2)
)

c6.metric(
    "Risk Level",
    row["risk_level"]
)

st.divider()

# --------------------
# AI Insight
# --------------------
st.subheader("🤖 AI Insight")

if row["risk_level"] == "Critical":
    st.error(
        f"{selected_dc} shows significant environmental stress. "
        "Recommend immediate monitoring."
    )

elif row["risk_level"] == "Concern":
    st.warning(
        f"{selected_dc} should be monitored closely."
    )

else:
    st.success(
        f"{selected_dc} currently shows relatively stable conditions."
    )