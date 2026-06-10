import streamlit as st
from turtle import st

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path

# =========================================================
# DC-Resource Competition Dashboard
# Uses geosentinel_dashboard_data.csv as the only data source.
# All dashboard scores are either direct CSV values or transparent
# calculations derived from CSV columns.
# =========================================================

st.set_page_config(
    page_title="DC-Resource",
    page_icon="🌐",
    layout="wide",
    initial_sidebar_state="expanded",
)

# -----------------------------
# Visual style: Raleway + clear competition palette
# -----------------------------
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Raleway:wght@400;500;600;700;800;900&display=swap');

    html, body, [class*="css"], .stApp, .stMarkdown, .stText, .stCaption,
    div, span, p, h1, h2, h3, h4, h5, h6, label, button {
        font-family: 'Raleway', sans-serif !important;
    }

    .stApp {
        background:
            radial-gradient(circle at 10% 0%, rgba(28, 91, 135, .62) 0, rgba(7, 17, 31, 0) 35%),
            linear-gradient(135deg, #07111f 0%, #0b1f34 48%, #06101e 100%);
        color: #f4f8ff;
    }

    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, rgba(5,18,34,.98), rgba(4,12,24,.98));
        border-right: 1px solid rgba(135, 205, 255, .20);
    }

    section[data-testid="stSidebar"] * { color: #f4f8ff; }

    .brand-card {
        padding: 18px 16px;
        border-radius: 22px;
        background: linear-gradient(160deg, rgba(49,143,202,.22), rgba(63,211,214,.10));
        border: 1px solid rgba(139, 213, 255, .22);
        margin-bottom: 18px;
    }

    .brand-title {
        font-size: 26px;
        font-weight: 900;
        letter-spacing: -0.03em;
        margin-bottom: 4px;
        color: #ffffff;
    }

    .brand-subtitle {
        color: #d7e8f8;
        font-size: 11.5px;
        line-height: 1.55;
    }

    .main-title {
        font-size: 34px;
        font-weight: 900;
        letter-spacing: -0.04em;
        color: #ffffff;
        margin-bottom: 3px;
    }

    .subtitle {
        color: #d1e3f4;
        font-size: 13px;
        margin-bottom: 16px;
        line-height: 1.5;
    }

    .badge {
        display: inline-block;
        padding: 9px 13px;
        border-radius: 999px;
        border: 1px solid rgba(72, 216, 232, .42);
        background: rgba(31, 151, 185, .16);
        color: #cfffff;
        font-size: 11px;
        font-weight: 800;
        margin-bottom: 10px;
    }

    .card {
        background: linear-gradient(180deg, rgba(255,255,255,.105), rgba(255,255,255,.060));
        border: 1px solid rgba(182,222,255,.18);
        border-radius: 24px;
        padding: 16px;
        box-shadow: 0 20px 60px rgba(0,0,0,.28);
        backdrop-filter: blur(14px);
        margin-bottom: 14px;
    }

    .kpi-card {
        background: linear-gradient(180deg, rgba(255,255,255,.120), rgba(255,255,255,.065));
        border: 1px solid rgba(182,222,255,.18);
        border-radius: 22px;
        padding: 15px;
        min-height: 112px;
    }

    .kpi-label {
        color: #d5e6f5;
        font-size: 10.8px;
        font-weight: 800;
        letter-spacing: .02em;
        text-transform: uppercase;
    }

    .kpi-value {
        font-size: 28px;
        font-weight: 900;
        line-height: 1.08;
        margin-top: 8px;
        color: #ffffff;
    }

    .kpi-note {
        color: #bcd0e4;
        font-size: 10.5px;
        margin-top: 7px;
        line-height: 1.35;
    }

    .section-title {
        font-size: 16px;
        font-weight: 900;
        color: #ffffff;
        margin-bottom: 4px;
        letter-spacing: -.01em;
    }

    .section-subtitle {
        color: #c7d9ea;
        font-size: 11.2px;
        line-height: 1.45;
        margin-bottom: 13px;
    }

    .cyan { color: #46e6ff; }
    .red { color: #ff6678; }
    .green { color: #60e49a; }
    .yellow { color: #ffe06a; }
    .orange { color: #ffad66; }

    .insight-box {
        display: grid;
        grid-template-columns: 48px 1fr;
        gap: 12px;
        align-items: start;
        background: rgba(255,255,255,.075);
        border: 1px solid rgba(182,222,255,.18);
        border-radius: 20px;
        padding: 14px;
    }

    .bot-icon {
        width: 48px;
        height: 48px;
        border-radius: 17px;
        background: linear-gradient(135deg, #2fe1ee, #316fff);
        display: grid;
        place-items: center;
        font-size: 24px;
        box-shadow: 0 0 24px rgba(47,225,238,.28);
    }

    .mini-text {
        color: #d7e8f8;
        font-size: 11.8px;
        line-height: 1.62;
    }

    div[data-testid="stMetric"] {
        background: rgba(255,255,255,.085);
        border: 1px solid rgba(182,222,255,.18);
        border-radius: 18px;
        padding: 13px;
    }

    div[data-testid="stMetric"] label {
        color: #d5e6f5 !important;
        font-size: 11px !important;
        font-weight: 800 !important;
    }

    div[data-testid="stMetricValue"] {
        color: #ffffff !important;
        font-size: 22px !important;
        font-weight: 900 !important;
    }

    .stDataFrame {
        border-radius: 16px;
        overflow: hidden;
    }

    .small-note {
        color: #c7d9ea;
        font-size: 10.5px;
        line-height: 1.55;
    }

    .recommendation-item {
        padding: 12px 13px;
        border-radius: 17px;
        background: rgba(255,255,255,.075);
        border: 1px solid rgba(182,222,255,.16);
        margin-bottom: 9px;
    }

    .recommendation-item b {
        color: #ffffff;
        font-size: 12px;
    }

    .recommendation-item p {
        color: #d4e4f3;
        font-size: 11px;
        margin: 6px 0 0 0;
        line-height: 1.55;
    }

    /* Make dataframe text readable on dark background */
    [data-testid="stDataFrame"] div { font-size: 11px !important; }
    </style>
    """,
    unsafe_allow_html=True,
)

# -----------------------------
# Data loading
# -----------------------------
DATA_PATH = Path("geosentinel_dashboard_data.csv")

REQUIRED_COLUMNS = [
    "data_center", "lat", "lon", "mean_LST_C", "mean_NDWI",
    "mean_soil_moisture", "lst_change", "ndwi_change",
    "soil_moisture_change", "ECI", "ESS", "risk_level"
]

@st.cache_data
def load_data(path: Path) -> pd.DataFrame:
    if not path.exists():
        st.error("The file geosentinel_dashboard_data.csv was not found. Please place it in the same folder as this dashboard file.")
        st.stop()

    data = pd.read_csv(path)
    missing = [col for col in REQUIRED_COLUMNS if col not in data.columns]
    if missing:
        st.error("Missing required CSV fields: " + ", ".join(missing))
        st.stop()

    for col in ["lat", "lon", "mean_LST_C", "mean_NDWI", "mean_soil_moisture", "lst_change", "ndwi_change", "soil_moisture_change", "ECI", "ESS"]:
        data[col] = pd.to_numeric(data[col], errors="coerce")

    data = data.dropna(subset=["lat", "lon", "ECI", "ESS"])
    data["Site Name"] = data["data_center"].astype(str).str.replace("_", " ", regex=False)
    data["Risk Classification"] = data["risk_level"].apply(clean_risk_label)
    data["Priority Score"] = compute_priority_score(data)
    data["Risk Outlook"] = data.apply(classify_outlook, axis=1)
    return data

# -----------------------------
# Helper functions
# -----------------------------
def clean_risk_label(value: str) -> str:
    text = str(value)
    if "(" in text:
        text = text.split("(")[0].strip()
    return text


def risk_color(value: str) -> str:
    text = str(value).lower()
    if "critical" in text or "red" in text:
        return "#ff6678"
    if "warning" in text or "yellow" in text:
        return "#ffe06a"
    if "safe" in text or "green" in text:
        return "#60e49a"
    return "#46e6ff"


def compute_priority_score(data: pd.DataFrame) -> pd.Series:
    # Transparent score derived only from CSV values.
    # ECI represents environmental change; ESS represents environmental stress.
    eci_rank = data["ECI"].rank(pct=True)
    ess_rank = data["ESS"].rank(pct=True)
    return ((eci_rank + ess_rank) / 2 * 100).round(1)


def classify_outlook(row: pd.Series) -> str:
    stress_signals = 0
    if row["lst_change"] > 0:
        stress_signals += 1
    if row["ndwi_change"] < 0:
        stress_signals += 1
    if row["soil_moisture_change"] < 0:
        stress_signals += 1

    if "Critical" in str(row["risk_level"]) or stress_signals >= 2:
        return "Increasing Attention Required"
    if stress_signals == 1:
        return "Continued Observation Required"
    return "Relatively Stable"


def evidence_points(row: pd.Series) -> list[str]:
    points = []
    if row["lst_change"] > 0:
        points.append(f"Surface temperature increased by {row['lst_change']:.2f} °C")
    elif row["lst_change"] < 0:
        points.append(f"Surface temperature decreased by {abs(row['lst_change']):.2f} °C")

    if row["ndwi_change"] < 0:
        points.append(f"Surface water availability decreased by {abs(row['ndwi_change']):.4f}")
    elif row["ndwi_change"] > 0:
        points.append(f"Surface water availability increased by {row['ndwi_change']:.4f}")

    if row["soil_moisture_change"] < 0:
        points.append(f"Soil water content decreased by {abs(row['soil_moisture_change']):.4f}")
    elif row["soil_moisture_change"] > 0:
        points.append(f"Soil water content increased by {row['soil_moisture_change']:.4f}")

    return points


def build_recommendations(row: pd.Series) -> list[tuple[str, str]]:
    recommendations = []
    if row["lst_change"] > 0:
        recommendations.append((
            "Heat Mitigation Planning",
            "Prioritize cooling-efficiency review, reflective surface planning, and landscape-based heat reduction around the selected site."
        ))
    if row["ndwi_change"] < 0:
        recommendations.append((
            "Water Resource Monitoring",
            "Monitor surface-water availability and review operational water demand during periods of increasing environmental pressure."
        ))
    if row["soil_moisture_change"] < 0:
        recommendations.append((
            "Soil Moisture Conservation",
            "Consider green-buffer maintenance and local land-cover interventions to support soil-water retention."
        ))
    if not recommendations:
        recommendations.append((
            "Routine Environmental Surveillance",
            "Maintain periodic satellite-based monitoring because current CSV indicators do not show multiple negative change signals."
        ))
    return recommendations


def display_table(df_in: pd.DataFrame, columns: list[str]):
    st.dataframe(
        df_in[columns],
        use_container_width=True,
        hide_index=True,
        height=min(440, 72 + len(df_in) * 38),
    )


def style_figure(fig):
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Raleway", color="#f4f8ff", size=11),
        margin=dict(l=0, r=0, t=18, b=0),
        legend=dict(font=dict(color="#f4f8ff", size=10)),
    )
    fig.update_xaxes(gridcolor="rgba(255,255,255,.10)", tickfont=dict(size=10, color="#d7e8f8"), title_font=dict(size=11))
    fig.update_yaxes(gridcolor="rgba(255,255,255,.10)", tickfont=dict(size=10, color="#d7e8f8"), title_font=dict(size=11))
    return fig


df = load_data(DATA_PATH)

# -----------------------------
# Sidebar
# -----------------------------
with st.sidebar:
    st.markdown(
        """
        <div class="brand-card">
            <div class="brand-title">DC-Resource</div>
            <div class="brand-subtitle">GeoAI-based environmental intelligence for sustainable data center development.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    page = st.radio(
        "Dashboard Navigation",
        [
            "Executive Overview",
            "Site Assessment",
            "Change Dynamics",
            "Predictive Outlook",
            "Resource Recommendations",
        ],
        label_visibility="collapsed",
    )
    st.markdown("---")
    st.markdown("**Data Basis**")
    st.caption("All indicators are read from geosentinel_dashboard_data.csv or calculated directly from its columns.")
    st.markdown("**Coverage**")
    st.caption(f"{len(df)} monitored data center sites")

# -----------------------------
# Header
# -----------------------------
st.markdown('<div class="badge">HACKATHON DEMO · GEOAI ENVIRONMENTAL INTELLIGENCE</div>', unsafe_allow_html=True)
st.markdown('<div class="main-title">DC-Resource Intelligence Platform</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="subtitle">A GeoAI dashboard for assessing environmental resource impacts around large-scale data centers using satellite-derived indicators.</div>',
    unsafe_allow_html=True,
)

critical_count = int(df["Risk Classification"].str.contains("Critical", case=False, na=False).sum())
warning_count = int(df["Risk Classification"].str.contains("Warning", case=False, na=False).sum())
safe_count = int(df["Risk Classification"].str.contains("Safe", case=False, na=False).sum())
top_priority = df.loc[df["Priority Score"].idxmax()]
top_eci = df.loc[df["ECI"].idxmax()]
top_ess = df.loc[df["ESS"].idxmax()]

# -----------------------------
# Executive Overview
# -----------------------------
if page == "Executive Overview":
    k1, k2, k3, k4 = st.columns(4)
    with k1:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">Monitored Sites</div>
            <div class="kpi-value cyan">{len(df)}</div>
            <div class="kpi-note">Data center locations in the CSV dataset</div>
        </div>
        """, unsafe_allow_html=True)
    with k2:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">Critical Risk Sites</div>
            <div class="kpi-value red">{critical_count}</div>
            <div class="kpi-note">Based on environmental risk classification</div>
        </div>
        """, unsafe_allow_html=True)
    with k3:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">Highest Change Index</div>
            <div class="kpi-value yellow">{top_eci['ECI']:.2f}</div>
            <div class="kpi-note">{top_eci['Site Name']}</div>
        </div>
        """, unsafe_allow_html=True)
    with k4:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">Highest Stress Score</div>
            <div class="kpi-value green">{top_ess['ESS']:.2f}</div>
            <div class="kpi-note">{top_ess['Site Name']}</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    left, right = st.columns([0.92, 1.08])

    # Swapped position: priority table first, map second.
    with left:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">Priority Environmental Risk Assessment</div>', unsafe_allow_html=True)
        st.markdown(
            '<div class="section-subtitle">Ranked assessment using Environmental Change Index and Environmental Stress Score from the CSV dataset.</div>',
            unsafe_allow_html=True,
        )
        rank_df = df.sort_values("Priority Score", ascending=False).copy()
        rank_show = rank_df[["Site Name", "Priority Score", "ECI", "ESS", "Risk Classification", "Risk Outlook"]].rename(columns={
            "Site Name": "Monitored Site",
            "Priority Score": "Priority Score",
            "ECI": "Environmental Change Index",
            "ESS": "Environmental Stress Score",
            "Risk Classification": "Risk Classification",
            "Risk Outlook": "Risk Outlook",
        })
        display_table(rank_show, rank_show.columns.tolist())
        st.markdown('</div>', unsafe_allow_html=True)

    with right:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">National Environmental Risk Distribution</div>', unsafe_allow_html=True)
        st.markdown(
            '<div class="section-subtitle">Spatial distribution of environmental stress and resource vulnerability surrounding monitored data center sites.</div>',
            unsafe_allow_html=True,
        )
        map_df = df.copy()
        fig_map = px.scatter_mapbox(
            map_df,
            lat="lat",
            lon="lon",
            color="Risk Classification",
            size="Priority Score",
            size_max=24,
            zoom=3,
            height=500,
            hover_name="Site Name",
            hover_data={
                "lat": False,
                "lon": False,
                "Priority Score": ":.1f",
                "ECI": ":.2f",
                "ESS": ":.2f",
                "Risk Classification": True,
            },
            color_discrete_map={
                "Critical": "#ff6678",
                "Warning": "#ffe06a",
                "Safe": "#60e49a",
            },
        )
        fig_map.update_layout(
            mapbox_style="carto-darkmatter",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(family="Raleway", color="#f4f8ff", size=11),
            margin=dict(l=0, r=0, t=0, b=0),
            legend_title_text="Risk Classification",
        )
        st.plotly_chart(fig_map, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    c1, c2 = st.columns([0.58, 0.42])
    with c1:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">Environmental Risk Classification Summary</div>', unsafe_allow_html=True)
        st.markdown('<div class="section-subtitle">Summary of classified risk levels across monitored sites.</div>', unsafe_allow_html=True)
        summary = pd.DataFrame({
            "Risk Classification": ["Critical", "Warning", "Safe"],
            "Number of Sites": [critical_count, warning_count, safe_count],
        })
        fig = px.bar(
            summary,
            x="Risk Classification",
            y="Number of Sites",
            color="Risk Classification",
            color_discrete_map={"Critical": "#ff6678", "Warning": "#ffe06a", "Safe": "#60e49a"},
            height=310,
            text="Number of Sites",
        )
        fig.update_traces(textposition="outside", textfont_color="#ffffff")
        st.plotly_chart(style_figure(fig), use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    with c2:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">Executive Interpretation</div>', unsafe_allow_html=True)
        st.markdown(
            f"""
            <div class="insight-box">
                <div class="bot-icon">🌐</div>
                <div class="mini-text">
                    <b>{top_priority['Site Name']}</b> currently has the highest combined priority score in this dataset.<br><br>
                    The assessment uses only satellite-derived environmental indicators available in the CSV file: environmental change, environmental stress, location, and risk classification.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.markdown('</div>', unsafe_allow_html=True)

# -----------------------------
# Site Assessment
# -----------------------------
elif page == "Site Assessment":
    selected_site = st.selectbox("Select Monitored Site", df["Site Name"].tolist())
    row = df[df["Site Name"] == selected_site].iloc[0]

    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown(f'<div class="section-title">Site-Level Environmental Assessment: {selected_site}</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-subtitle">Detailed environmental profile for the selected data center site.</div>', unsafe_allow_html=True)

    a, b, c, d = st.columns(4)
    a.metric("Risk Classification", row["Risk Classification"])
    b.metric("Environmental Change Index", f"{row['ECI']:.2f}")
    c.metric("Environmental Stress Score", f"{row['ESS']:.2f}")
    d.metric("Priority Score", f"{row['Priority Score']:.1f}")

    e, f, g = st.columns(3)
    e.metric("Land Surface Temperature", f"{row['mean_LST_C']:.2f} °C")
    f.metric("Surface Water Availability", f"{row['mean_NDWI']:.4f}")
    g.metric("Soil Water Content", f"{row['mean_soil_moisture']:.4f}")
    st.markdown('</div>', unsafe_allow_html=True)

    left, right = st.columns([0.58, 0.42])
    with left:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">Environmental Performance Metrics</div>', unsafe_allow_html=True)
        st.markdown('<div class="section-subtitle">Presentation-ready labels are used instead of raw CSV field names.</div>', unsafe_allow_html=True)
        indicator_df = pd.DataFrame({
            "Indicator": [
                "Land Surface Temperature",
                "Surface Water Availability",
                "Soil Water Content",
                "Temperature Change",
                "Water Availability Change",
                "Soil Water Change",
                "Environmental Change Index",
                "Environmental Stress Score",
            ],
            "Value": [
                row["mean_LST_C"], row["mean_NDWI"], row["mean_soil_moisture"],
                row["lst_change"], row["ndwi_change"], row["soil_moisture_change"],
                row["ECI"], row["ESS"],
            ],
        })
        fig = px.bar(indicator_df, x="Value", y="Indicator", orientation="h", color="Indicator", height=440)
        fig.update_layout(showlegend=False)
        st.plotly_chart(style_figure(fig), use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with right:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">GeoAI Analytical Interpretation</div>', unsafe_allow_html=True)
        points = evidence_points(row)
        point_html = "".join([f"<li>{p}</li>" for p in points]) if points else "<li>No major change signal is identified from the CSV fields.</li>"
        st.markdown(
            f"""
            <div class="insight-box">
                <div class="bot-icon">◈</div>
                <div class="mini-text">
                    <b>Risk Outlook:</b> {row['Risk Outlook']}<br>
                    <b>Evidence from CSV:</b>
                    <ul>{point_html}</ul>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.markdown('<p class="small-note">This interpretation is rule-based and uses only the environmental change indicators available in the CSV file.</p>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

# -----------------------------
# Change Dynamics
# -----------------------------
elif page == "Change Dynamics":
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Environmental Change Dynamics</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-subtitle">Comparison of observed change indicators across monitored sites.</div>', unsafe_allow_html=True)

    trend_df = df.sort_values("Priority Score", ascending=False).copy()
    fig = go.Figure()
    fig.add_trace(go.Bar(name="Temperature Change", x=trend_df["Site Name"], y=trend_df["lst_change"], marker_color="#ff6678"))
    fig.add_trace(go.Bar(name="Water Availability Change", x=trend_df["Site Name"], y=trend_df["ndwi_change"], marker_color="#46e6ff"))
    fig.add_trace(go.Bar(name="Soil Water Change", x=trend_df["Site Name"], y=trend_df["soil_moisture_change"], marker_color="#60e49a"))
    fig.update_layout(barmode="group", height=540, xaxis_tickangle=-25)
    st.plotly_chart(style_figure(fig), use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Indicator Comparison Table</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-subtitle">Formal labels are used for presentation clarity.</div>', unsafe_allow_html=True)
    table = trend_df[["Site Name", "lst_change", "ndwi_change", "soil_moisture_change", "Risk Classification"]].rename(columns={
        "Site Name": "Monitored Site",
        "lst_change": "Temperature Change",
        "ndwi_change": "Water Availability Change",
        "soil_moisture_change": "Soil Water Change",
        "Risk Classification": "Risk Classification",
    })
    display_table(table, table.columns.tolist())
    st.markdown('</div>', unsafe_allow_html=True)

# -----------------------------
# Predictive Outlook
# -----------------------------
elif page == "Predictive Outlook":
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Predictive Risk Outlook</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="section-subtitle">This page presents an evidence-based outlook derived from current CSV indicators. It does not introduce external or invented forecast values.</div>',
        unsafe_allow_html=True,
    )
    outlook_summary = df.groupby("Risk Outlook", as_index=False).agg(
        **{"Number of Sites": ("Site Name", "count"), "Average Priority Score": ("Priority Score", "mean")}
    )
    outlook_summary["Average Priority Score"] = outlook_summary["Average Priority Score"].round(1)
    fig = px.bar(
        outlook_summary,
        x="Risk Outlook",
        y="Number of Sites",
        color="Average Priority Score",
        color_continuous_scale=["#60e49a", "#ffe06a", "#ff6678"],
        height=360,
        text="Number of Sites",
    )
    fig.update_traces(textposition="outside", textfont_color="#ffffff")
    st.plotly_chart(style_figure(fig), use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

    left, right = st.columns([0.54, 0.46])
    with left:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">Priority Sites Requiring Forward Monitoring</div>', unsafe_allow_html=True)
        focus = df.sort_values("Priority Score", ascending=False).head(5)[["Site Name", "Priority Score", "Risk Classification", "Risk Outlook"]].rename(columns={
            "Site Name": "Monitored Site",
            "Priority Score": "Priority Score",
            "Risk Classification": "Risk Classification",
            "Risk Outlook": "Risk Outlook",
        })
        display_table(focus, focus.columns.tolist())
        st.markdown('</div>', unsafe_allow_html=True)
    with right:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">Outlook Interpretation Method</div>', unsafe_allow_html=True)
        st.markdown(
            """
            <div class="mini-text">
            <b>Increasing Attention Required</b><br>
            Assigned when the site is already classified as critical or when at least two negative environmental change signals are present.<br><br>
            <b>Continued Observation Required</b><br>
            Assigned when one negative environmental change signal is present.<br><br>
            <b>Relatively Stable</b><br>
            Assigned when the CSV change indicators do not show multiple negative signals.
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.markdown('</div>', unsafe_allow_html=True)

# -----------------------------
# Resource Recommendations
# -----------------------------
else:
    selected_site = st.selectbox("Select Site for Resource Management Guidance", df["Site Name"].tolist())
    row = df[df["Site Name"] == selected_site].iloc[0]

    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown(f'<div class="section-title">Strategic Resource Management Insights: {selected_site}</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-subtitle">Recommendations are selected from observed environmental change signals in the CSV dataset.</div>', unsafe_allow_html=True)

    a, b, c = st.columns(3)
    a.metric("Risk Classification", row["Risk Classification"])
    b.metric("Risk Outlook", row["Risk Outlook"])
    c.metric("Priority Score", f"{row['Priority Score']:.1f}")
    st.markdown('</div>', unsafe_allow_html=True)

    left, right = st.columns([0.52, 0.48])
    with left:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">Recommended Action Areas</div>', unsafe_allow_html=True)
        for title, description in build_recommendations(row):
            st.markdown(
                f"""
                <div class="recommendation-item">
                    <b>{title}</b>
                    <p>{description}</p>
                </div>
                """,
                unsafe_allow_html=True,
            )
        st.markdown('</div>', unsafe_allow_html=True)

    with right:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">Evidence Supporting Recommendation</div>', unsafe_allow_html=True)
        points = evidence_points(row)
        if points:
            for point in points:
                st.markdown(f"<div class='recommendation-item'><p>{point}</p></div>", unsafe_allow_html=True)
        else:
            st.markdown("<div class='recommendation-item'><p>No major negative change signal is identified from the CSV fields.</p></div>", unsafe_allow_html=True)
        st.markdown('<p class="small-note">No external forecast values or unverified impact estimates are added.</p>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
