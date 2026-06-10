import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from pathlib import Path

st.set_page_config(page_title="DC-Resource Intelligence Platform", page_icon="🛡️", layout="wide", initial_sidebar_state="collapsed")

DATA_FILE = Path("geosentinel_monthly_dashboard_data.csv")

# -----------------------------------------------------------------------------
# Load data
# -----------------------------------------------------------------------------
@st.cache_data
def load_data():
    if not DATA_FILE.exists():
        st.error("ไม่พบไฟล์ geosentinel_monthly_dashboard_data.csv กรุณาวางไฟล์ไว้ในโฟลเดอร์เดียวกับ app.py")
        st.stop()
    df = pd.read_csv(DATA_FILE)
    df["year_month"] = pd.to_datetime(df["year_month"])
    return df

df = load_data()
all_months = sorted(df["year_month"].unique())
latest_month = all_months[-1]
latest = df[df["year_month"] == latest_month].copy()
centers = sorted(df["data_center_name"].unique())

# -----------------------------------------------------------------------------
# Display names: no underscore on dashboard/table
# -----------------------------------------------------------------------------
DISPLAY_COLUMNS = {
    "data_center_name": "Data Center",
    "latitude": "Latitude",
    "longitude": "Longitude",
    "year_month": "Date",
    "mean_LST_C": "Land Surface Temperature",
    "mean_NDWI": "Water Availability",
    "mean_NDVI": "Vegetation Health",
    "mean_NDBI": "Built Up Index",
    "precipitation_mm": "Rainfall",
    "soil_moisture": "Soil Moisture",
    "lst_change_1y": "Temperature Change",
    "ndwi_change_1y": "Water Change",
    "ndvi_change_1y": "Vegetation Change",
    "ndbi_change_1y": "Urban Change",
    "ECI_score": "ECI Score",
    "ESS_score": "ESS Score",
    "risk_score": "Risk Score",
    "risk_level": "Risk Level",
    "forecast_risk_score_6m": "Forecast Risk 6 Months",
    "forecast_risk_level_6m": "Forecast Level 6 Months",
    "forecast_risk_score_12m": "Forecast Risk 12 Months",
    "forecast_risk_level_12m": "Forecast Level 12 Months",
}

# -----------------------------------------------------------------------------
# Helpers
# -----------------------------------------------------------------------------
def level_color(level):
    level = str(level).lower()
    if level == "critical":
        return "#dc2626"
    if level == "concern":
        return "#f97316"
    if level == "watch":
        return "#facc15"
    return "#22c55e"


def level_badge(level):
    color = level_color(level)
    bg = {"#dc2626":"#fee2e2", "#f97316":"#ffedd5", "#facc15":"#fef3c7", "#22c55e":"#dcfce7"}[color]
    return f'<span class="badge" style="background:{bg};color:{color};">{level}</span>'


def metric_card(icon, title, value, subtitle, bubble="#dbeafe", extra=""):
    return f"""
    <div class="metric-card">
        <div class="metric-flex">
            <div class="metric-icon" style="background:{bubble};">{icon}</div>
            <div>
                <div class="metric-title">{title}</div>
                <div class="metric-value">{value}</div>
            </div>
        </div>
        <div class="metric-subtitle">{subtitle}</div>
        {extra}
    </div>
    """


def mini_status_dot(color):
    return f'<span style="display:inline-block;width:13px;height:13px;border-radius:50%;background:{color};"></span>'


def make_us_map(data, score_col, title, subtitle, legend_title):
    fig = go.Figure()
    colors = data["risk_level"].map(level_color)
    sizes = 16 + (data[score_col] - data[score_col].min()) / max((data[score_col].max() - data[score_col].min()), 1) * 16
    fig.add_trace(go.Scattergeo(
        lon=data["longitude"], lat=data["latitude"], text=data["data_center_name"],
        customdata=data[[score_col, "risk_level", "mean_LST_C", "mean_NDWI"]],
        mode="markers",
        marker=dict(size=sizes, color=colors, opacity=0.88, line=dict(width=1.8, color="white")),
        hovertemplate=(
            "<b>%{text}</b><br>" + DISPLAY_COLUMNS[score_col] + ": %{customdata[0]:.2f}<br>" +
            "Risk Level: %{customdata[1]}<br>Land Surface Temperature: %{customdata[2]:.2f} °C<br>" +
            "Water Availability: %{customdata[3]:.2f}<extra></extra>"
        ),
    ))
    fig.update_layout(
        height=375,
        margin=dict(l=0, r=0, t=4, b=0),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        geo=dict(
            scope="usa", projection_type="albers usa", showland=True, landcolor="#fafafa",
            showlakes=True, lakecolor="#dff2fb", showocean=True, oceancolor="#dff2fb",
            countrycolor="#d1d5db", subunitcolor="#e5e7eb", coastlinecolor="#d1d5db",
            bgcolor="#eaf6fb",
        ),
        showlegend=False,
    )
    return fig


