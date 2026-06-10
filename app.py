import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path

# -----------------------------
# Page setup
# -----------------------------
st.set_page_config(
    page_title="GeoSentinel AI",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded",
)

# -----------------------------
# Dark premium CSS
# -----------------------------
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    .stApp {
        background: radial-gradient(circle at top left, #12345a 0, #07111f 42%, #040914 100%);
        color: #edf6ff;
    }

    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, rgba(7,17,31,.98), rgba(4,9,20,.98));
        border-right: 1px solid rgba(255,255,255,.12);
    }

    section[data-testid="stSidebar"] * {
        color: #edf6ff;
    }

    .main-title {
        font-size: 34px;
        font-weight: 900;
        letter-spacing: -0.04em;
        margin-bottom: 4px;
    }

    .subtitle {
        color: #8fa8c4;
        font-size: 14px;
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
        font-weight: 900;
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
        font-weight: 800;
    }

    .kpi-value {
        font-size: 34px;
        font-weight: 900;
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
        font-size: 18px;
        font-weight: 900;
        margin-bottom: 4px;
    }

    .section-subtitle {
        color: #8fa8c4;
        font-size: 12px;
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
        font-weight: 800;
    }

    div[data-testid="stMetricValue"] {
        color: #edf6ff !important;
        font-weight: 900;
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
# Load data from CSV only
# -----------------------------
DATA_PATH = Path("geosentinel_dashboard_data.csv")

@st.cache_data
def load_data(path: Path) -> pd.DataFrame:
    if not path.exists():
        st.error("ไม่พบไฟล์ geosentinel_dashboard_data.csv กรุณาวางไฟล์ CSV ไว้ในโฟลเดอร์เดียวกับ app.py")
        st.stop()

    data = pd.read_csv(path)

    required_columns = [
        "data_center", "lat", "lon", "mean_LST_C", "mean_NDWI",
        "mean_soil_moisture", "lst_change", "ndwi_change",
        "soil_moisture_change", "ECI", "ESS", "risk_level"
    ]
    missing = [col for col in required_columns if col not in data.columns]
    if missing:
        st.error(f"CSV ขาดคอลัมน์: {', '.join(missing)}")
        st.stop()

    return data


df = load_data(DATA_PATH)

# -----------------------------
# Helpers based only on CSV values
# -----------------------------
def risk_color(level: str) -> str:
    level = str(level).lower()
    if "critical" in level or "red" in level:
        return "#ff425b"
    if "warning" in level or "yellow" in level:
        return "#ffd24a"
    if "safe" in level or "green" in level:
        return "#42d67b"
    return "#20e0ff"


def risk_short(level: str) -> str:
    text = str(level)
    if "(" in text:
        return text.split("(")[0].strip()
    return text


def driver_summary(row: pd.Series) -> list[str]:
    drivers = []
    if row["lst_change"] > 0:
        drivers.append(f"LST เพิ่มขึ้น {row['lst_change']:.2f} °C")
    elif row["lst_change"] < 0:
        drivers.append(f"LST ลดลง {abs(row['lst_change']):.2f} °C")

    if row["ndwi_change"] < 0:
        drivers.append(f"NDWI ลดลง {abs(row['ndwi_change']):.4f}")
    elif row["ndwi_change"] > 0:
        drivers.append(f"NDWI เพิ่มขึ้น {row['ndwi_change']:.4f}")

    if row["soil_moisture_change"] < 0:
        drivers.append(f"Soil Moisture ลดลง {abs(row['soil_moisture_change']):.4f}")
    elif row["soil_moisture_change"] > 0:
        drivers.append(f"Soil Moisture เพิ่มขึ้น {row['soil_moisture_change']:.4f}")

    return drivers


# -----------------------------
# Sidebar
# -----------------------------
with st.sidebar:
    st.markdown("# ⌁ GeoSentinel AI")
    st.caption("Satellite-Powered Environmental Early Warning")
    page = st.radio(
        "Navigation",
        ["▣ Innovation Overview", "⌖ Hotspot Detail", "↗ Evidence Trends", "▤ Raw Data"],
        label_visibility="collapsed",
    )
    st.markdown("---")
    st.markdown("**Data source**")
    st.caption("ใช้ข้อมูลจาก `geosentinel_dashboard_data.csv` เท่านั้น")
    st.markdown("**Records**")
    st.caption(f"{len(df)} data centers")

# -----------------------------
# Header
# -----------------------------
st.markdown('<div class="badge">LIVE DEMO · Hackathon Prototype</div>', unsafe_allow_html=True)
st.markdown('<div class="main-title">GeoSentinel AI Innovation Dashboard</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="subtitle">Satellite-derived environmental monitoring for data centers · values calculated from CSV only</div>',
    unsafe_allow_html=True,
)

# -----------------------------
# Overview Page
# -----------------------------
if page == "▣ Innovation Overview":
    critical_count = int(df["risk_level"].astype(str).str.contains("Critical", case=False, na=False).sum())
    warning_count = int(df["risk_level"].astype(str).str.contains("Warning", case=False, na=False).sum())
    safe_count = int(df["risk_level"].astype(str).str.contains("Safe", case=False, na=False).sum())

    top_eci = df.loc[df["ECI"].idxmax()]
    top_ess = df.loc[df["ESS"].idxmax()]

    k1, k2, k3, k4 = st.columns(4)
    with k1:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">Monitored Data Centers</div>
            <div class="kpi-value cyan">{len(df)}</div>
            <div class="kpi-note">CSV records</div>
        </div>
        """, unsafe_allow_html=True)
    with k2:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">Critical Hotspots</div>
            <div class="kpi-value red">{critical_count}</div>
            <div class="kpi-note">from risk_level column</div>
        </div>
        """, unsafe_allow_html=True)
    with k3:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">Highest ECI</div>
            <div class="kpi-value yellow">{top_eci['ECI']:.2f}</div>
            <div class="kpi-note">{top_eci['data_center']}</div>
        </div>
        """, unsafe_allow_html=True)
    with k4:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">Highest ESS</div>
            <div class="kpi-value green">{top_ess['ESS']:.2f}</div>
            <div class="kpi-note">{top_ess['data_center']}</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    left, right = st.columns([1.35, 0.65])

    with left:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">1. Monitor + Detect: Environmental Hotspot Map</div>', unsafe_allow_html=True)
        st.markdown(
            '<div class="section-subtitle">ตำแหน่ง Data Center และสีความเสี่ยงมาจาก lat, lon และ risk_level ใน CSV</div>',
            unsafe_allow_html=True,
        )

        map_df = df.copy()
        map_df["risk_display"] = map_df["risk_level"].apply(risk_short)
        map_df["color"] = map_df["risk_level"].apply(risk_color)

        fig_map = px.scatter_mapbox(
            map_df,
            lat="lat",
            lon="lon",
            color="risk_display",
            size="ECI",
            size_max=22,
            zoom=3,
            height=520,
            hover_name="data_center",
            hover_data={
                "lat": ":.3f",
                "lon": ":.3f",
                "mean_LST_C": ":.2f",
                "mean_NDWI": ":.4f",
                "mean_soil_moisture": ":.4f",
                "ECI": ":.2f",
                "ESS": ":.2f",
                "risk_display": False,
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
            font=dict(color="#edf6ff"),
            margin=dict(l=0, r=0, t=0, b=0),
            legend_title_text="Risk Level",
        )
        st.plotly_chart(fig_map, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with right:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">Top Risk Ranking</div>', unsafe_allow_html=True)
        st.markdown('<div class="section-subtitle">เรียงตาม ECI จากข้อมูลจริงใน CSV</div>', unsafe_allow_html=True)
        rank_df = df.sort_values("ECI", ascending=False)[["data_center", "ECI", "ESS", "risk_level"]].copy()
        rank_df.insert(0, "rank", range(1, len(rank_df) + 1))
        st.dataframe(rank_df, use_container_width=True, hide_index=True)
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">Risk Level Summary</div>', unsafe_allow_html=True)
        st.markdown('<div class="section-subtitle">นับจำนวนจาก risk_level column</div>', unsafe_allow_html=True)
        summary = pd.DataFrame({
            "Risk Level": ["Critical", "Warning", "Safe"],
            "Count": [critical_count, warning_count, safe_count],
        })
        fig_bar = px.bar(
            summary,
            x="Risk Level",
            y="Count",
            color="Risk Level",
            color_discrete_map={"Critical": "#ff425b", "Warning": "#ffd24a", "Safe": "#42d67b"},
            height=260,
        )
        fig_bar.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#edf6ff"),
            margin=dict(l=0, r=0, t=10, b=0),
            showlegend=False,
        )
        st.plotly_chart(fig_bar, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

# -----------------------------
# Hotspot Detail Page
# -----------------------------
elif page == "⌖ Hotspot Detail":
    selected_dc = st.selectbox("Select Data Center", df["data_center"].tolist())
    row = df[df["data_center"] == selected_dc].iloc[0]

    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown(f'<div class="section-title">Selected Hotspot: {selected_dc}</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-subtitle">ค่าทั้งหมดอ่านจากแถวของ Data Center ที่เลือกใน CSV</div>', unsafe_allow_html=True)

    a, b, c, d = st.columns(4)
    a.metric("Risk Level", row["risk_level"])
    b.metric("ECI", f"{row['ECI']:.2f}")
    c.metric("ESS", f"{row['ESS']:.2f}")
    d.metric("LST", f"{row['mean_LST_C']:.2f} °C")

    e, f, g = st.columns(3)
    e.metric("NDWI", f"{row['mean_NDWI']:.4f}")
    f.metric("Soil Moisture", f"{row['mean_soil_moisture']:.4f}")
    g.metric("Location", f"{row['lat']:.3f}, {row['lon']:.3f}")
    st.markdown('</div>', unsafe_allow_html=True)

    col1, col2 = st.columns([0.55, 0.45])
    with col1:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">Environmental Indicators</div>', unsafe_allow_html=True)
        indicator_df = pd.DataFrame({
            "Indicator": ["mean_LST_C", "mean_NDWI", "mean_soil_moisture", "lst_change", "ndwi_change", "soil_moisture_change", "ECI", "ESS"],
            "Value": [row["mean_LST_C"], row["mean_NDWI"], row["mean_soil_moisture"], row["lst_change"], row["ndwi_change"], row["soil_moisture_change"], row["ECI"], row["ESS"]],
        })
        fig = px.bar(indicator_df, x="Indicator", y="Value", color="Indicator", height=430)
        fig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#edf6ff"),
            margin=dict(l=0, r=0, t=10, b=0),
            showlegend=False,
        )
        st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">AI Insight Summary</div>', unsafe_allow_html=True)
        drivers = driver_summary(row)
        driver_text = "<br>".join([f"• {d}" for d in drivers]) if drivers else "ไม่มีค่า change ที่เด่นจาก CSV"
        st.markdown(
            f"""
            <div class="insight-box">
                <div class="bot-icon">🤖</div>
                <div>
                    <b>{selected_dc}</b><br>
                    <div class="mini-text">
                    Risk level จาก CSV: <b>{row['risk_level']}</b><br><br>
                    Evidence from CSV:<br>{driver_text}
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.info("หมายเหตุ: ส่วนนี้เป็น rule-based explanation จากคอลัมน์ change ใน CSV ไม่ได้เมคตัวเลขใหม่")
        st.markdown('</div>', unsafe_allow_html=True)

