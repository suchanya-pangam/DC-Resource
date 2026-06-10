import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path

# =========================================================
# DC-Resource Dashboard
# All dashboard values are calculated from geosentinel_dashboard_data.csv only.
# =========================================================

st.set_page_config(
    page_title="DC-Resource",
    page_icon="🌐",
    layout="wide",
    initial_sidebar_state="expanded",
)

# -----------------------------
# Premium dark visual style
# -----------------------------
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Gelasio:wght@400;500;600;700&display=swap');

    html, body, [class*="css"], .stApp, .stMarkdown, .stText, .stCaption, div, span, p, h1, h2, h3, h4, h5, h6 {
        font-family: 'Gelasio', serif !important;
    }

    .stApp {
        background: radial-gradient(circle at top left, #12345a 0, #07111f 42%, #040914 100%);
        color: #edf6ff;
    }

    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, rgba(7,17,31,.98), rgba(4,9,20,.98));
        border-right: 1px solid rgba(255,255,255,.12);
    }

    section[data-testid="stSidebar"] * { color: #edf6ff; }

    .brand-block {
        padding: 18px 14px;
        border-radius: 22px;
        background: linear-gradient(160deg, rgba(32,224,255,.14), rgba(138,92,255,.12));
        border: 1px solid rgba(255,255,255,.12);
        margin-bottom: 22px;
    }

    .brand-title {
        font-size: 28px;
        font-weight: 700;
        letter-spacing: -0.03em;
        margin-bottom: 2px;
    }

    .brand-subtitle {
        color: #b8c9dc;
        font-size: 12px;
        line-height: 1.5;
    }

    .main-title {
        font-size: 38px;
        font-weight: 700;
        letter-spacing: -0.04em;
        margin-bottom: 4px;
    }

    .subtitle {
        color: #8fa8c4;
        font-size: 15px;
        margin-bottom: 18px;
    }

    .badge {
        display: inline-block;
        padding: 10px 14px;
        border-radius: 999px;
        border: 1px solid rgba(32,224,255,.35);
        background: rgba(32,224,255,.08);
        color: #bff7ff;
        font-size: 12px;
        font-weight: 700;
        margin-bottom: 12px;
    }

    .card {
        background: linear-gradient(180deg, rgba(255,255,255,.075), rgba(255,255,255,.045));
        border: 1px solid rgba(255,255,255,.12);
        border-radius: 26px;
        padding: 18px;
        box-shadow: 0 24px 70px rgba(0,0,0,.28);
        backdrop-filter: blur(16px);
        margin-bottom: 16px;
    }

    .kpi-card {
        background: rgba(255,255,255,.07);
        border: 1px solid rgba(255,255,255,.12);
        border-radius: 22px;
        padding: 18px;
        min-height: 130px;
    }

    .kpi-label {
        color: #8fa8c4;
        font-size: 12px;
        font-weight: 700;
    }

    .kpi-value {
        font-size: 34px;
        font-weight: 700;
        line-height: 1.1;
        margin-top: 8px;
    }

    .kpi-note {
        color: #9fb4ca;
        font-size: 12px;
        margin-top: 8px;
    }

    .cyan { color: #20e0ff; }
    .red { color: #ff425b; }
    .green { color: #42d67b; }
    .yellow { color: #ffd24a; }
    .orange { color: #ff8a3c; }

    .section-title {
        font-size: 20px;
        font-weight: 700;
        margin-bottom: 4px;
    }

    .section-subtitle {
        color: #8fa8c4;
        font-size: 13px;
        margin-bottom: 16px;
    }

    .insight-box {
        display: grid;
        grid-template-columns: 56px 1fr;
        gap: 14px;
        align-items: start;
        background: rgba(255,255,255,.06);
        border: 1px solid rgba(255,255,255,.12);
        border-radius: 22px;
        padding: 18px;
    }

    .bot-icon {
        width: 56px;
        height: 56px;
        border-radius: 20px;
        background: linear-gradient(135deg, #20e0ff, #3279ff);
        display: grid;
        place-items: center;
        font-size: 27px;
        box-shadow: 0 0 28px rgba(32,224,255,.35);
    }

    .mini-text {
        color: #bfd0e4;
        font-size: 13px;
        line-height: 1.7;
    }

    div[data-testid="stMetric"] {
        background: rgba(255,255,255,.07);
        border: 1px solid rgba(255,255,255,.12);
        border-radius: 20px;
        padding: 16px;
    }

    div[data-testid="stMetric"] label {
        color: #8fa8c4 !important;
        font-weight: 700;
    }

    div[data-testid="stMetricValue"] {
        color: #edf6ff !important;
        font-weight: 700;
    }

    .stDataFrame {
        border-radius: 18px;
        overflow: hidden;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# -----------------------------
# Load source data
# -----------------------------
DATA_PATH = Path("geosentinel_dashboard_data.csv")

REQUIRED_COLUMNS = [
    "data_center", "lat", "lon", "mean_LST_C", "mean_NDWI",
    "mean_soil_moisture", "lst_change", "ndwi_change",
    "soil_moisture_change", "ECI", "ESS", "risk_level"
]

DISPLAY_NAMES = {
    "data_center": "Data Center Site",
    "lat": "Latitude",
    "lon": "Longitude",
    "mean_LST_C": "Land Surface Temperature (°C)",
    "mean_NDWI": "Surface Water Availability Index",
    "mean_soil_moisture": "Soil Water Content",
    "lst_change": "Temperature Change",
    "ndwi_change": "Water Availability Change",
    "soil_moisture_change": "Soil Moisture Change",
    "ECI": "Environmental Change Index",
    "ESS": "Environmental Stress Score",
    "risk_level": "Environmental Risk Classification",
}

@st.cache_data
def load_data(path: Path) -> pd.DataFrame:
    if not path.exists():
        st.error("Source dataset not found. Please place geosentinel_dashboard_data.csv in the same folder as this app file.")
        st.stop()

    data = pd.read_csv(path)
    missing = [col for col in REQUIRED_COLUMNS if col not in data.columns]
    if missing:
        st.error("The source dataset is missing required fields for the dashboard analysis.")
        st.stop()

    return data


df = load_data(DATA_PATH)

# -----------------------------
# Helper functions
# -----------------------------
def risk_class(level: str) -> str:
    text = str(level).strip()
    if "(" in text:
        text = text.split("(")[0].strip()
    return text


def risk_color(level: str) -> str:
    text = str(level).lower()
    if "critical" in text:
        return "#ff425b"
    if "warning" in text:
        return "#ffd24a"
    if "safe" in text:
        return "#42d67b"
    return "#20e0ff"


def evidence_summary(row: pd.Series) -> list[str]:
    evidence = []

    if row["lst_change"] > 0:
        evidence.append(f"Land surface temperature increased by {row['lst_change']:.2f} °C")
    elif row["lst_change"] < 0:
        evidence.append(f"Land surface temperature decreased by {abs(row['lst_change']):.2f} °C")

    if row["ndwi_change"] < 0:
        evidence.append(f"Surface water availability decreased by {abs(row['ndwi_change']):.4f}")
    elif row["ndwi_change"] > 0:
        evidence.append(f"Surface water availability increased by {row['ndwi_change']:.4f}")

    if row["soil_moisture_change"] < 0:
        evidence.append(f"Soil water content decreased by {abs(row['soil_moisture_change']):.4f}")
    elif row["soil_moisture_change"] > 0:
        evidence.append(f"Soil water content increased by {row['soil_moisture_change']:.4f}")

    return evidence


def display_table(data: pd.DataFrame) -> pd.DataFrame:
    return data.rename(columns=DISPLAY_NAMES)

# -----------------------------
# Sidebar
# -----------------------------
with st.sidebar:
    st.markdown(
        """
        <div class="brand-block">
            <div class="brand-title">DC-Resource</div>
            <div class="brand-subtitle">GeoAI-Based Environmental Intelligence for Sustainable Data Center Development</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    page = st.radio(
        "Navigation",
        [
            "Overview",
            "Site Assessment",
            "Environmental Dynamics",
            "Source Dataset",
        ],
        label_visibility="collapsed",
    )
    st.markdown("---")
    st.markdown("**Dataset Status**")
    st.caption("Dashboard values are calculated from the uploaded CSV dataset only.")
    st.markdown("**Monitored Sites**")
    st.caption(f"{len(df)} data center sites")

# -----------------------------
# Global header
# -----------------------------
st.markdown('<div class="badge">LIVE DEMO · GeoAI Hackathon Prototype</div>', unsafe_allow_html=True)
st.markdown('<div class="main-title">DC-Resource Intelligence Platform</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="subtitle">A GeoAI framework for monitoring environmental resource impacts of large-scale data centers</div>',
    unsafe_allow_html=True,
)

# -----------------------------
# Overview
# -----------------------------
if page == "Overview":
    critical_count = int(df["risk_level"].astype(str).str.contains("Critical", case=False, na=False).sum())
    warning_count = int(df["risk_level"].astype(str).str.contains("Warning", case=False, na=False).sum())
    stable_count = int(df["risk_level"].astype(str).str.contains("Safe", case=False, na=False).sum())

    top_eci = df.loc[df["ECI"].idxmax()]
    top_ess = df.loc[df["ESS"].idxmax()]

    k1, k2, k3, k4 = st.columns(4)
    with k1:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">Monitored Data Center Sites</div>
            <div class="kpi-value cyan">{len(df)}</div>
            <div class="kpi-note">Sites available in the source dataset</div>
        </div>
        """, unsafe_allow_html=True)
    with k2:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">Critical Environmental Sites</div>
            <div class="kpi-value red">{critical_count}</div>
            <div class="kpi-note">Sites classified as critical risk</div>
        </div>
        """, unsafe_allow_html=True)
    with k3:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">Maximum Environmental Change</div>
            <div class="kpi-value yellow">{top_eci['ECI']:.2f}</div>
            <div class="kpi-note">{top_eci['data_center']}</div>
        </div>
        """, unsafe_allow_html=True)
    with k4:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">Maximum Environmental Stress</div>
            <div class="kpi-value green">{top_ess['ESS']:.2f}</div>
            <div class="kpi-note">{top_ess['data_center']}</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    left, right = st.columns([1.35, 0.65])

    with left:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">National Environmental Risk Distribution</div>', unsafe_allow_html=True)
        st.markdown(
            '<div class="section-subtitle">Spatial distribution of environmental stress and resource vulnerability surrounding monitored data center sites.</div>',
            unsafe_allow_html=True,
        )

        map_df = df.copy()
        map_df["Risk Classification"] = map_df["risk_level"].apply(risk_class)
        map_df["Land Surface Temperature (°C)"] = map_df["mean_LST_C"]
        map_df["Surface Water Availability Index"] = map_df["mean_NDWI"]
        map_df["Soil Water Content"] = map_df["mean_soil_moisture"]
        map_df["Environmental Change Index"] = map_df["ECI"]
        map_df["Environmental Stress Score"] = map_df["ESS"]

        fig_map = px.scatter_mapbox(
            map_df,
            lat="lat",
            lon="lon",
            color="Risk Classification",
            size="Environmental Change Index",
            size_max=22,
            zoom=3,
            height=520,
            hover_name="data_center",
            hover_data={
                "lat": False,
                "lon": False,
                "Land Surface Temperature (°C)": ":.2f",
                "Surface Water Availability Index": ":.4f",
                "Soil Water Content": ":.4f",
                "Environmental Change Index": ":.2f",
                "Environmental Stress Score": ":.2f",
                "Risk Classification": False,
            },
            color_discrete_map={
                "Critical": "#ff425b",
                "Warning": "#ffd24a",
                "Safe": "#42d67b",
            },
        )
        fig_map.update_layout(
            mapbox_style="carto-darkmatter",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#edf6ff", family="Gelasio"),
            margin=dict(l=0, r=0, t=0, b=0),
            legend_title_text="Risk Classification",
        )
        st.plotly_chart(fig_map, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with right:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">Priority Environmental Risk Assessment</div>', unsafe_allow_html=True)
        st.markdown('<div class="section-subtitle">Ranked by environmental change intensity from the source dataset.</div>', unsafe_allow_html=True)
        rank_df = df.sort_values("ECI", ascending=False)[["data_center", "ECI", "ESS", "risk_level"]].copy()
        rank_df.insert(0, "Priority", range(1, len(rank_df) + 1))
        rank_df["risk_level"] = rank_df["risk_level"].apply(risk_class)
        st.dataframe(display_table(rank_df), use_container_width=True, hide_index=True)
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">Risk Classification Overview</div>', unsafe_allow_html=True)
        st.markdown('<div class="section-subtitle">Summary of environmental risk classes across all monitored sites.</div>', unsafe_allow_html=True)
        summary = pd.DataFrame({
            "Risk Classification": ["Critical", "Warning", "Safe"],
            "Number of Sites": [critical_count, warning_count, stable_count],
        })
        fig_bar = px.bar(
            summary,
            x="Risk Classification",
            y="Number of Sites",
            color="Risk Classification",
            color_discrete_map={"Critical": "#ff425b", "Warning": "#ffd24a", "Safe": "#42d67b"},
            height=260,
        )
        fig_bar.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#edf6ff", family="Gelasio"),
            margin=dict(l=0, r=0, t=10, b=0),
            showlegend=False,
        )
        st.plotly_chart(fig_bar, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

# -----------------------------
# Site assessment
# -----------------------------
elif page == "Site Assessment":
    selected_site = st.selectbox("Select Data Center Site", df["data_center"].tolist())
    row = df[df["data_center"] == selected_site].iloc[0]

    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown(f'<div class="section-title">Site-Level Environmental Assessment: {selected_site}</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-subtitle">Environmental status and site-level metrics derived from the selected record in the source dataset.</div>', unsafe_allow_html=True)

    a, b, c, d = st.columns(4)
    a.metric("Risk Classification", risk_class(row["risk_level"]))
    b.metric("Environmental Change Index", f"{row['ECI']:.2f}")
    c.metric("Environmental Stress Score", f"{row['ESS']:.2f}")
    d.metric("Land Surface Temperature", f"{row['mean_LST_C']:.2f} °C")

    e, f, g = st.columns(3)
    e.metric("Surface Water Availability", f"{row['mean_NDWI']:.4f}")
    f.metric("Soil Water Content", f"{row['mean_soil_moisture']:.4f}")
    g.metric("Site Coordinates", f"{row['lat']:.3f}, {row['lon']:.3f}")
    st.markdown('</div>', unsafe_allow_html=True)

    col1, col2 = st.columns([0.58, 0.42])
    with col1:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">Environmental Performance Metrics</div>', unsafe_allow_html=True)
        st.markdown('<div class="section-subtitle">Indicator values from the selected site record.</div>', unsafe_allow_html=True)
        indicator_df = pd.DataFrame({
            "Environmental Metric": [
                "Land Surface Temperature",
                "Surface Water Availability",
                "Soil Water Content",
                "Temperature Change",
                "Water Availability Change",
                "Soil Moisture Change",
                "Environmental Change Index",
                "Environmental Stress Score",
            ],
            "Value": [
                row["mean_LST_C"],
                row["mean_NDWI"],
                row["mean_soil_moisture"],
                row["lst_change"],
                row["ndwi_change"],
                row["soil_moisture_change"],
                row["ECI"],
                row["ESS"],
            ],
        })
        fig_metric = px.bar(indicator_df, x="Environmental Metric", y="Value", color="Environmental Metric", height=430)
        fig_metric.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#edf6ff", family="Gelasio"),
            margin=dict(l=0, r=0, t=10, b=0),
            showlegend=False,
            xaxis_tickangle=-30,
        )
        st.plotly_chart(fig_metric, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">GeoAI Evidence Summary</div>', unsafe_allow_html=True)
        evidence = evidence_summary(row)
        evidence_text = "<br>".join([f"• {item}" for item in evidence]) if evidence else "No major directional change is available from the source record."
        st.markdown(
            f"""
            <div class="insight-box">
                <div class="bot-icon">⌁</div>
                <div>
                    <b>{selected_site}</b><br>
                    <div class="mini-text">
                    Environmental risk classification: <b>{risk_class(row['risk_level'])}</b><br><br>
                    Evidence from source data:<br>{evidence_text}
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.caption("This explanation is rule-based and uses only directional changes available in the source dataset.")
        st.markdown('</div>', unsafe_allow_html=True)

# -----------------------------
# Environmental dynamics
# -----------------------------
elif page == "Environmental Dynamics":
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Environmental Change Dynamics</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-subtitle">Comparison of temperature, water availability, and soil moisture changes across monitored data center sites.</div>', unsafe_allow_html=True)

    trend_df = df[["data_center", "lst_change", "ndwi_change", "soil_moisture_change"]].rename(columns={
        "data_center": "Data Center Site",
        "lst_change": "Temperature Change",
        "ndwi_change": "Water Availability Change",
        "soil_moisture_change": "Soil Moisture Change",
    })

    fig_trend = go.Figure()
    fig_trend.add_trace(go.Bar(name="Temperature Change", x=trend_df["Data Center Site"], y=trend_df["Temperature Change"], marker_color="#ff425b"))
    fig_trend.add_trace(go.Bar(name="Water Availability Change", x=trend_df["Data Center Site"], y=trend_df["Water Availability Change"], marker_color="#20e0ff"))
    fig_trend.add_trace(go.Bar(name="Soil Moisture Change", x=trend_df["Data Center Site"], y=trend_df["Soil Moisture Change"], marker_color="#42d67b"))
    fig_trend.update_layout(
        barmode="group",
        height=520,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#edf6ff", family="Gelasio"),
        margin=dict(l=0, r=0, t=20, b=0),
        xaxis_tickangle=-35,
    )
    st.plotly_chart(fig_trend, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Strategic Resource Management Insights</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-subtitle">Priority observations based on the strongest environmental change values in the source dataset.</div>', unsafe_allow_html=True)
    for _, r in df.sort_values("ECI", ascending=False).head(5).iterrows():
        evidence = "; ".join(evidence_summary(r))
        st.markdown(
            f"**{r['data_center']}** — Risk Classification: `{risk_class(r['risk_level'])}` · "
            f"Environmental Change Index: `{r['ECI']:.2f}` · Environmental Stress Score: `{r['ESS']:.2f}`"
        )
        st.caption(evidence if evidence else "No directional change evidence is available for this site.")
    st.markdown('</div>', unsafe_allow_html=True)

# -----------------------------
# Source dataset
# -----------------------------
else:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Source Dataset</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-subtitle">Renamed field view of the dataset used by this dashboard.</div>', unsafe_allow_html=True)
    source_view = df.copy()
    source_view["risk_level"] = source_view["risk_level"].apply(risk_class)
    st.dataframe(display_table(source_view), use_container_width=True, hide_index=True)
    st.download_button(
        "Download Source Dataset",
        df.to_csv(index=False).encode("utf-8"),
        file_name="geosentinel_dashboard_data.csv",
        mime="text/csv",
    )
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown(
    '<div style="text-align:center;color:#9fb4ca;font-size:12px;margin-top:12px;">DC-Resource · All dashboard values are calculated from the CSV dataset only.</div>',
    unsafe_allow_html=True,
)