def line_chart(ts, y, title, suffix="", color="#ef4444"):
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=ts["year_month"], y=ts[y], mode="lines+markers", line=dict(width=3, color=color),
        marker=dict(size=5, color=color), fill="tozeroy", fillcolor="rgba(239,68,68,0.12)",
        hovertemplate="%{x|%b %Y}<br>%{y:.2f}" + suffix + "<extra></extra>",
    ))
    fig.update_layout(
        title=dict(text=title, font=dict(size=13, color="#172033")),
        height=245, margin=dict(l=12, r=18, t=45, b=18),
        paper_bgcolor="white", plot_bgcolor="white", xaxis_title="", yaxis_title="",
        font=dict(family="Inter", size=11, color="#334155"),
    )
    fig.update_xaxes(showgrid=True, gridcolor="#eef2f7", tickformat="%Y")
    fig.update_yaxes(showgrid=True, gridcolor="#eef2f7")
    return fig


def display_table(data):
    table = data.rename(columns=DISPLAY_COLUMNS).copy()
    for col in table.select_dtypes(include="number").columns:
        table[col] = table[col].round(2)
    st.dataframe(table, use_container_width=True, hide_index=True, height=260)

# -----------------------------------------------------------------------------
# CSS: clone layout from reference image
# -----------------------------------------------------------------------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