# -----------------------------
# Evidence Trends Page
# -----------------------------
elif page == "↗ Evidence Trends":
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">2. Evidence Trends from CSV</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-subtitle">ใช้ lst_change, ndwi_change และ soil_moisture_change แทน Forecast ที่ยังไม่มีข้อมูลจริง</div>', unsafe_allow_html=True)

    trend_df = df[["data_center", "lst_change", "ndwi_change", "soil_moisture_change", "risk_level"]].copy()
    fig = go.Figure()
    fig.add_trace(go.Bar(name="LST Change", x=trend_df["data_center"], y=trend_df["lst_change"], marker_color="#ff425b"))
    fig.add_trace(go.Bar(name="NDWI Change", x=trend_df["data_center"], y=trend_df["ndwi_change"], marker_color="#20e0ff"))
    fig.add_trace(go.Bar(name="Soil Moisture Change", x=trend_df["data_center"], y=trend_df["soil_moisture_change"], marker_color="#42d67b"))
    fig.update_layout(
        barmode="group",
        height=520,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#edf6ff"),
        margin=dict(l=0, r=0, t=20, b=0),
        xaxis_tickangle=-35,
    )
    st.plotly_chart(fig, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">3. Recommendation Evidence</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="section-subtitle">แสดงข้อสรุปตามหลักฐานจาก CSV เท่านั้น ยังไม่ใส่ expected impact ที่ไม่มีข้อมูลรองรับ</div>',
        unsafe_allow_html=True,
    )
    for _, r in df.sort_values("ECI", ascending=False).head(5).iterrows():
        drivers = "; ".join(driver_summary(r))
        st.markdown(f"**{r['data_center']}** — Risk: `{r['risk_level']}` · ECI: `{r['ECI']:.2f}` · ESS: `{r['ESS']:.2f}`")
        st.caption(drivers if drivers else "No change evidence available")
    st.markdown('</div>', unsafe_allow_html=True)

# -----------------------------
# Raw Data Page
# -----------------------------
else:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Raw CSV Data</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-subtitle">ข้อมูลต้นทางที่ Dashboard ใช้ทั้งหมด</div>', unsafe_allow_html=True)
    st.dataframe(df, use_container_width=True, hide_index=True)
    st.download_button(
        "Download CSV",
        df.to_csv(index=False).encode("utf-8"),
        file_name="geosentinel_dashboard_data.csv",
        mime="text/csv",
    )
    st.markdown('</div>', unsafe_allow_html=True)
