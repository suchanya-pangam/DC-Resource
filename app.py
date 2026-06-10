import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path

st.set_page_config(page_title="DC-Resource Intelligence Platform", layout="wide", initial_sidebar_state="expanded")

CSV_NAME = "geosentinel_monthly_dashboard_data.csv"

# -----------------------------
# Helper functions
# -----------------------------
def clean_name(name: str) -> str:
    return str(name).replace("_", " ")

def level_color(level: str) -> str:
    level = str(level).lower()
    if "critical" in level:
        return "#dc2626"
    if "concern" in level or "high" in level:
        return "#f97316"
    if "watch" in level or "moderate" in level:
        return "#facc15"
    return "#22c55e"

def chip_class(level: str) -> str:
    level = str(level).lower()
    if "critical" in level:
        return "chip critical"
    if "concern" in level or "high" in level:
        return "chip concern"
    if "watch" in level or "moderate" in level:
        return "chip watch"
    return "chip stable"

def level_from_eci(value: float) -> str:
    if value >= 1.0:
        return "Critical"
    if value >= 0.6:
        return "Concern"
    if value >= 0.3:
        return "Watch"
    return "Stable"

def level_from_ess(value: float) -> str:
    if value >= 70:
        return "Critical"
    if value >= 50:
        return "Concern"
    if value >= 30:
        return "Watch"
    return "Stable"