html, body, [class*="css"] {font-family:'Inter', sans-serif;}
.stApp {background:#f4f8fb;}
header[data-testid="stHeader"] {display:none;}
section[data-testid="stSidebar"] {display:none;}
.block-container {padding: 0.25rem 0.25rem 0.25rem 0.25rem; max-width: 100%;}
div[data-testid="stVerticalBlock"] {gap: 0.75rem;}

.shell {
    display:grid;
    grid-template-columns: 218px minmax(720px, 1.35fr) minmax(420px, .92fr);
    gap: 14px;
    min-height: 100vh;
}
.sidebar-panel {
    background: linear-gradient(180deg,#062542 0%,#031424 100%);
    color:white;
    border-radius: 14px;
    padding: 26px 18px;
    min-height: calc(100vh - 10px);
    position: sticky; top: 5px;
}
.brand {display:flex; gap:12px; align-items:center; margin-bottom: 22px;}
.brand-shield {width:42px;height:42px;border-radius:14px;border:2px solid #3ee6a2;display:flex;align-items:center;justify-content:center;font-size:23px;}
.brand-title {font-size:18px;font-weight:800;}
.brand-sub {font-size:11px;line-height:1.5;color:#b8d2e8;margin-top:12px;margin-left:46px;}
.nav-item {display:flex;align-items:center;gap:13px;padding:14px 13px;border-radius:10px;font-weight:700;font-size:14px;margin:8px 0;color:#e6f4ff;}
.nav-active {background:linear-gradient(90deg,#1168d8,#0d4ea4);box-shadow:0 10px 24px rgba(37,99,235,.26);}
.source-card {border:1px solid rgba(255,255,255,.22);border-radius:11px;padding:16px;margin-top:44vh;color:#dff3ff;font-size:12px;line-height:1.7;}
.satellite {font-size:38px;text-align:center;margin-top:14px;}

.main-panel, .right-panel {
    background: rgba(255,255,255,.88);
    border:1px solid #dce7f0;
    border-radius: 14px;
    padding: 24px;
    box-shadow: 0 5px 18px rgba(21,55,84,.07);
}
.top-row {display:flex;justify-content:space-between;align-items:center;margin-bottom:20px;}
.title {font-size:24px;font-weight:800;color:#0f172a;margin-bottom:6px;}
.subtitle {font-size:14px;color:#52677d;}
.date-pill {border:1px solid #dbe7f0;border-radius:12px;padding:12px 16px;background:#fff;color:#0f172a;font-weight:600;font-size:14px;}
.metric-grid {display:grid;grid-template-columns:repeat(4,1fr);gap:14px;margin-bottom:18px;}
.metric-card, .card {
    background:white;border:1px solid #dfe8f1;border-radius:14px;padding:16px;
    box-shadow:0 8px 24px rgba(21,55,84,.06);
}
.metric-card {min-height:115px;}
.metric-flex {display:flex;gap:14px;align-items:center;}
.metric-icon {width:58px;height:58px;border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:28px;}
.metric-title {font-size:13px;font-weight:700;color:#0f172a;line-height:1.35;}
.metric-value {font-size:31px;font-weight:800;color:#071327;line-height:1.15;margin-top:4px;}
.metric-subtitle {font-size:12px;color:#52677d;margin-top:12px;}
.purple {color:#6d28d9;font-weight:800;font-size:16px;margin-top:13px;}
.map-grid, .table-grid, .chart-grid, .alert-grid {display:grid;grid-template-columns:1fr 1fr;gap:14px;}
.card-title {font-size:14px;font-weight:800;color:#0f172a;margin-bottom:5px;}
.card-subtitle {font-size:12px;color:#64748b;margin-bottom:9px;}
.expand-btn {float:right;border:1px solid #dbe7f0;border-radius:10px;padding:4px 7px;color:#64748b;background:#fff;}
.legend-box {position:relative;margin-top:-116px;margin-left:12px;background:white;border:1px solid #dbe7f0;border-radius:10px;padding:11px;width:135px;font-size:11px;line-height:1.9;box-shadow:0 5px 18px rgba(0,0,0,.08);}
.legend-title {font-weight:800;color:#0f172a;margin-bottom:4px;}
.info-strip {display:grid;grid-template-columns:1.4fr 1fr;gap:15px;background:#eef7ff;border-radius:12px;padding:16px;margin-top:14px;border:1px solid #dbeafe;font-size:12px;color:#10243d;}
.badge {display:inline-block;border-radius:8px;padding:5px 9px;font-size:12px;font-weight:800;}
.right-title-row {display:flex;align-items:center;justify-content:space-between;margin-bottom:12px;}
.breadcrumb {font-size:11px;color:#64748b;margin-top:6px;}
.small-card-grid {display:grid;grid-template-columns:.95fr .9fr .9fr 1.15fr;gap:12px;margin-bottom:14px;}
.small-title {font-size:12px;font-weight:800;color:#0f172a;}
.small-value {font-size:29px;font-weight:800;color:#071327;margin-top:10px;}
.driver-row {font-size:11px;display:flex;gap:8px;align-items:center;margin:8px 0;color:#172033;}
.alert-summary {display:grid;grid-template-columns:70px 1fr 150px;gap:18px;align-items:center;background:#fff4f4;border:1px solid #fecaca;border-radius:14px;padding:18px;margin:14px 0;}
.alert-icon {width:58px;height:58px;border-radius:50%;background:#dc2626;color:white;display:flex;align-items:center;justify-content:center;font-size:31px;font-weight:800;}
.alert-title {font-weight:800;color:#0f172a;font-size:14px;margin-bottom:8px;}
.alert-text {font-size:12px;color:#1f2937;line-height:1.65;}
.risk-box {text-align:center;}
.risk-label {font-size:12px;font-weight:800;color:#0f172a;margin-bottom:8px;}
.risk-value {background:#dc2626;color:white;border-radius:8px;font-size:18px;font-weight:800;padding:12px 14px;}
.community-grid {display:grid;grid-template-columns:1fr 1.35fr;gap:12px;margin-top:12px;}
.footer-dark {background:#062542;color:white;border-radius:12px;padding:17px;margin-top:14px;display:flex;justify-content:space-between;font-size:11px;align-items:center;}

/* Make Streamlit widgets flatter */
div[data-testid="stSelectbox"] label {display:none;}
div[data-baseweb="select"] > div {border-radius:10px;border-color:#dbe7f0;background:#fff;}
.stPlotlyChart {border-radius: 12px; overflow:hidden;}
[data-testid="stDataFrame"] {border:1px solid #e4edf5;border-radius:12px;overflow:hidden;}

@media (max-width: 1300px) {
    .shell {grid-template-columns: 190px 1fr;}
    .right-panel {grid-column:2;}
    .metric-grid {grid-template-columns:repeat(2,1fr);}
}
</style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# Select current hotspot in invisible/compact top area
# -----------------------------------------------------------------------------
rank_order = {"Critical": 4, "Concern": 3, "Watch": 2, "Stable": 1, "Low": 1}
latest["Risk Rank"] = latest["risk_level"].map(rank_order).fillna(0)
latest = latest.sort_values(["Risk Rank", "risk_score", "ECI_score", "ESS_score"], ascending=False)
top_hotspot = latest.iloc[0]

# Use selectbox for actual interactivity, placed on top right panel later
selected_center = st.session_state.get("selected_center", top_hotspot["data_center_name"])

# -----------------------------------------------------------------------------
# Custom layout start
# -----------------------------------------------------------------------------
st.markdown('<div class="shell">', unsafe_allow_html=True)

# Sidebar
st.markdown(f"""
<div class="sidebar-panel">
    <div class="brand">
        <div class="brand-shield">🛡️</div>
        <div class="brand-title">GeoSentinel AI</div>
    </div>
    <div class="brand-sub">Environmental<br>Early Warning System</div>
    <div style="height:22px;"></div>
    <div class="nav-item nav-active">▦ <span>Overview</span></div>
    <div class="nav-item">⌖ <span>Hotspot Detail</span></div>
    <div class="nav-item">♢ <span>Alerts</span></div>
    <div class="nav-item">▱ <span>Data Centers</span></div>
    <div class="nav-item">⌁ <span>Trends</span></div>
    <div class="nav-item">▤ <span>Reports</span></div>
    <div class="nav-item">ⓘ <span>About</span></div>
    <div class="source-card">
        <b>Data Source</b><br>Google Earth Engine<br>2019 – 2025
        <div class="satellite">🛰️</div>
    </div>
</div>
""", unsafe_allow_html=True)

# Main panel
st.markdown('<div class="main-panel">', unsafe_allow_html=True)
st.markdown(f"""
<div class="top-row">
    <div>
        <div class="title">Overview Dashboard</div>
        <div class="subtitle">Real-time environmental monitoring of data centers across the United States</div>
    </div>
    <div class="date-pill">▣ &nbsp; {pd.to_datetime(latest_month).strftime('%b %d, %Y')} &nbsp;⌄</div>
</div>
""", unsafe_allow_html=True)

critical_eci = int((latest["ECI_score"] >= latest["ECI_score"].quantile(.80)).sum())
critical_ess = int((latest["ESS_score"] >= latest["ESS_score"].quantile(.80)).sum())

st.markdown('<div class="metric-grid">', unsafe_allow_html=True)
st.markdown(metric_card("▦", "Monitored<br>Data Centers", latest["data_center_name"].nunique(), "Across the United States", "#dbeafe"), unsafe_allow_html=True)
st.markdown(metric_card("⌁", "Critical<br>ECI Areas", critical_eci, "High rate of change", "#fee2e2"), unsafe_allow_html=True)
st.markdown(metric_card("⚠", "Critical<br>ESS Areas", critical_ess, "High environmental stress", "#ffedd5"), unsafe_allow_html=True)
st.markdown(f"""
<div class="metric-card">
    <div class="metric-flex">
        <div class="metric-icon" style="background:#ede9fe;">◎</div>
        <div>
            <div class="metric-title">Top Hotspot</div>
            <div class="purple">{top_hotspot['data_center_name']}</div>
        </div>
    </div>
    <div class="metric-subtitle"><b>ECI:</b> {top_hotspot['ECI_score']:.2f} &nbsp;&nbsp; <b>ESS:</b> {top_hotspot['ESS_score']:.2f}</div>
</div>
""", unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# Maps
st.markdown('<div class="map-grid">', unsafe_allow_html=True)
for score_col, title, subtitle, legend_title in [
    ("ECI_score", "ECI Map (Environmental Change Index)", "Rate of environmental change (2019–2025)", "ECI Risk Level"),
    ("ESS_score", "ESS Map (Environmental Stress Score)", "Current environmental stress (2025)", "ESS Risk Level"),
]:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown(f'<div class="card-title">▧ {title}<span class="expand-btn">↗</span></div><div class="card-subtitle">{subtitle}</div>', unsafe_allow_html=True)
    st.plotly_chart(make_us_map(latest, score_col, title, subtitle, legend_title), use_container_width=True, config={"displayModeBar": False})
    st.markdown(f"""
    <div class="legend-box">
        <div class="legend-title">{legend_title}</div>
        {mini_status_dot('#22c55e')} Stable / Low<br>
        {mini_status_dot('#facc15')} Watch / Moderate<br>
        {mini_status_dot('#f97316')} Concern / High<br>
        {mini_status_dot('#dc2626')} Critical
    </div>
    """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# Tables
st.markdown('<div class="table-grid">', unsafe_allow_html=True)
st.markdown('<div class="card"><div class="card-title">▧ Top 5 by Environmental Change (ECI)<span style="float:right;color:#2563eb;font-size:12px;">View all</span></div>', unsafe_allow_html=True)
top_eci = latest.nlargest(5, "ECI_score")[["data_center_name", "ECI_score", "risk_level", "lst_change_1y", "ndwi_change_1y"]]
display_table(top_eci)
st.markdown('</div>', unsafe_allow_html=True)
st.markdown('<div class="card"><div class="card-title">▧ Top 5 by Environmental Stress (ESS)<span style="float:right;color:#2563eb;font-size:12px;">View all</span></div>', unsafe_allow_html=True)
top_ess = latest.nlargest(5, "ESS_score")[["data_center_name", "ESS_score", "risk_level", "mean_LST_C", "mean_NDWI"]]
display_table(top_ess)
st.markdown('</div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

st.markdown("""
<div class="info-strip">
    <div>ℹ️ &nbsp; GeoSentinel AI transforms satellite-derived environmental indicators into early warning insights for communities and decision-makers.</div>
    <div>🧪 &nbsp; ECI detects areas with rapid environmental change.<br>⚠️ &nbsp; ESS detects areas with high current environmental stress.</div>
</div>
""", unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# Right panel
st.markdown('<div class="right-panel">', unsafe_allow_html=True)
st.markdown('<div class="right-title-row"><div><div class="title" style="font-size:19px;">← &nbsp; Hotspot Detail</div><div class="breadcrumb">Overview &nbsp;›&nbsp; Hotspot Detail</div></div></div>', unsafe_allow_html=True)
selected_center = st.selectbox("Choose Data Center", centers, index=centers.index(top_hotspot["data_center_name"]) if top_hotspot["data_center_name"] in centers else 0)
ts = df[df["data_center_name"] == selected_center].sort_values("year_month")
row_df = ts[ts["year_month"] == latest_month]
row = row_df.iloc[0] if not row_df.empty else ts.iloc[-1]

st.markdown('<div class="small-card-grid">', unsafe_allow_html=True)
st.markdown(f"""
<div class="card">
    <div class="small-title">{selected_center}</div>
    <div style="height:24px;"></div>
    <div style="font-size:11px;color:#64748b;">United States</div>
    <div style="border-top:1px solid #e5edf5;margin:12px 0;"></div>
    <div style="font-size:11px;color:#172033;">Data Center</div>
</div>
""", unsafe_allow_html=True)
st.markdown(f"""
<div class="card">
    <div class="small-title"><span style="color:#ef4444;">▌</span> ECI Score</div>
    <div class="small-value">{row['ECI_score']:.2f} {level_badge(row['risk_level'])}</div>
    <div class="metric-subtitle">High rate of change</div>
</div>
""", unsafe_allow_html=True)
st.markdown(f"""
<div class="card">
    <div class="small-title"><span style="color:#f97316;">▌</span> ESS Score</div>
    <div class="small-value">{row['ESS_score']:.2f} {level_badge(row['risk_level'])}</div>
    <div class="metric-subtitle">High environmental stress</div>
</div>
""", unsafe_allow_html=True)
st.markdown(f"""
<div class="card">
    <div class="small-title">Key Drivers (2025)</div>
    <div class="driver-row">🌡️ High Land Surface Temperature</div>
    <div class="driver-row">🌿 Low Vegetation Health</div>
    <div class="driver-row">💧 Low Water Availability</div>
</div>
""", unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

st.markdown('<div class="chart-grid">', unsafe_allow_html=True)
st.plotly_chart(line_chart(ts, "mean_LST_C", "Land Surface Temperature (LST)", " °C", "#ef4444"), use_container_width=True, config={"displayModeBar": False})
st.plotly_chart(line_chart(ts, "mean_NDWI", "Normalized Difference Water Index (NDWI)", "", "#2563eb"), use_container_width=True, config={"displayModeBar": False})
st.markdown('</div>', unsafe_allow_html=True)

risk_level_display = str(row["risk_level"]).upper()
st.markdown(f"""
<div class="alert-summary">
    <div class="alert-icon">!</div>
    <div>
        <div class="alert-title">AI Alert Summary</div>
        <div class="alert-text"><b>{selected_center}</b> shows elevated environmental stress and significant temperature or water index change compared with the historical baseline. Continuous monitoring and proactive mitigation are recommended.</div>
    </div>
    <div class="risk-box">
        <div class="risk-label">Overall Risk Level</div>
        <div class="risk-value">{risk_level_display}</div>
        <div class="metric-subtitle">Priority Action Required</div>
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown('<div class="title" style="font-size:19px;margin-top:8px;">← &nbsp; Community Alert</div><div class="breadcrumb">Overview &nbsp;›&nbsp; Alerts &nbsp;›&nbsp; Alert Detail</div>', unsafe_allow_html=True)
st.markdown('<div class="community-grid">', unsafe_allow_html=True)
st.markdown(f"""
<div class="card" style="display:flex;gap:18px;align-items:center;">
    <div class="alert-icon">!</div>
    <div>
        <div class="small-title">Alert Level</div>
        <div style="font-size:24px;font-weight:800;color:#dc2626;margin-top:7px;">{risk_level_display}</div>
        <div class="metric-subtitle"><b>Issued:</b> {pd.to_datetime(latest_month).strftime('%b %d, %Y')} 12:00 PM</div>
    </div>
</div>
<div class="card">
    <div class="small-title">Issue Detected</div>
    <div style="font-size:15px;font-weight:800;color:#172033;margin:9px 0;">High Heat Stress and Water Stress</div>
    <div class="alert-text">Satellite analysis indicates heat increase and water availability decline in the area.</div>
</div>
""", unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

st.markdown('<div class="alert-grid">', unsafe_allow_html=True)
st.markdown("""
<div class="card">
    <div class="small-title">What does this mean?</div>
    <div class="alert-text" style="margin-top:12px;">The environment in this area is under high stress. This may affect water supply, vegetation, and overall community well-being.</div>
</div>
<div class="card">
    <div class="small-title">Recommended Actions</div>
    <div class="driver-row">✅ Monitor local water storage and usage</div>
    <div class="driver-row">✅ Avoid outdoor activity during peak heat hours</div>
    <div class="driver-row">✅ Save water and use efficiently</div>
    <div class="driver-row">✅ Report to local authority if water shortage continues</div>
    <div class="driver-row">✅ Stay updated with official announcements</div>
</div>
""", unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

st.markdown('<div class="alert-grid">', unsafe_allow_html=True)
st.markdown("""
<div class="card">
    <div class="small-title">Community Resources</div>
    <div class="driver-row">💧 Local Water Authority ↗</div>
    <div class="driver-row">▣ Heat Safety Tips ↗</div>
    <div class="driver-row">▤ Report an Issue ↗</div>
</div>
<div class="card">
    <div class="small-title">Stay Informed</div>
    <div class="metric-subtitle">Get updates when conditions change.</div>
    <div style="display:flex;gap:10px;margin-top:12px;"><div style="flex:1;border:1px solid #dbe7f0;border-radius:8px;padding:11px;color:#94a3b8;font-size:12px;">Enter your email</div><div style="background:#0b65e5;color:white;border-radius:8px;padding:11px 14px;font-weight:800;font-size:12px;">Subscribe</div></div>
</div>
""", unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

st.markdown("""
<div class="footer-dark">
    <div><b>🛡️ GeoSentinel AI</b><br><span style="color:#b8d2e8;">Protecting communities through satellite intelligence</span></div>
    <div style="text-align:right;">Data Source: Google Earth Engine<br>2019 – 2025</div>
</div>
""", unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)