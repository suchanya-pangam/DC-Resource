import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path

# =========================================================
# DC-Resource Intelligence Platform
# Run: streamlit run geop.py
# Put CSV in same folder: geosentinel_monthly_dashboard_data.csv
# =========================================================

st.set_page_config(
    page_title="DC-Resource Intelligence Platform",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

DATA_FILE = Path("geosentinel_monthly_dashboard_data.csv")

# ---------- CSS ----------
st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

html, body, [class*="css"] {font-family: 'Inter', sans-serif;}
.block-container {padding-top: 1.4rem; padding-left: 1.8rem; padding-right: 1.8rem; background:#f7fbff;}
section[data-testid="stSidebar"] {background: linear-gradient(180deg,#061b2e 0%,#03111f 100%);}
section[data-testid="stSidebar"] * {color: #eef7ff !important;}
[data-testid="stMetricValue"] {font-size: 30px; font-weight: 800;}

.hero-title {font-size: 30px; font-weight: 800; color:#0b1b33; margin-bottom:0px;}
.hero-sub {color:#53677f; font-size:15px; margin-top:3px;}
.card {
    background: rgba(255,255,255,0.94);
    border: 1px solid #dbe7f3;
    border-radius: 18px;
    padding: 18px 18px;
    box-shadow: 0 8px 26px rgba(20,55,90,.07);
}
.kpi-card {
    min-height: 128px;
    background: white;
    border: 1px solid #dbe7f3;
    border-radius: 18px;
    padding: 18px;
    box-shadow: 0 8px 26px rgba(20,55,90,.07);
}
.kpi-label {font-size:14px; color:#233853; font-weight:700;}
.kpi-value {font-size:38px; color:#06172d; font-weight:800; line-height:1.15;}
.kpi-caption {font-size:13px; color:#65778d; margin-top:8px;}
.badge-low {background:#dcfce7; color:#166534; padding:5px 10px; border-radius:999px; font-weight:700; font-size:12px;}
.badge-watch {background:#fef3c7; color:#92400e; padding:5px 10px; border-radius:999px; font-weight:700; font-size:12px;}
.badge-concern {background:#ffedd5; color:#c2410c; padding:5px 10px; border-radius:999px; font-weight:700; font-size:12px;}
.badge-critical {background:#fee2e2; color:#b91c1c; padding:5px 10px; border-radius:999px; font-weight:700; font-size:12px;}
.alert-card {
    background: linear-gradient(90deg,#fff1f2,#ffffff);
    border: 1px solid #fecaca;
    border-radius: 18px;
    padding: 18px;
}
.info-strip {
    background: linear-gradient(90deg,#eaf4ff,#f8fbff);
    border: 1px solid #dbeafe;
    border-radius: 16px;
    padding: 16px;
    color:#0f2942;
}
.small-muted {font-size:13px; color:#64748b;}
.footer {
    background:#061b2e; color:white; border-radius:14px; padding:16px 18px; margin-top:12px;
}
</style>
""",
    unsafe_allow_html=True,
)

# ---------- Helpers ----------
@st.cache_data
def load_data(uploaded_file=None):
    if uploaded_file is not None:
        df = pd.read_csv(uploaded_file)
    elif DATA_FILE.exists():
        df = pd.read_csv(DATA_FILE)
    else:
        st.error("ไม่พบไฟล์ geosentinel_monthly_dashboard_data.csv กรุณาวางไฟล์ไว้โฟลเดอร์เดียวกับ geop.py")
        st.stop()

    df["year_month"] = pd.to_datetime(df["year_month"])
    numeric_cols = df.select_dtypes(include="number").columns
    df[numeric_cols] = df[numeric_cols].apply(pd.to_numeric, errors="coerce")
    return df


def level_badge(level):
    level = str(level)
    cls = "badge-low"
    if level.lower() == "watch":
        cls = "badge-watch"
    elif level.lower() == "concern":
        cls = "badge-concern"
    elif level.lower() == "critical":
        cls = "badge-critical"
    return f'<span class="{cls}">{level}</span>'


def risk_color(level):
    level = str(level).lower()
    if level == "critical": return "#dc2626"
    if level == "concern": return "#f97316"
    if level == "watch": return "#facc15"
    return "#22c55e"


def risk_sort_value(level):
    order = {"Low": 1, "Watch": 2, "Concern": 3, "Critical": 4}
    return order.get(str(level), 0)


def kpi_card(title, value, caption, icon="📍", accent="#dbeafe"):
    st.markdown(
        f"""
        <div class="kpi-card">
            <div style="display:flex;gap:14px;align-items:center;">
                <div style="width:54px;height:54px;border-radius:50%;background:{accent};display:flex;align-items:center;justify-content:center;font-size:27px;">{icon}</div>
                <div>
                    <div class="kpi-label">{title}</div>
                    <div class="kpi-value">{value}</div>
                </div>
            </div>
            <div class="kpi-caption">{caption}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def clean_table(df):
    out = df.copy()
    out["year_month"] = out["year_month"].dt.strftime("%Y-%m")
    return out


def make_map(df, score_col, title, color_mode="risk"):
    plot_df = df.copy()
    plot_df["color"] = plot_df["risk_level"].apply(risk_color)
    plot_df["size"] = plot_df[score_col].rank(pct=True) * 16 + 10

    fig = go.Figure()
    fig.add_trace(go.Scattergeo(
        lon=plot_df["longitude"],
        lat=plot_df["latitude"],
        text=plot_df["data_center_name"],
        customdata=plot_df[[score_col, "risk_level", "mean_LST_C", "mean_NDWI"]],
        mode="markers",
        marker=dict(
            size=plot_df["size"],
            color=plot_df["color"],
            line=dict(width=1.5, color="white"),
            opacity=0.86,
        ),
        hovertemplate=(
            "<b>%{text}</b><br>"
            + f"{score_col}: %{{customdata[0]:.2f}}<br>"
            + "Risk: %{customdata[1]}<br>"
            + "LST: %{customdata[2]:.2f} °C<br>"
            + "NDWI: %{customdata[3]:.2f}<extra></extra>"
        ),
    ))
    fig.update_layout(
        height=430,
        margin=dict(l=0, r=0, t=30, b=0),
        paper_bgcolor="white",
        plot_bgcolor="white",
        title=dict(text=title, font=dict(size=15, color="#0f172a")),
        geo=dict(
            scope="usa",
            projection_type="albers usa",
            showland=True,
            landcolor="#f8fafc",
            showocean=True,
            oceancolor="#e0f2fe",
            showlakes=True,
            lakecolor="#dbeafe",
            subunitcolor="#d1d5db",
            countrycolor="#d1d5db",
            bgcolor="rgba(0,0,0,0)",
        ),
        showlegend=False,
    )
    return fig


def line_chart(ts, y, title, color=None):
    fig = px.line(ts, x="year_month", y=y, markers=True)
    fig.update_traces(line=dict(width=3), marker=dict(size=6), fill="tozeroy")
    fig.update_layout(
        title=title,
        height=285,
        margin=dict(l=10, r=10, t=45, b=10),
        paper_bgcolor="white",
        plot_bgcolor="white",
        xaxis_title="",
        yaxis_title="",
        font=dict(color="#172033"),
    )
    fig.update_xaxes(showgrid=True, gridcolor="#eef2f7")
    fig.update_yaxes(showgrid=True, gridcolor="#eef2f7")
    return fig


def forecast_chart(row):
    names = ["Current", "6 Months", "12 Months"]
    vals = [row["risk_score"], row["forecast_risk_score_6m"], row["forecast_risk_score_12m"]]
    fig = go.Figure(go.Bar(x=names, y=vals, text=[f"{v:.1f}" for v in vals], textposition="outside"))
    fig.update_layout(
        title="AI Risk Forecast",
        height=300,
        margin=dict(l=10, r=10, t=45, b=10),
        yaxis=dict(range=[0, 100], title="Risk Score"),
        xaxis_title="",
        paper_bgcolor="white",
        plot_bgcolor="white",
    )
    fig.update_yaxes(showgrid=True, gridcolor="#eef2f7")
    return fig

# ---------- Load Data ----------
with st.sidebar:
    st.markdown("## 🛡️ GeoSentinel AI")
    st.caption("Environmental Early Warning System")
    st.markdown("---")
    uploaded = st.file_uploader("Upload CSV", type=["csv"], label_visibility="collapsed")

df = load_data(uploaded)
months = sorted(df["year_month"].unique())
latest_month = max(months)

# ---------- Sidebar ----------
with st.sidebar:
    page = st.radio(
        "Navigation",
        ["Overview", "Hotspot Detail", "Alerts", "Data Centers", "Trends", "Forecast", "Reports", "About"],
        label_visibility="collapsed",
    )
    selected_month = st.selectbox(
        "Analysis Month",
        months,
        index=len(months)-1,
        format_func=lambda x: pd.to_datetime(x).strftime("%b %Y"),
    )
    st.markdown("---")
    st.markdown("### Data Source")
    st.caption("Google Earth Engine\n2019 – 2025")
    st.markdown("🛰️")

latest = df[df["year_month"] == selected_month].copy()
latest["risk_rank"] = latest["risk_level"].apply(risk_sort_value)
latest = latest.sort_values(["risk_rank", "risk_score"], ascending=False)
top_hotspot = latest.iloc[0]

# ---------- Overview ----------
if page == "Overview":
    c1, c2 = st.columns([0.72, 0.28])
    with c1:
        st.markdown('<div class="hero-title">Overview Dashboard</div>', unsafe_allow_html=True)
        st.markdown('<div class="hero-sub">Real-time environmental monitoring of data centers across the United States</div>', unsafe_allow_html=True)
    with c2:
        st.selectbox("Date", months, index=list(months).index(selected_month), format_func=lambda x: pd.to_datetime(x).strftime("%b %d, %Y"), key="date_top")

    k1, k2, k3, k4 = st.columns(4)
    with k1: kpi_card("Monitored Data Centers", latest["data_center_name"].nunique(), "Across the United States", "🗄️", "#dbeafe")
    with k2: kpi_card("Critical ECI Areas", int((latest["ECI_score"] >= 1.0).sum()), "High rate of change", "📈", "#fee2e2")
    with k3: kpi_card("Critical ESS Areas", int((latest["ESS_score"] >= 60).sum()), "High environmental stress", "⚠️", "#ffedd5")
    with k4:
        st.markdown(
            f"""
            <div class="kpi-card">
                <div class="kpi-label">Top Hotspot</div>
                <div style="font-size:21px;font-weight:800;color:#6d28d9;margin-top:12px;">{top_hotspot['data_center_name']}</div>
                <div class="kpi-caption">ECI: {top_hotspot['ECI_score']:.2f} &nbsp; ESS: {top_hotspot['ESS_score']:.2f}</div>
                <div style="margin-top:8px;">{level_badge(top_hotspot['risk_level'])}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.write("")
    m1, m2 = st.columns(2)
    with m1:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.plotly_chart(make_map(latest, "ECI_score", "ECI Map (Environmental Change Index)"), use_container_width=True)
        st.markdown("**ECI Risk Level:** 🟢 Stable &nbsp; 🟡 Watch &nbsp; 🟠 Concern &nbsp; 🔴 Critical")
        st.markdown('</div>', unsafe_allow_html=True)
    with m2:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.plotly_chart(make_map(latest, "ESS_score", "ESS Map (Environmental Stress Score)"), use_container_width=True)
        st.markdown("**ESS Risk Level:** 🟢 Low &nbsp; 🟡 Moderate &nbsp; 🟠 High &nbsp; 🔴 Critical")
        st.markdown('</div>', unsafe_allow_html=True)

    t1, t2 = st.columns(2)
    with t1:
        st.markdown("### 📊 Top 5 by Environmental Change (ECI)")
        top_eci = latest.nlargest(5, "ECI_score")[["data_center_name", "ECI_score", "risk_level", "lst_change_1y", "ndwi_change_1y"]]
        st.dataframe(top_eci, use_container_width=True, hide_index=True)
    with t2:
        st.markdown("### 📊 Top 5 by Environmental Stress (ESS)")
        top_ess = latest.nlargest(5, "ESS_score")[["data_center_name", "ESS_score", "risk_level", "mean_LST_C", "mean_NDWI"]]
        st.dataframe(top_ess, use_container_width=True, hide_index=True)

    st.markdown(
        """
        <div class="info-strip">
        ℹ️ GeoSentinel AI transforms satellite-derived environmental indicators into early warning insights for communities and decision-makers. &nbsp;&nbsp;
        🧪 ECI detects rapid environmental change. &nbsp;&nbsp; ⚠️ ESS detects high current environmental stress.
        </div>
        """,
        unsafe_allow_html=True,
    )

# ---------- Hotspot Detail ----------
elif page == "Hotspot Detail":
    st.markdown('<div class="hero-title">Hotspot Detail</div>', unsafe_allow_html=True)
    dc = st.selectbox("Select Data Center", sorted(df["data_center_name"].unique()), index=sorted(df["data_center_name"].unique()).index(top_hotspot["data_center_name"]))
    ts = df[df["data_center_name"] == dc].sort_values("year_month")
    row = ts[ts["year_month"] == selected_month]
    if row.empty:
        row = ts.iloc[[-1]]
    row = row.iloc[0]

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        kpi_card(dc, "USA", f"Lat {row['latitude']:.2f}, Lon {row['longitude']:.2f}", "📍", "#f8fafc")
    with c2:
        kpi_card("ECI Score", f"{row['ECI_score']:.2f}", str(row["risk_level"]), "📈", "#fee2e2")
    with c3:
        kpi_card("ESS Score", f"{row['ESS_score']:.2f}", "High environmental stress" if row["ESS_score"] >= 60 else "Moderate environmental stress", "⚠️", "#ffedd5")
    with c4:
        st.markdown(
            f"""
            <div class="kpi-card">
            <div class="kpi-label">Key Drivers</div><br>
            🌡️ Land Surface Temperature<br>
            🌿 Vegetation Health<br>
            💧 Water Availability<br><br>
            {level_badge(row['risk_level'])}
            </div>
            """,
            unsafe_allow_html=True,
        )

    g1, g2 = st.columns(2)
    with g1:
        st.plotly_chart(line_chart(ts, "mean_LST_C", "Land Surface Temperature (LST)"), use_container_width=True)
    with g2:
        st.plotly_chart(line_chart(ts, "mean_NDWI", "Normalized Difference Water Index (NDWI)"), use_container_width=True)

    st.markdown(
        f"""
        <div class="alert-card">
        <h3>🚨 AI Alert Summary</h3>
        <b>{dc}</b> shows current risk level as {row['risk_level']}. Current ECI is <b>{row['ECI_score']:.2f}</b> and ESS is <b>{row['ESS_score']:.2f}</b>.
        Forecast risk is expected to reach <b>{row['forecast_risk_score_6m']:.2f}</b> in 6 months and <b>{row['forecast_risk_score_12m']:.2f}</b> in 12 months.
        <div style="float:right;margin-top:-54px;text-align:center;"><span class="badge-critical" style="font-size:20px;">{row['risk_level']}</span><br><span class="small-muted">Overall Risk Level</span></div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    a1, a2 = st.columns(2)
    with a1:
        st.markdown("### What does this mean?")
        st.info("The environment around this data center may be under heat, water, or vegetation stress. Monitor changes and prioritize mitigation when forecast risk is rising.")
    with a2:
        st.markdown("### Recommended Actions")
        st.success("✅ Monitor local water storage and usage")
        st.success("✅ Avoid outdoor activity during peak heat hours")
        st.success("✅ Save water and use efficiently")
        st.success("✅ Report to local authority if water shortage continues")

# ---------- Alerts ----------
elif page == "Alerts":
    st.markdown('<div class="hero-title">Community Alert</div>', unsafe_allow_html=True)
    critical = latest[latest["risk_level"].eq("Critical")].copy()
    if critical.empty:
        critical = latest.nlargest(5, "risk_score")
    for _, r in critical.iterrows():
        st.markdown(
            f"""
            <div class="alert-card">
            <h3>🚨 {r['data_center_name']} — {r['risk_level']}</h3>
            Issue detected: High Heat Stress and Water Stress<br>
            Current Risk Score: <b>{r['risk_score']:.2f}</b> | Forecast 6M: <b>{r['forecast_risk_score_6m']:.2f}</b> | Forecast 12M: <b>{r['forecast_risk_score_12m']:.2f}</b>
            </div><br>
            """,
            unsafe_allow_html=True,
        )

# ---------- Data Centers ----------
elif page == "Data Centers":
    st.markdown('<div class="hero-title">Data Centers</div>', unsafe_allow_html=True)
    cols = ["data_center_name", "latitude", "longitude", "mean_LST_C", "mean_NDWI", "mean_NDVI", "mean_NDBI", "ECI_score", "ESS_score", "risk_score", "risk_level"]
    st.dataframe(latest[cols], use_container_width=True, hide_index=True)

# ---------- Trends ----------
elif page == "Trends":
    st.markdown('<div class="hero-title">Environmental Trends</div>', unsafe_allow_html=True)
    dc = st.selectbox("Select Data Center", sorted(df["data_center_name"].unique()))
    ts = df[df["data_center_name"] == dc].sort_values("year_month")
    c1, c2 = st.columns(2)
    with c1:
        st.plotly_chart(line_chart(ts, "mean_LST_C", "LST Trend"), use_container_width=True)
        st.plotly_chart(line_chart(ts, "mean_NDVI", "NDVI Trend"), use_container_width=True)
    with c2:
        st.plotly_chart(line_chart(ts, "mean_NDWI", "NDWI Trend"), use_container_width=True)
        st.plotly_chart(line_chart(ts, "soil_moisture", "Soil Moisture Trend"), use_container_width=True)

# ---------- Forecast ----------
elif page == "Forecast":
    st.markdown('<div class="hero-title">AI Forecast Center</div>', unsafe_allow_html=True)
    dc = st.selectbox("Select Data Center", sorted(df["data_center_name"].unique()))
    ts = df[df["data_center_name"] == dc].sort_values("year_month")
    row = ts[ts["year_month"] == selected_month]
    if row.empty:
        row = ts.iloc[[-1]]
    row = row.iloc[0]

    c1, c2, c3 = st.columns(3)
    with c1: kpi_card("Current Risk", f"{row['risk_score']:.1f}", str(row["risk_level"]), "📍", "#dbeafe")
    with c2: kpi_card("Forecast 6M", f"{row['forecast_risk_score_6m']:.1f}", str(row["forecast_risk_level_6m"]), "🔮", "#ede9fe")
    with c3: kpi_card("Forecast 12M", f"{row['forecast_risk_score_12m']:.1f}", str(row["forecast_risk_level_12m"]), "🚀", "#fee2e2")
    st.plotly_chart(forecast_chart(row), use_container_width=True)

    delta12 = row["forecast_risk_score_12m"] - row["risk_score"]
    if delta12 > 10:
        st.error(f"Rising Risk: forecast increases by {delta12:.1f} points within 12 months.")
    elif delta12 > 0:
        st.warning(f"Slightly Rising Risk: forecast increases by {delta12:.1f} points within 12 months.")
    else:
        st.success(f"Stable or improving risk trend: forecast changes by {delta12:.1f} points.")

# ---------- Reports ----------
elif page == "Reports":
    st.markdown('<div class="hero-title">Reports</div>', unsafe_allow_html=True)
    summary = latest.groupby("risk_level").agg(
        data_centers=("data_center_name", "count"),
        avg_ECI=("ECI_score", "mean"),
        avg_ESS=("ESS_score", "mean"),
        avg_risk=("risk_score", "mean"),
        avg_forecast_12m=("forecast_risk_score_12m", "mean"),
    ).reset_index()
    st.dataframe(summary, use_container_width=True, hide_index=True)
    st.download_button("Download latest month report CSV", latest.to_csv(index=False), "geosentinel_latest_report.csv", "text/csv")

# ---------- About ----------
else:
    st.markdown('<div class="hero-title">About GeoSentinel AI</div>', unsafe_allow_html=True)
    st.markdown(
        """
        <div class="card">
        <h3>GeoAI-Based Environmental Monitoring and Resource Risk Assessment for Data Centers</h3>
        <p>This prototype combines satellite-derived environmental indicators, Environmental Change Index (ECI), Environmental Stress Score (ESS), Risk Engine, and AI Forecast to support early warning for data center environmental risk.</p>
        <b>Core indicators:</b><br>
        • Land Surface Temperature (LST)<br>
        • NDWI for water availability<br>
        • NDVI for vegetation health<br>
        • NDBI for built-up intensity<br>
        • Soil moisture and precipitation<br>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.markdown('<div class="footer">🛡️ GeoSentinel AI &nbsp; | &nbsp; Data Source: Google Earth Engine &nbsp; | &nbsp; 2019–2025</div>', unsafe_allow_html=True)