def metric_card(title, value, subtitle, icon, tone="blue"):
    st.markdown(
        f"""
        <div class="metric-card">
            <div>
                <div class="metric-title">{title}</div>
                <div class="metric-value">{value}</div>
                <div class="metric-subtitle">{subtitle}</div>
            </div>
            <div class="metric-icon {tone}">{icon}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

def small_card(label, value, level=None, note=""):
    tag = "" if level is None else f'<span class="{chip_class(level)}">{level}</span>'
    st.markdown(
        f"""
        <div class="small-card">
            <div class="small-label">{label}</div>
            <div class="small-value">{value}</div>
            {tag}
            <div class="small-note">{note}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

def section_header(title, subtitle=""):
    st.markdown(
        f"""
        <div class="section-card section-head">
            <div class="section-title">{title}</div>
            <div class="section-subtitle">{subtitle}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

def make_geo_map(df, value_col, title, color_scale):
    fig = px.scatter_geo(
        df,
        lat="latitude",
        lon="longitude",
        color=value_col,
        size=value_col,
        hover_name="Display Name",
        hover_data={
            value_col: ":.2f",
            "latitude": False,
            "longitude": False,
            "Risk Level": True,
        },
        scope="usa",
        projection="albers usa",
        color_continuous_scale=color_scale,
        size_max=22,
    )
    fig.update_geos(
        showland=True,
        landcolor="#f8fafc",
        showlakes=True,
        lakecolor="#dbeafe",
        showsubunits=True,
        subunitcolor="#e5e7eb",
        bgcolor="rgba(0,0,0,0)",
    )
    fig.update_layout(
        height=285,
        margin=dict(l=0, r=0, t=0, b=0),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        coloraxis_colorbar=dict(title="Score", thickness=12, len=0.72),
    )
    return fig

def line_chart(df, y_col, title, color):
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=df["year_month"],
            y=df[y_col],
            mode="lines+markers",
            line=dict(width=3, color=color),
            marker=dict(size=6),
            fill="tozeroy",
            fillcolor="rgba(59,130,246,0.12)" if color == "#2563eb" else "rgba(220,38,38,0.12)",
        )
    )
    fig.update_layout(
        height=220,
        margin=dict(l=10, r=10, t=10, b=10),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(showgrid=True, gridcolor="#eef2f7", tickfont=dict(size=10)),
        yaxis=dict(showgrid=True, gridcolor="#eef2f7", tickfont=dict(size=10)),
    )
    return fig

def render_table(df, score_col, level_func, title):
    table = df.sort_values(score_col, ascending=False).head(5).copy()
    rows = ""
    for i, row in enumerate(table.itertuples(), 1):
        score = getattr(row, score_col)
        level = level_func(float(score))
        rows += f"""
        <tr>
            <td>{i}</td>
            <td>{clean_name(getattr(row, 'data_center_name'))}</td>
            <td>{float(score):.2f}</td>
            <td><span class=\"{chip_class(level)}\">{level}</span></td>
        </tr>
        """
    st.markdown(
        f"""
        <div class="section-card table-card">
            <div class="table-title">{title}</div>
            <table class="nice-table">
                <thead><tr><th>Rank</th><th>Data Center</th><th>Score</th><th>Level</th></tr></thead>
                <tbody>{rows}</tbody>
            </table>
        </div>
        """,
        unsafe_allow_html=True,
    )

# -----------------------------
# CSS: clone-like horizontal dashboard
# -----------------------------
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap');

    * { font-family: 'Inter', sans-serif; }
    html, body, [data-testid="stAppViewContainer"] { background:#f3f7fb; }
    [data-testid="stHeader"] { display:none; }
    [data-testid="stToolbar"] { display:none; }
    [data-testid="stDecoration"] { display:none; }
    [data-testid="stStatusWidget"] { display:none; }
    [data-testid="stMainBlockContainer"] {
        max-width: 100% !important;
        padding: 22px 26px 24px 26px !important;
    }

    [data-testid="stSidebar"] { background:#041b34; border-right: 1px solid #0f2f55; min-width: 230px !important; max-width: 230px !important; }
    [data-testid="stSidebar"] > div { padding: 26px 18px; }
    [data-testid="stSidebar"] * { color:#eaf3ff; }

    .brand { margin-top: 10px; margin-bottom: 34px; }
    .brand-title { font-size: 24px; line-height:1.08; font-weight:900; color:#ffffff; }
    .brand-sub { font-size: 12px; color:#b9c9de; line-height:1.55; margin-top:12px; font-weight:600; }
    .nav-title { font-size: 12px; letter-spacing:2px; color:#94a8c0; font-weight:900; margin: 0 0 10px 0; }
    div[data-testid="stSidebar"] button {
        width: 100%; border-radius: 13px !important; height: 46px !important;
        background: transparent !important; border: 1px solid rgba(148,168,192,.22) !important;
        color:#eaf3ff !important; font-weight:800 !important; text-align:left !important;
        margin-bottom: 8px !important;
    }
    div[data-testid="stSidebar"] button:hover { background:#0b5bd3 !important; border-color:#0b5bd3 !important; }
    .source-box { position:fixed; bottom:20px; left:18px; width:194px; border:1px solid rgba(148,168,192,.32); border-radius:14px; padding:14px; background:rgba(255,255,255,.03); }
    .source-title { font-size:12px; font-weight:900; color:#fff; }
    .source-text { font-size:11px; color:#b9c9de; line-height:1.55; margin-top:8px; }

    .hero-card {
        background:#fff; border:1px solid #dbe6f2; border-radius:20px; padding:26px 28px;
        box-shadow:0 18px 45px rgba(15,45,75,.08); min-height:112px;
    }
    .hero-title { font-size:30px; font-weight:900; color:#07122c; letter-spacing:-1.1px; white-space:nowrap; }
    .hero-sub { color:#607187; font-size:14px; font-weight:700; margin-top:12px; }

    .filter-wrap { background:transparent; padding-top: 4px; }
    div[data-testid="stButton"] button {
        border-radius:14px !important; border:1px solid #d7e5f4 !important;
        background:#ffffff !important; color:#2563eb !important; font-weight:800 !important;
        min-height:40px !important; box-shadow:0 8px 24px rgba(15,45,75,.05);
    }
    div[data-testid="stButton"] button:hover { background:#eaf3ff !important; border-color:#93c5fd !important; }
    div[data-testid="stSelectbox"] label, div[data-testid="stRadio"] label { color:#50617a !important; font-weight:800 !important; }
    div[data-baseweb="select"] > div { border-radius:12px !important; background:#f6f8fb !important; border:0 !important; min-height:44px; }

    .metric-card {
        height:116px; background:#fff; border:1px solid #dbe6f2; border-radius:16px; padding:18px;
        display:flex; justify-content:space-between; overflow:hidden; box-shadow:0 12px 30px rgba(15,45,75,.06);
    }
    .metric-title { color:#53677f; font-weight:900; font-size:12px; letter-spacing:1.5px; text-transform:uppercase; line-height:1.5; }
    .metric-value { color:#07122c; font-size:30px; line-height:1; font-weight:900; margin-top:12px; }
    .metric-subtitle { color:#8ba0b8; font-size:12px; font-weight:700; margin-top:12px; line-height:1.35; }
    .metric-icon { width:48px; height:48px; border-radius:50%; display:flex; align-items:center; justify-content:center; font-size:23px; font-weight:900; flex:0 0 auto; }
    .metric-icon.blue { background:#e7f1ff; color:#2563eb; }
    .metric-icon.red { background:#ffe4e9; color:#e11d48; }
    .metric-icon.orange { background:#ffedd5; color:#f97316; }
    .metric-icon.purple { background:#ede9fe; color:#7c3aed; }

    .section-card { background:#fff; border:1px solid #dbe6f2; border-radius:16px; box-shadow:0 12px 30px rgba(15,45,75,.055); }
    .section-head { padding:16px 18px; margin-bottom:-2px; border-bottom-left-radius:0; border-bottom-right-radius:0; }
    .section-title { color:#07122c; font-size:16px; font-weight:900; }
    .section-subtitle { color:#607187; font-size:12px; font-weight:700; margin-top:8px; }
    .map-box { background:#fff; border:1px solid #dbe6f2; border-top:0; border-radius:0 0 16px 16px; padding: 0 8px 10px 8px; margin-bottom:14px; box-shadow:0 12px 30px rgba(15,45,75,.055); }

    .table-card { padding:16px 18px; }
    .table-title { color:#07122c; font-size:14px; font-weight:900; margin-bottom:10px; }
    .nice-table { width:100%; border-collapse:collapse; font-size:12px; }
    .nice-table th { text-align:left; color:#53677f; font-size:11px; padding:9px 6px; border-bottom:1px solid #e5edf5; }
    .nice-table td { color:#07122c; padding:10px 6px; border-bottom:1px solid #eef2f7; font-weight:650; }
    .chip { display:inline-block; border-radius:9px; padding:5px 9px; font-size:11px; font-weight:900; }
    .critical { background:#fee2e2; color:#dc2626; }
    .concern { background:#ffedd5; color:#ea580c; }
    .watch { background:#fef3c7; color:#b45309; }
    .stable { background:#dcfce7; color:#16a34a; }

    .detail-panel { background:#fff; border:1px solid #dbe6f2; border-radius:18px; padding:18px; box-shadow:0 16px 35px rgba(15,45,75,.06); }
    .detail-title { color:#07122c; font-size:20px; font-weight:900; margin-bottom:5px; }
    .crumb { color:#6b7c93; font-size:11px; font-weight:800; margin-bottom:16px; }
    .small-card { background:#fff; border:1px solid #dbe6f2; border-radius:14px; padding:16px; min-height:110px; }
    .small-label { color:#53677f; font-weight:900; letter-spacing:1px; font-size:11px; text-transform:uppercase; }
    .small-value { color:#07122c; font-size:28px; font-weight:900; margin:12px 0 8px 0; }
    .small-note { color:#7c8ca3; font-size:11px; font-weight:700; margin-top:8px; line-height:1.35; }

    .alert-box { background:#fff1f2; border:1px solid #fecdd3; border-radius:14px; padding:16px; display:flex; gap:16px; align-items:center; }
    .alert-icon { width:56px; height:56px; border-radius:50%; background:#dc2626; color:#fff; display:flex; align-items:center; justify-content:center; font-size:30px; font-weight:900; }
    .alert-title { font-weight:900; color:#07122c; font-size:14px; }
    .alert-text { color:#26364e; font-size:12px; line-height:1.55; font-weight:650; margin-top:7px; }
    .risk-badge { background:#dc2626; color:#fff; display:inline-block; padding:10px 14px; border-radius:8px; font-size:18px; font-weight:900; margin-top:6px; }
    .info-box { background:#fff; border:1px solid #dbe6f2; border-radius:14px; padding:15px; min-height:132px; }
    .info-title { font-weight:900; color:#07122c; font-size:13px; margin-bottom:8px; }
    .info-text, .info-list { color:#334155; font-size:12px; line-height:1.65; font-weight:650; }

    div[data-testid="column"] { padding-left: 0.42rem !important; padding-right: 0.42rem !important; }
    .block-container div[data-testid="stVerticalBlock"] > div { gap: 0.75rem; }
    </style>
    """,
    unsafe_allow_html=True,
)

# -----------------------------
# Data load
# -----------------------------
@st.cache_data
def load_data():
    path = Path(CSV_NAME)
    if not path.exists():
        st.error(f"ไม่พบไฟล์ {CSV_NAME} กรุณาวางไฟล์ CSV ไว้ในโฟลเดอร์เดียวกับไฟล์ Python นี้")
        st.stop()
    data = pd.read_csv(path)
    data["year_month"] = data["year_month"].astype(str)
    data["Year"] = data["year_month"].str[:4]
    data["Display Name"] = data["data_center_name"].apply(clean_name)
    data["Risk Level"] = data["risk_level"].astype(str).str.title()
    return data

df = load_data()

# -----------------------------
# Session state
# -----------------------------
if "page" not in st.session_state:
    st.session_state.page = "Overview"
if "year" not in st.session_state:
    st.session_state.year = sorted(df["Year"].unique())[-1]
if "month" not in st.session_state:
    st.session_state.month = sorted(df.loc[df["Year"] == st.session_state.year, "year_month"].unique())[-1]
if "risk" not in st.session_state:
    st.session_state.risk = "All"

# -----------------------------
# Sidebar
# -----------------------------
with st.sidebar:
    st.markdown(
        """
        <div class="brand">
            <div class="brand-title">🛡️ DC-Resource<br>Intelligence</div>
            <div class="brand-sub">GeoAI Environmental Monitoring<br>for Data Centers</div>
        </div>
        <div class="nav-title">NAVIGATION</div>
        """,
        unsafe_allow_html=True,
    )
    for item, icon in [
        ("Overview", "▣"), ("Hotspot Detail", "◎"), ("Alerts", "△"), ("Data Centers", "⌂"),
        ("Trends", "↗"), ("Forecast", "◷"), ("Reports", "▤"), ("About", "ⓘ")
    ]:
        if st.button(f"{icon} {item}", key=f"menu_{item}"):
            st.session_state.page = item
    st.markdown(
        """
        <div class="source-box">
            <div class="source-title">Data Source</div>
            <div class="source-text">Google Earth Engine<br>2019 – 2025<br><br>🛰️</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

# -----------------------------
# Filter data
# -----------------------------
year_list = sorted(df["Year"].unique())
month_list = sorted(df.loc[df["Year"] == st.session_state.year, "year_month"].unique())
risk_options = ["All"] + sorted(df["Risk Level"].dropna().unique())

# Keep month valid after year change
if st.session_state.month not in month_list:
    st.session_state.month = month_list[-1]

latest = df[df["year_month"] == st.session_state.month].copy()
if st.session_state.risk != "All":
    latest = latest[latest["Risk Level"] == st.session_state.risk]
if latest.empty:
    latest = df[df["year_month"] == st.session_state.month].copy()

# Hotspot default
hotspot_row = latest.sort_values("risk_score", ascending=False).iloc[0]
hotspot_name = hotspot_row["data_center_name"]

# -----------------------------
# Header + clickable filters in horizontal layout
# -----------------------------
header_col, filter_col = st.columns([3.25, 1.25], gap="large")
with header_col:
    st.markdown(
        """
        <div class="hero-card">
            <div class="hero-title">DC-Resource Intelligence Platform</div>
            <div class="hero-sub">GeoAI-Based Environmental Monitoring and Resource Risk Assessment for Data Centers</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with filter_col:
    st.markdown('<div class="filter-wrap">', unsafe_allow_html=True)
    y_cols = st.columns(len(year_list)) if len(year_list) <= 4 else st.columns(2)
    for i, y in enumerate(year_list):
        with y_cols[i % len(y_cols)]:
            label = f"✓ {y}" if st.session_state.year == y else y
            if st.button(f"📅 {label}", key=f"year_{y}"):
                st.session_state.year = y
                valid_months = sorted(df.loc[df["Year"] == y, "year_month"].unique())
                st.session_state.month = valid_months[-1]
                st.rerun()
    r_cols = st.columns(2)
    for i, r in enumerate(risk_options[:6]):
        with r_cols[i % 2]:
            label = f"✓ {r}" if st.session_state.risk == r else r
            if st.button(f"📌 {label}", key=f"risk_{r}"):
                st.session_state.risk = r
                st.rerun()
    m_cols = st.columns(3)
    for i, m in enumerate(month_list):
        with m_cols[i % 3]:
            label = f"✓ {m}" if st.session_state.month == m else m
            if st.button(label, key=f"month_{m}"):
                st.session_state.month = m
                st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

# -----------------------------
# Main clone layout: left overview + right detail
# -----------------------------
left, right = st.columns([1.42, 1.0], gap="large")

with left:
    # KPI cards
    total_sites = latest["data_center_name"].nunique()
    critical_eci = int((latest["ECI_score"].apply(level_from_eci) == "Critical").sum())
    critical_ess = int((latest["ESS_score"].apply(level_from_ess) == "Critical").sum())
    top_display = clean_name(hotspot_name)

    k1, k2, k3, k4 = st.columns(4)
    with k1:
        metric_card("Monitored Data Centers", total_sites, "Across selected filter", "▦", "blue")
    with k2:
        metric_card("Critical ECI Areas", critical_eci, "High rate of change", "↗", "red")
    with k3:
        metric_card("Critical ESS Areas", critical_ess, "High environmental stress", "⚠", "orange")
    with k4:
        metric_card("Top Hotspot", top_display, "Ranked by risk score", "⌖", "purple")

    map1, map2 = st.columns(2)
    with map1:
        section_header("▧ ECI Map", "Environmental Change Index by data center location")
        st.markdown('<div class="map-box">', unsafe_allow_html=True)
        st.plotly_chart(make_geo_map(latest, "ECI_score", "ECI", "RdYlGn_r"), use_container_width=True, config={"displayModeBar": False})
        st.markdown('</div>', unsafe_allow_html=True)
    with map2:
        section_header("▧ ESS Map", "Environmental Stress Score by data center location")
        st.markdown('<div class="map-box">', unsafe_allow_html=True)
        st.plotly_chart(make_geo_map(latest, "ESS_score", "ESS", "YlOrRd"), use_container_width=True, config={"displayModeBar": False})
        st.markdown('</div>', unsafe_allow_html=True)

    t1, t2 = st.columns(2)
    with t1:
        render_table(latest, "ECI_score", level_from_eci, "▣ Top 5 by Environmental Change")
    with t2:
        render_table(latest, "ESS_score", level_from_ess, "▣ Top 5 by Environmental Stress")

    st.markdown(
        """
        <div class="section-card" style="padding:16px 18px; background:#eef7ff;">
            <b style="color:#2563eb;">ⓘ</b>
            <span style="color:#334155; font-size:12px; font-weight:650; margin-left:8px;">
            DC-Resource Intelligence Platform transforms satellite-derived environmental indicators into early warning insights for infrastructure and decision-makers.</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

with right:
    st.markdown('<div class="detail-panel">', unsafe_allow_html=True)
    st.markdown('<div class="crumb">← Overview › Hotspot Detail</div><div class="detail-title">Hotspot Detail</div>', unsafe_allow_html=True)

    name_options = latest.sort_values("risk_score", ascending=False)["data_center_name"].tolist()
    display_options = [clean_name(x) for x in name_options]
    selected_display = st.selectbox("Select Hotspot", display_options, index=0, key="hotspot_select")
    selected_name = name_options[display_options.index(selected_display)]

    selected_latest = latest[latest["data_center_name"] == selected_name].iloc[0]
    selected_all = df[df["data_center_name"] == selected_name].sort_values("year_month")

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        small_card(clean_name(selected_name), "", None, f"Lat {selected_latest.latitude:.3f}, Lon {selected_latest.longitude:.3f}")
    with c2:
        small_card("ECI Score", f"{selected_latest.ECI_score:.2f}", level_from_eci(selected_latest.ECI_score), "Rate of environmental change")
    with c3:
        small_card("ESS Score", f"{selected_latest.ESS_score:.2f}", level_from_ess(selected_latest.ESS_score), "Current environmental stress")
    with c4:
        key = "High Surface Temperature" if selected_latest.mean_LST_C >= latest.mean_LST_C.median() else "Water Availability Watch"
        small_card("Key Drivers", "3", None, key)

    chart1, chart2 = st.columns(2)
    with chart1:
        st.markdown('<div class="section-card" style="padding:14px;"><div class="table-title">Land Surface Temperature</div>', unsafe_allow_html=True)
        st.plotly_chart(line_chart(selected_all, "mean_LST_C", "LST", "#dc2626"), use_container_width=True, config={"displayModeBar": False})
        st.markdown('</div>', unsafe_allow_html=True)
    with chart2:
        st.markdown('<div class="section-card" style="padding:14px;"><div class="table-title">Water Availability Index</div>', unsafe_allow_html=True)
        st.plotly_chart(line_chart(selected_all, "mean_NDWI", "NDWI", "#2563eb"), use_container_width=True, config={"displayModeBar": False})
        st.markdown('</div>', unsafe_allow_html=True)

    risk_level = str(selected_latest["Risk Level"])
    risk_score = float(selected_latest["risk_score"])
    st.markdown(
        f"""
        <div class="alert-box">
            <div class="alert-icon">!</div>
            <div style="flex:1;">
                <div class="alert-title">AI Alert Summary</div>
                <div class="alert-text">{clean_name(selected_name)} shows elevated environmental stress with current resource pressure. Forecast outputs indicate the risk level should be monitored over the next 6 to 12 months.</div>
            </div>
            <div style="text-align:center;">
                <div class="small-label">Overall Risk Level</div>
                <div class="risk-badge">{risk_level.upper()}</div>
                <div class="small-note">Score {risk_score:.2f}</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    a, b = st.columns(2)
    with a:
        st.markdown(
            """
            <div class="info-box">
                <div class="info-title">What does this mean?</div>
                <div class="info-text">The selected area is monitored for heat stress, water availability, vegetation condition, and built-up pressure around the data center location.</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with b:
        st.markdown(
            """
            <div class="info-box">
                <div class="info-title">Recommended Actions</div>
                <div class="info-list">✓ Monitor local water usage<br>✓ Review cooling efficiency<br>✓ Watch peak heat periods<br>✓ Prepare mitigation planning</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    f6 = selected_latest.get("forecast_risk_score_6m", None)
    f12 = selected_latest.get("forecast_risk_score_12m", None)
    if f6 is not None and f12 is not None:
        p1, p2, p3 = st.columns(3)
        with p1:
            small_card("Current Risk", f"{risk_score:.2f}", risk_level, "Baseline")
        with p2:
            small_card("Forecast 6 Months", f"{float(f6):.2f}", selected_latest.get("forecast_risk_level_6m", "Watch"), "Predictive risk")
        with p3:
            small_card("Forecast 12 Months", f"{float(f12):.2f}", selected_latest.get("forecast_risk_level_12m", "Watch"), "Longer-term risk")

    st.markdown('</div>', unsafe_allow_html=True)

# -----------------------------
# Extra pages are clickable and show filtered content
# -----------------------------
if st.session_state.page != "Overview":
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(
        f"""
        <div class="section-card" style="padding:18px;">
            <div class="section-title">{st.session_state.page}</div>
            <div class="section-subtitle">This section is active. It uses the selected year, month, risk level, and hotspot filters.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
