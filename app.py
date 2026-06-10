import os
from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# =========================================================
# DC-Resource Intelligence Platform
# New file: dc_resource_dashboard.py
# Run: python -m streamlit run dc_resource_dashboard.py
# =========================================================

st.set_page_config(
    page_title="DC-Resource Intelligence Platform",
    page_icon="🌐",
    layout="wide",
    initial_sidebar_state="expanded",
)

# -----------------------------
# Global Style: clone dashboard layout
# -----------------------------
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

    html, body, [class*="css"], .stApp {
        font-family: 'Inter', sans-serif;
        background: #F4F7FB;
        color: #0F172A;
    }

    .block-container {
        padding-top: 1.05rem !important;
        padding-left: 1.15rem !important;
        padding-right: 1.15rem !important;
        padding-bottom: 1.2rem !important;
        max-width: 100% !important;
    }

    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #071A36 0%, #0B2447 100%);
        min-width: 250px !important;
        max-width: 250px !important;
    }

    [data-testid="stSidebar"] * {
        color: #EAF2FF !important;
    }

    [data-testid="stSidebar"] .stButton > button {
        width: 100%;
        height: 42px;
        border-radius: 12px;
        background: transparent;
        border: 1px solid rgba(255,255,255,0.08);
        color: #DCEBFF !important;
        text-align: left;
        padding-left: 14px;
        font-weight: 600;
    }

    [data-testid="stSidebar"] .stButton > button:hover {
        background: #2563EB;
        border-color: #2563EB;
        color: white !important;
    }

    [data-testid="stSidebar"] .stSelectbox, [data-testid="stSidebar"] .stMultiSelect {
        background: transparent !important;
    }

    div[data-testid="stVerticalBlock"] { gap: 0.75rem; }
    div[data-testid="stHorizontalBlock"] { gap: 0.9rem; align-items: stretch; }

    .top-header {
        background: #FFFFFF;
        border: 1px solid #E5EAF2;
        border-radius: 22px;
        padding: 18px 22px;
        box-shadow: 0 12px 32px rgba(15, 23, 42, 0.06);
    }

    .title-main {
        margin: 0;
        font-size: 30px;
        line-height: 1.15;
        font-weight: 800;
        color: #0B1220;
        letter-spacing: -0.02em;
    }

    .title-sub {
        margin-top: 6px;
        font-size: 13px;
        color: #64748B;
        font-weight: 500;
    }

    .mini-pill {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        height: 30px;
        padding: 0 12px;
        border-radius: 999px;
        background: #EFF6FF;
        color: #2563EB;
        font-size: 12px;
        font-weight: 800;
        border: 1px solid #DBEAFE;
        white-space: nowrap;
    }

    .card {
        background: #FFFFFF;
        border: 1px solid #E5EAF2;
        border-radius: 20px;
        padding: 16px 17px;
        box-shadow: 0 12px 32px rgba(15, 23, 42, 0.06);
        height: 100%;
    }

    .metric-card {
        background: #FFFFFF;
        border: 1px solid #E5EAF2;
        border-radius: 18px;
        padding: 15px 16px;
        box-shadow: 0 12px 32px rgba(15, 23, 42, 0.06);
        min-height: 112px;
    }

    .metric-row {
        display: flex;
        justify-content: space-between;
        gap: 12px;
        align-items: flex-start;
    }

    .metric-title {
        font-size: 12px;
        color: #64748B;
        font-weight: 800;
        text-transform: uppercase;
        letter-spacing: 0.03em;
        margin-bottom: 7px;
    }

    .metric-value {
        font-size: 29px;
        line-height: 1.05;
        color: #0F172A;
        font-weight: 800;
        letter-spacing: -0.03em;
    }

    .metric-subtitle {
        font-size: 12px;
        color: #94A3B8;
        margin-top: 8px;
        font-weight: 600;
    }

    .metric-icon {
        width: 42px;
        height: 42px;
        border-radius: 15px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 20px;
        background: #EFF6FF;
        color: #2563EB;
    }

    .section-title {
        font-size: 16px;
        font-weight: 800;
        color: #0F172A;
        margin-bottom: 4px;
        letter-spacing: -0.01em;
    }

    .section-subtitle {
        font-size: 12px;
        color: #64748B;
        margin-bottom: 10px;
        font-weight: 600;
    }

    .detail-title {
        font-size: 20px;
        font-weight: 800;
        color: #0F172A;
        margin-bottom: 2px;
    }

    .detail-subtitle {
        font-size: 12px;
        color: #64748B;
        font-weight: 700;
        margin-bottom: 14px;
    }

    .score-box {
        background: #F8FAFC;
        border: 1px solid #E5EAF2;
        border-radius: 16px;
        padding: 14px;
        min-height: 96px;
    }

    .score-label {
        font-size: 11px;
        color: #64748B;
        font-weight: 800;
        text-transform: uppercase;
        letter-spacing: 0.04em;
    }

    .score-value {
        font-size: 25px;
        line-height: 1.05;
        font-weight: 800;
        color: #0F172A;
        margin-top: 7px;
    }

    .badge {
        display: inline-flex;
        padding: 5px 10px;
        border-radius: 999px;
        font-size: 11px;
        font-weight: 800;
        margin-top: 8px;
        border: 1px solid transparent;
    }
    .badge-low { background: #DCFCE7; color: #15803D; border-color: #BBF7D0; }
    .badge-watch { background: #FEF3C7; color: #B45309; border-color: #FDE68A; }
    .badge-concern { background: #FFEDD5; color: #C2410C; border-color: #FDBA74; }
    .badge-critical { background: #FEE2E2; color: #B91C1C; border-color: #FECACA; }

    .alert-box {
        background: #FFF7ED;
        border: 1px solid #FED7AA;
        border-radius: 16px;
        padding: 13px 14px;
        color: #9A3412;
        font-size: 12px;
        line-height: 1.55;
        font-weight: 650;
    }

    .nav-logo {
        padding: 16px 4px 12px 4px;
    }
    .nav-logo-title {
        font-size: 22px;
        font-weight: 850;
        color: white !important;
        letter-spacing: -0.03em;
        line-height: 1.05;
    }
    .nav-logo-sub {
        font-size: 11px;
        color: #AFC7E9 !important;
        margin-top: 7px;
        font-weight: 600;
        line-height: 1.4;
    }
    .nav-label {
        font-size: 11px;
        color: #8EAAD0 !important;
        text-transform: uppercase;
        letter-spacing: .08em;
        font-weight: 800;
        margin: 14px 0 6px 2px;
    }

    .filter-label {
        font-size: 11px;
        color: #64748B;
        font-weight: 800;
        text-transform: uppercase;
        letter-spacing: 0.04em;
        margin-bottom: -4px;
    }

    .stSelectbox label, .stMultiSelect label, .stRadio label {
        font-size: 12px !important;
        font-weight: 800 !important;
        color: #475569 !important;
    }

    [data-testid="stDataFrame"] {
        border-radius: 16px;
        overflow: hidden;
        border: 1px solid #E5EAF2;
    }

    .js-plotly-plot, .plotly, .plot-container {
        border-radius: 16px;
    }

    hr { margin: 0.7rem 0; }

    /* hide Streamlit chrome */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    /* make sidebar filters readable */
    [data-testid="stSidebar"] div[data-baseweb="select"] span,
    [data-testid="stSidebar"] div[data-baseweb="select"] div {
        color: #0F172A !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# -----------------------------
# Helpers
# -----------------------------
DATA_FILE = "geosentinel_monthly_dashboard_data.csv"

@st.cache_data
def load_data():
    possible_paths = [
        Path(DATA_FILE),
        Path(__file__).parent / DATA_FILE,
        Path.cwd() / DATA_FILE,
        Path("/mnt/data") / DATA_FILE,
    ]
    for p in possible_paths:
        if p.exists():
            df = pd.read_csv(p)
            break
    else:
        st.error(f"ไม่พบไฟล์ {DATA_FILE} กรุณาวาง CSV ไว้ในโฟลเดอร์เดียวกับไฟล์ Python นี้")
        st.stop()

    df["year_month_date"] = pd.to_datetime(df["year_month"], errors="coerce")
    df = df.sort_values(["data_center_name", "year_month_date"]).reset_index(drop=True)
    return df


def risk_badge_class(level):
    level = str(level).lower()
    if "critical" in level:
        return "badge-critical"
    if "concern" in level:
        return "badge-concern"
    if "watch" in level:
        return "badge-watch"
    return "badge-low"


def risk_color(level):
    level = str(level).lower()
    if "critical" in level:
        return "#EF4444"
    if "concern" in level:
        return "#F97316"
    if "watch" in level:
        return "#F59E0B"
    return "#22C55E"


def score_color(value):
    try:
        v = float(value)
    except Exception:
        return "#64748B"
    if v >= 75:
        return "#EF4444"
    if v >= 55:
        return "#F97316"
    if v >= 35:
        return "#F59E0B"
    return "#22C55E"


def card_metric(title, value, subtitle, icon):
    return f"""
    <div class="metric-card">
      <div class="metric-row">
        <div>
          <div class="metric-title">{title}</div>
          <div class="metric-value">{value}</div>
          <div class="metric-subtitle">{subtitle}</div>
        </div>
        <div class="metric-icon">{icon}</div>
      </div>
    </div>
    """


def plot_map(df, score_col, title, color_scale):
    center_lat = df["latitude"].mean() if len(df) else 0
    center_lon = df["longitude"].mean() if len(df) else 0
    fig = px.scatter_mapbox(
        df,
        lat="latitude",
        lon="longitude",
        color=score_col,
        size="risk_score",
        size_max=19,
        hover_name="data_center_name",
        hover_data={
            "latitude": ":.3f",
            "longitude": ":.3f",
            score_col: ":.2f",
            "risk_score": ":.2f",
            "risk_level": True,
        },
        color_continuous_scale=color_scale,
        zoom=2.35,
        center={"lat": center_lat, "lon": center_lon},
        height=285,
    )
    fig.update_layout(
        mapbox_style="carto-positron",
        margin=dict(l=0, r=0, t=0, b=0),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        coloraxis_colorbar=dict(title="Score", thickness=10, len=0.75),
        font=dict(family="Inter", size=11, color="#334155"),
    )
    return fig


def line_chart(df, y_col, title, color=None):
    fig = px.line(df, x="year_month_date", y=y_col, markers=True, height=210)
    fig.update_traces(line=dict(width=3), marker=dict(size=6))
    fig.update_layout(
        margin=dict(l=10, r=10, t=8, b=5),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        xaxis_title="",
        yaxis_title="",
        font=dict(family="Inter", size=11, color="#334155"),
        xaxis=dict(showgrid=False),
        yaxis=dict(gridcolor="#E5EAF2"),
    )
    return fig


def readable_table(df, cols):
    rename_map = {
        "data_center_name": "Data Center",
        "year_month": "Month",
        "mean_LST_C": "Land Surface Temperature",
        "mean_NDWI": "Water Availability",
        "mean_NDVI": "Vegetation Health",
        "mean_NDBI": "Urbanization Index",
        "precipitation_mm": "Precipitation",
        "soil_moisture": "Soil Moisture",
        "lst_change_1y": "Temperature Change",
        "ndwi_change_1y": "Water Change",
        "ndvi_change_1y": "Vegetation Change",
        "ndbi_change_1y": "Urbanization Change",
        "ECI_score": "ECI Score",
        "ESS_score": "ESS Score",
        "risk_score": "Risk Score",
        "risk_level": "Risk Level",
        "forecast_risk_score_6m": "Forecast Risk 6 Months",
        "forecast_risk_level_6m": "Forecast Level 6 Months",
        "forecast_risk_score_12m": "Forecast Risk 12 Months",
        "forecast_risk_level_12m": "Forecast Level 12 Months",
        "latitude": "Latitude",
        "longitude": "Longitude",
    }
    out = df[cols].copy()
    for c in out.columns:
        if pd.api.types.is_numeric_dtype(out[c]):
            out[c] = out[c].round(2)
    return out.rename(columns=rename_map)


# -----------------------------
# Data
# -----------------------------
df = load_data()

# Latest month default
months = sorted(df["year_month"].dropna().unique().tolist())
risk_levels = sorted(df["risk_level"].dropna().unique().tolist())
data_centers = sorted(df["data_center_name"].dropna().unique().tolist())

# -----------------------------
# Sidebar: clickable menu + filters
# -----------------------------
with st.sidebar:
    st.markdown(
        """
        <div class="nav-logo">
            <div class="nav-logo-title">DC-Resource<br>Intelligence</div>
            <div class="nav-logo-sub">GeoAI Environmental Monitoring for Data Centers</div>
        </div>
        <div class="nav-label">Navigation</div>
        """,
        unsafe_allow_html=True,
    )

    if "page" not in st.session_state:
        st.session_state.page = "Overview"

    pages = ["Overview", "Hotspot Detail", "Alerts", "Data Centers", "Trends", "Forecast", "Reports", "About"]
    icons = ["▣", "◎", "⚠", "⌂", "↗", "◷", "▤", "ⓘ"]
    for icon, page in zip(icons, pages):
        label = f"{icon}  {page}"
        if st.button(label, key=f"nav_{page}"):
            st.session_state.page = page

    st.markdown("<div class='nav-label'>Filters</div>", unsafe_allow_html=True)

    selected_month = st.selectbox("Month", months, index=len(months)-1, key="filter_month")
    selected_risk = st.multiselect("Risk Level", risk_levels, default=risk_levels, key="filter_risk")
    selected_centers = st.multiselect("Data Center", data_centers, default=data_centers, key="filter_center")
    sort_by_label = st.selectbox(
        "Sort By",
        ["Risk Score", "ECI Score", "ESS Score", "Land Surface Temperature", "Water Availability"],
        key="filter_sort",
    )

    st.markdown("<div class='nav-label'>Status</div>", unsafe_allow_html=True)
    st.caption("All filters are active and connected to every card, map, table, and chart.")

sort_map = {
    "Risk Score": "risk_score",
    "ECI Score": "ECI_score",
    "ESS Score": "ESS_score",
    "Land Surface Temperature": "mean_LST_C",
    "Water Availability": "mean_NDWI",
}
sort_col = sort_map[sort_by_label]

filtered = df[
    (df["year_month"] == selected_month)
    & (df["risk_level"].isin(selected_risk))
    & (df["data_center_name"].isin(selected_centers))
].copy()

if filtered.empty:
    st.warning("ไม่มีข้อมูลตาม Filter ที่เลือก กรุณาปรับตัวกรองด้านซ้าย")
    st.stop()

filtered = filtered.sort_values(sort_col, ascending=False).reset_index(drop=True)
selected_detail = filtered.iloc[0]["data_center_name"]

# detail center changes with page or filter; also selectable in detail panel
# -----------------------------
# Top Header
# -----------------------------
st.markdown(
    f"""
    <div class="top-header">
        <div style="display:flex; justify-content:space-between; gap:16px; align-items:flex-start;">
            <div>
                <h1 class="title-main">DC-Resource Intelligence Platform</h1>
                <div class="title-sub">GeoAI-Based Environmental Monitoring and Resource Risk Assessment for Data Centers</div>
            </div>
            <div style="display:flex; gap:8px; flex-wrap:wrap; justify-content:flex-end;">
                <span class="mini-pill">Month: {selected_month}</span>
                <span class="mini-pill">{len(filtered)} Active Records</span>
                <span class="mini-pill">{st.session_state.page}</span>
            </div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# -----------------------------
# Main Horizontal Layout: left main + right detail
# -----------------------------
main_col, detail_col = st.columns([1.92, 0.9], gap="medium")

with main_col:
    # KPI row: horizontal exactly
    total_dc = filtered["data_center_name"].nunique()
    critical_eci = int((filtered["ECI_score"] >= filtered["ECI_score"].quantile(0.80)).sum())
    critical_ess = int((filtered["ESS_score"] >= filtered["ESS_score"].quantile(0.80)).sum())
    top_hotspot = str(filtered.iloc[0]["data_center_name"]).replace("_", " ")

    k1, k2, k3, k4 = st.columns(4, gap="medium")
    with k1:
        st.markdown(card_metric("Monitored Data Centers", total_dc, "Filtered active sites", "⌂"), unsafe_allow_html=True)
    with k2:
        st.markdown(card_metric("Critical ECI Areas", critical_eci, "Highest environmental change", "↯"), unsafe_allow_html=True)
    with k3:
        st.markdown(card_metric("Critical ESS Areas", critical_ess, "Highest environmental stress", "◌"), unsafe_allow_html=True)
    with k4:
        st.markdown(card_metric("Top Hotspot", top_hotspot[:18], "Ranked by selected filter", "⚠"), unsafe_allow_html=True)

    # Map row: horizontal side-by-side
    map1, map2 = st.columns(2, gap="medium")
    with map1:
        st.markdown("<div class='card'><div class='section-title'>ECI Map</div><div class='section-subtitle'>Environmental Change Index by data center location</div>", unsafe_allow_html=True)
        st.plotly_chart(plot_map(filtered, "ECI_score", "ECI Map", "YlOrRd"), use_container_width=True, config={"displayModeBar": False})
        st.markdown("</div>", unsafe_allow_html=True)
    with map2:
        st.markdown("<div class='card'><div class='section-title'>ESS Map</div><div class='section-subtitle'>Environmental Stress Score by data center location</div>", unsafe_allow_html=True)
        st.plotly_chart(plot_map(filtered, "ESS_score", "ESS Map", "OrRd"), use_container_width=True, config={"displayModeBar": False})
        st.markdown("</div>", unsafe_allow_html=True)

    # Tables row: horizontal side-by-side
    t1, t2 = st.columns(2, gap="medium")
    with t1:
        st.markdown("<div class='card'><div class='section-title'>Top 5 by Environmental Change</div><div class='section-subtitle'>Highest ECI Score in selected month</div>", unsafe_allow_html=True)
        table_eci = readable_table(
            filtered.nlargest(5, "ECI_score"),
            ["data_center_name", "ECI_score", "risk_score", "risk_level"],
        )
        st.dataframe(table_eci, use_container_width=True, hide_index=True, height=210)
        st.markdown("</div>", unsafe_allow_html=True)
    with t2:
        st.markdown("<div class='card'><div class='section-title'>Top 5 by Environmental Stress</div><div class='section-subtitle'>Highest ESS Score in selected month</div>", unsafe_allow_html=True)
        table_ess = readable_table(
            filtered.nlargest(5, "ESS_score"),
            ["data_center_name", "ESS_score", "mean_LST_C", "mean_NDWI"],
        )
        st.dataframe(table_ess, use_container_width=True, hide_index=True, height=210)
        st.markdown("</div>", unsafe_allow_html=True)

    # Extra page content, controlled by clickable left menu
    if st.session_state.page == "Data Centers":
        st.markdown("<div class='card'><div class='section-title'>Data Center Records</div><div class='section-subtitle'>Filtered dataset with dashboard-ready column names</div>", unsafe_allow_html=True)
        st.dataframe(
            readable_table(
                filtered,
                [
                    "data_center_name", "year_month", "latitude", "longitude", "mean_LST_C",
                    "mean_NDWI", "mean_NDVI", "mean_NDBI", "ECI_score", "ESS_score",
                    "risk_score", "risk_level", "forecast_risk_score_6m", "forecast_risk_score_12m"
                ],
            ),
            use_container_width=True,
            hide_index=True,
            height=420,
        )
        st.markdown("</div>", unsafe_allow_html=True)

    if st.session_state.page == "Trends":
        st.markdown("<div class='card'><div class='section-title'>Portfolio Trend Overview</div><div class='section-subtitle'>Average monthly movement across selected data centers</div>", unsafe_allow_html=True)
        trend_df = df[df["data_center_name"].isin(selected_centers)].groupby("year_month_date", as_index=False)[["mean_LST_C", "mean_NDWI", "ECI_score", "ESS_score", "risk_score"]].mean()
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=trend_df["year_month_date"], y=trend_df["risk_score"], mode="lines+markers", name="Risk Score"))
        fig.add_trace(go.Scatter(x=trend_df["year_month_date"], y=trend_df["ECI_score"], mode="lines+markers", name="ECI Score"))
        fig.add_trace(go.Scatter(x=trend_df["year_month_date"], y=trend_df["ESS_score"], mode="lines+markers", name="ESS Score"))
        fig.update_layout(height=330, margin=dict(l=10, r=10, t=8, b=5), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", legend=dict(orientation="h"), font=dict(family="Inter", size=11))
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
        st.markdown("</div>", unsafe_allow_html=True)

    if st.session_state.page == "Forecast":
        st.markdown("<div class='card'><div class='section-title'>AI Forecast Center</div><div class='section-subtitle'>Current, 6-month, and 12-month forecast risk comparison</div>", unsafe_allow_html=True)
        forecast_view = filtered[["data_center_name", "risk_score", "forecast_risk_score_6m", "forecast_risk_score_12m", "risk_level", "forecast_risk_level_6m", "forecast_risk_level_12m"]].copy()
        forecast_view = forecast_view.sort_values("forecast_risk_score_12m", ascending=False).head(12)
        forecast_long = forecast_view.melt(
            id_vars="data_center_name",
            value_vars=["risk_score", "forecast_risk_score_6m", "forecast_risk_score_12m"],
            var_name="Period",
            value_name="Risk Score",
        )
        forecast_long["Period"] = forecast_long["Period"].map({
            "risk_score": "Current",
            "forecast_risk_score_6m": "6 Months",
            "forecast_risk_score_12m": "12 Months",
        })
        fig = px.bar(forecast_long, x="data_center_name", y="Risk Score", color="Period", barmode="group", height=360)
        fig.update_layout(margin=dict(l=10, r=10, t=8, b=5), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", xaxis_title="", font=dict(family="Inter", size=11))
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
        st.markdown("</div>", unsafe_allow_html=True)

    if st.session_state.page == "Reports":
        st.markdown("<div class='card'><div class='section-title'>Executive Report Summary</div><div class='section-subtitle'>Auto-generated summary from selected filters</div>", unsafe_allow_html=True)
        avg_risk = filtered["risk_score"].mean()
        avg_forecast = filtered["forecast_risk_score_12m"].mean()
        trend_word = "increase" if avg_forecast > avg_risk else "remain stable or decrease"
        st.markdown(
            f"""
            <div class="alert-box">
            In {selected_month}, the platform monitors <b>{total_dc}</b> data center locations under the selected filter. 
            The average current risk score is <b>{avg_risk:.2f}</b>, while the 12-month forecast average is <b>{avg_forecast:.2f}</b>. 
            Overall risk is expected to <b>{trend_word}</b> based on ECI, ESS, and forecast indicators.
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.markdown("</div>", unsafe_allow_html=True)

    if st.session_state.page == "About":
        st.markdown("<div class='card'><div class='section-title'>About This Platform</div><div class='section-subtitle'>Innovation positioning for GeoAI Hackathon</div>", unsafe_allow_html=True)
        st.markdown(
            """
            <div class="alert-box" style="background:#EFF6FF; border-color:#BFDBFE; color:#1E40AF;">
            DC-Resource Intelligence Platform combines satellite-derived indicators, Environmental Change Index, Environmental Stress Score, Risk Engine, and AI-based 6–12 month forecasting to support proactive data center resource risk monitoring.
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.markdown("</div>", unsafe_allow_html=True)

with detail_col:
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown("<div class='detail-title'>Hotspot Detail</div><div class='detail-subtitle'>Focused intelligence panel</div>", unsafe_allow_html=True)

    center_options = filtered["data_center_name"].tolist()
    chosen_center = st.selectbox("Select Hotspot", center_options, index=0, key="detail_center")
    selected_row = filtered[filtered["data_center_name"] == chosen_center].iloc[0]
    history = df[df["data_center_name"] == chosen_center].copy()

    st.markdown(
        f"""
        <div style="font-size:18px; font-weight:850; color:#0F172A; margin-top:8px;">{chosen_center.replace('_',' ')}</div>
        <div style="font-size:12px; color:#64748B; font-weight:700; margin-bottom:12px;">Lat {selected_row['latitude']:.3f}, Lon {selected_row['longitude']:.3f}</div>
        """,
        unsafe_allow_html=True,
    )

    d1, d2 = st.columns(2, gap="small")
    with d1:
        st.markdown(
            f"""
            <div class="score-box">
              <div class="score-label">ECI Score</div>
              <div class="score-value">{selected_row['ECI_score']:.2f}</div>
              <span class="badge {risk_badge_class(selected_row['risk_level'])}">{selected_row['risk_level']}</span>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with d2:
        st.markdown(
            f"""
            <div class="score-box">
              <div class="score-label">ESS Score</div>
              <div class="score-value">{selected_row['ESS_score']:.2f}</div>
              <span class="badge {risk_badge_class(selected_row['risk_level'])}">{selected_row['risk_level']}</span>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown("<div class='section-title'>LST Trend</div><div class='section-subtitle'>Land Surface Temperature</div>", unsafe_allow_html=True)
    st.plotly_chart(line_chart(history, "mean_LST_C", "LST"), use_container_width=True, config={"displayModeBar": False})

    st.markdown("<div class='section-title'>NDWI Trend</div><div class='section-subtitle'>Water Availability</div>", unsafe_allow_html=True)
    st.plotly_chart(line_chart(history, "mean_NDWI", "NDWI"), use_container_width=True, config={"displayModeBar": False})

    st.markdown("<hr>", unsafe_allow_html=True)
    cur = float(selected_row["risk_score"])
    f6 = float(selected_row["forecast_risk_score_6m"])
    f12 = float(selected_row["forecast_risk_score_12m"])
    direction = "rising" if f12 > cur else "stable or decreasing"

    st.markdown("<div class='section-title'>AI Alert Summary</div>", unsafe_allow_html=True)
    st.markdown(
        f"""
        <div class="alert-box">
        <b>{chosen_center.replace('_',' ')}</b> shows a current risk score of <b>{cur:.2f}</b>.
        The 6-month forecast is <b>{f6:.2f}</b> and the 12-month forecast is <b>{f12:.2f}</b>, indicating a <b>{direction}</b> risk pattern.
        Recommended action: monitor cooling demand, water availability, and local environmental change indicators.
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(
        f"""
        <div class="score-box">
          <div class="score-label">Overall Risk Level</div>
          <div class="score-value" style="color:{risk_color(selected_row['risk_level'])};">{selected_row['risk_level']}</div>
          <div style="height:8px; background:#E5EAF2; border-radius:999px; overflow:hidden; margin-top:12px;">
             <div style="width:{min(max(cur,0),100)}%; height:100%; background:{score_color(cur)};"></div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("</div>", unsafe_allow_html=True)
