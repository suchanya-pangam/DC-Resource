import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path

# =========================================================
# DC-Resource Intelligence Platform
# File: GEO_FINAL.py
# Data source: geosentinel_dashboard_data.csv only
# =========================================================

st.set_page_config(
    page_title="DC-Resource Intelligence Platform",
    page_icon="🌐",
    layout="wide",
    initial_sidebar_state="expanded",
)

REQUIRED_COLUMNS = [
    "data_center", "lat", "lon", "mean_LST_C", "mean_NDWI",
    "mean_soil_moisture", "lst_change", "ndwi_change",
    "soil_moisture_change", "ECI", "ESS", "risk_level"
]

# -----------------------------
# Helper functions
# -----------------------------
def clean_risk_label(value):
    text = str(value).strip()
    if "(" in text:
        text = text.split("(")[0].strip()

    lower = text.lower()
    if lower in ["red", "critical risk", "high risk"]:
        return "Critical"
    if lower in ["yellow", "warning", "moderate risk"]:
        return "Warning"
    if lower in ["green", "safe", "low risk"]:
        return "Safe"
    return text


def risk_badge_class(value):
    text = str(value).lower()
    if "critical" in text:
        return "risk-critical"
    if "warning" in text:
        return "risk-warning"
    if "safe" in text:
        return "risk-safe"
    return "risk-default"


def compute_priority_score(data):
    eci_rank = data["ECI"].rank(pct=True)
    ess_rank = data["ESS"].rank(pct=True)
    return ((eci_rank + ess_rank) / 2 * 100).round(1)


def classify_change_direction(row):
    negative = 0
    positive = 0

    if row["lst_change"] > 0:
        negative += 1
    elif row["lst_change"] < 0:
        positive += 1

    if row["ndwi_change"] < 0:
        negative += 1
    elif row["ndwi_change"] > 0:
        positive += 1

    if row["soil_moisture_change"] < 0:
        negative += 1
    elif row["soil_moisture_change"] > 0:
        positive += 1

    if negative >= 2:
        return "Environmental Pressure Increasing"
    if negative == 1:
        return "Early Warning Signal Detected"
    if positive >= 2:
        return "Environmental Condition Improving"
    return "No Major Change Signal"


def classify_outlook(row):
    if "Critical" in str(row["Risk Classification"]):
        return "Immediate Monitoring Priority"
    if row["Change Direction"] == "Environmental Pressure Increasing":
        return "Forward Monitoring Required"
    if row["Change Direction"] == "Early Warning Signal Detected":
        return "Continued Observation Required"
    return "Routine Monitoring"


def evidence_points(row):
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

    if not points:
        points.append("No major change signal is available from the CSV indicators.")

    return points


def build_recommendations(row):
    recommendations = []

    if row["lst_change"] > 0:
        recommendations.append((
            "🌡️ Thermal Mitigation Strategy",
            "Review cooling efficiency, reflective surface planning, and heat-reduction landscape design around the selected facility.",
            "Triggered by positive temperature change from CSV."
        ))

    if row["ndwi_change"] < 0:
        recommendations.append((
            "💧 Water Resource Monitoring",
            "Increase monitoring of surface-water availability and review operational water demand under environmental pressure.",
            "Triggered by decreasing surface water availability from CSV."
        ))

    if row["soil_moisture_change"] < 0:
        recommendations.append((
            "🌱 Green Buffer Enhancement",
            "Maintain vegetation buffers and land-cover interventions to support soil-water retention around the facility.",
            "Triggered by decreasing soil water content from CSV."
        ))

    if not recommendations:
        recommendations.append((
            "✅ Routine Environmental Surveillance",
            "Maintain periodic satellite-based monitoring because current CSV indicators do not show multiple negative change signals.",
            "Triggered by stable or improving CSV indicators."
        ))

    return recommendations


@st.cache_data
def load_data():
    path = Path("geosentinel_dashboard_data.csv")

    if not path.exists():
        st.error("ไม่พบไฟล์ geosentinel_dashboard_data.csv กรุณาวางไฟล์ไว้ในโฟลเดอร์เดียวกับ GEO_FINAL.py")
        st.stop()

    data = pd.read_csv(path)

    missing = [col for col in REQUIRED_COLUMNS if col not in data.columns]
    if missing:
        st.error("CSV ขาดคอลัมน์ที่จำเป็น: " + ", ".join(missing))
        st.stop()

    numeric_cols = [
        "lat", "lon", "mean_LST_C", "mean_NDWI",
        "mean_soil_moisture", "lst_change", "ndwi_change",
        "soil_moisture_change", "ECI", "ESS"
    ]

    for col in numeric_cols:
        data[col] = pd.to_numeric(data[col], errors="coerce")

    data = data.dropna(subset=["lat", "lon", "ECI", "ESS"]).copy()
    data["Monitored Facility"] = data["data_center"].astype(str).str.replace("_", " ", regex=False)
    data["Risk Classification"] = data["risk_level"].apply(clean_risk_label)
    data["Priority Score"] = compute_priority_score(data)
    data["Change Direction"] = data.apply(classify_change_direction, axis=1)
    data["Risk Outlook"] = data.apply(classify_outlook, axis=1)

    return data


def style_figure(fig, height=None):
    if height:
        fig.update_layout(height=height)

    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Raleway", color="#f7fbff", size=11),
        margin=dict(l=0, r=0, t=20, b=0),
        legend=dict(font=dict(color="#e5f1ff", size=10), bgcolor="rgba(0,0,0,0)")
    )

    fig.update_xaxes(
        gridcolor="rgba(255,255,255,.08)",
        tickfont=dict(size=10, color="#d7e7f7"),
        title_font=dict(size=11, color="#d7e7f7")
    )

    fig.update_yaxes(
        gridcolor="rgba(255,255,255,.08)",
        tickfont=dict(size=10, color="#d7e7f7"),
        title_font=dict(size=11, color="#d7e7f7")
    )

    return fig


def render_kpi(label, value, note, color_class="cyan"):
    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-label">{label}</div>
            <div class="kpi-value {color_class}">{value}</div>
            <div class="kpi-note">{note}</div>
        </div>
        """,
        unsafe_allow_html=True
    )


def render_ranking_cards(rank_df):
    for idx, (_, row) in enumerate(rank_df.iterrows(), start=1):
        badge = risk_badge_class(row["Risk Classification"])
        st.markdown(
            f"""
            <div class="ranking-row">
                <div class="rank-number">#{idx}</div>
                <div class="rank-name">{row['Monitored Facility']}</div>
                <div class="rank-score">{row['Priority Score']:.1f}</div>
                <div class="risk-badge {badge}">{row['Risk Classification']}</div>
            </div>
            """,
            unsafe_allow_html=True
        )


def render_prediction_cards(row):
    progress = min(max(float(row["Priority Score"]), 8), 100)
    st.markdown(
        f"""
        <div class="prediction-grid">
            <div class="prediction-card">
                <div class="prediction-label">Current Classification</div>
                <div class="prediction-value">{row['Risk Classification']}</div>
                <div class="prediction-detail">Environmental Stress Score: {row['ESS']:.2f}</div>
                <div class="progress-track"><div class="progress-fill" style="width:{progress}%"></div></div>
            </div>
            <div class="prediction-arrow">→</div>
            <div class="prediction-card">
                <div class="prediction-label">Observed Change Direction</div>
                <div class="prediction-value">{row['Change Direction']}</div>
                <div class="prediction-detail">Derived from temperature, water, and soil-water change indicators.</div>
                <div class="progress-track"><div class="progress-fill warning-fill" style="width:{progress}%"></div></div>
            </div>
            <div class="prediction-arrow">→</div>
            <div class="prediction-card">
                <div class="prediction-label">Forward Monitoring Outlook</div>
                <div class="prediction-value">{row['Risk Outlook']}</div>
                <div class="prediction-detail">Evidence-based outlook calculated from CSV values only.</div>
                <div class="progress-track"><div class="progress-fill green-fill" style="width:{progress}%"></div></div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )


def render_recommendation_cards(row):
    cards = build_recommendations(row)
    for title, body, basis in cards:
        st.markdown(
            f"""
            <div class="recommend-card">
                <div class="recommend-title">{title}</div>
                <div class="recommend-body">{body}</div>
                <div class="recommend-basis">{basis}</div>
            </div>
            """,
            unsafe_allow_html=True
        )


# -----------------------------
# CSS
# -----------------------------
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Raleway:wght@400;500;600;700;800;900&display=swap');

    html, body, [class*="css"], .stApp, div, span, p, h1, h2, h3, h4, label, button {
        font-family: 'Raleway', sans-serif !important;
    }

    .stApp {
        background:
            radial-gradient(circle at 6% 0%, rgba(27,92,143,.58) 0, rgba(7,17,31,0) 38%),
            radial-gradient(circle at 92% 8%, rgba(118,78,255,.28) 0, rgba(7,17,31,0) 34%),
            linear-gradient(135deg, #07111f 0%, #0b1f34 48%, #050b16 100%);
        color: #f7fbff;
    }

    .block-container {
        padding-top: 1.2rem;
        padding-bottom: 1.8rem;
        max-width: 1500px;
    }

    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, rgba(5,18,34,.98), rgba(4,12,24,.99));
        border-right: 1px solid rgba(135,205,255,.20);
    }

    section[data-testid="stSidebar"] * {
        color: #f7fbff;
    }

    .brand-card {
        padding: 18px 16px;
        border-radius: 24px;
        background: linear-gradient(160deg, rgba(34,211,238,.22), rgba(124,92,255,.13));
        border: 1px solid rgba(139,213,255,.25);
        margin-bottom: 18px;
        box-shadow: 0 18px 50px rgba(0,0,0,.22);
    }

    .brand-title {
        font-size: 28px;
        font-weight: 900;
        letter-spacing: -0.04em;
        margin-bottom: 4px;
        color: #ffffff;
    }

    .brand-subtitle {
        color: #d7e8f8;
        font-size: 11.5px;
        line-height: 1.55;
    }

    .main-title {
        font-size: 36px;
        font-weight: 900;
        letter-spacing: -0.05em;
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
        border: 1px solid rgba(72,216,232,.42);
        background: rgba(31,151,185,.16);
        color: #cfffff;
        font-size: 11px;
        font-weight: 800;
        margin-bottom: 10px;
        letter-spacing: .02em;
    }

    .card {
        background: linear-gradient(180deg, rgba(255,255,255,.105), rgba(255,255,255,.060));
        border: 1px solid rgba(182,222,255,.18);
        border-radius: 26px;
        padding: 18px;
        box-shadow: 0 24px 70px rgba(0,0,0,.28);
        backdrop-filter: blur(14px);
        margin-bottom: 16px;
    }

    .kpi-card {
        background: linear-gradient(180deg, rgba(255,255,255,.125), rgba(255,255,255,.065));
        border: 1px solid rgba(182,222,255,.18);
        border-radius: 24px;
        padding: 17px;
        min-height: 116px;
        box-shadow: 0 18px 45px rgba(0,0,0,.18);
    }

    .kpi-label {
        color: #d5e6f5;
        font-size: 10.5px;
        font-weight: 800;
        letter-spacing: .04em;
        text-transform: uppercase;
    }

    .kpi-value {
        font-size: 31px;
        font-weight: 900;
        line-height: 1.05;
        margin-top: 8px;
        color: #ffffff;
    }

    .kpi-note {
        color: #c6d8ea;
        font-size: 10.5px;
        margin-top: 7px;
        line-height: 1.35;
    }

    .section-title {
        font-size: 17px;
        font-weight: 900;
        color: #ffffff;
        margin-bottom: 4px;
        letter-spacing: -.02em;
    }

    .section-subtitle {
        color: #c7d9ea;
        font-size: 11.4px;
        line-height: 1.45;
        margin-bottom: 14px;
    }

    .cyan { color: #46e6ff; }
    .red { color: #ff6678; }
    .green { color: #60e49a; }
    .yellow { color: #ffe06a; }

    .ranking-row {
        display: grid;
        grid-template-columns: 42px 1fr 64px 92px;
        gap: 10px;
        align-items: center;
        padding: 13px 14px;
        border-radius: 19px;
        background: linear-gradient(180deg, rgba(255,255,255,.105), rgba(255,255,255,.06));
        border: 1px solid rgba(182,222,255,.16);
        margin-bottom: 10px;
    }

    .rank-number {
        color: #ffffff;
        font-size: 15px;
        font-weight: 900;
    }

    .rank-name {
        color: #f7fbff;
        font-size: 13px;
        font-weight: 800;
        line-height: 1.35;
    }

    .rank-score {
        color: #dbeafe;
        font-size: 15px;
        font-weight: 900;
        text-align: center;
    }

    .risk-badge {
        border-radius: 999px;
        padding: 7px 10px;
        font-size: 10.5px;
        font-weight: 900;
        text-align: center;
    }

    .risk-critical {
        background: rgba(255,77,109,.22);
        color: #ff9aaa;
    }

    .risk-warning {
        background: rgba(251,191,36,.20);
        color: #ffe08a;
    }

    .risk-safe {
        background: rgba(56,239,125,.18);
        color: #98ffc1;
    }

    .risk-default {
        background: rgba(34,211,238,.18);
        color: #bdf7ff;
    }

    .prediction-grid {
        display: grid;
        grid-template-columns: 1fr 36px 1fr 36px 1fr;
        gap: 12px;
        align-items: center;
    }

    .prediction-card {
        min-height: 160px;
        padding: 17px;
        border-radius: 24px;
        background: linear-gradient(180deg, rgba(255,255,255,.105), rgba(255,255,255,.060));
        border: 1px solid rgba(182,222,255,.18);
    }

    .prediction-label {
        color: #b8cce1;
        font-size: 11px;
        font-weight: 800;
        text-transform: uppercase;
        letter-spacing: .03em;
        margin-bottom: 12px;
    }

    .prediction-value {
        color: #ffffff;
        font-size: 20px;
        font-weight: 900;
        line-height: 1.22;
        margin-bottom: 10px;
    }

    .prediction-detail {
        color: #d7e8f8;
        font-size: 12px;
        line-height: 1.45;
        min-height: 38px;
    }

    .prediction-arrow {
        color: #9fb4ca;
        font-size: 28px;
        font-weight: 800;
        text-align: center;
    }

    .progress-track {
        width: 100%;
        height: 10px;
        border-radius: 999px;
        background: rgba(255,255,255,.14);
        overflow: hidden;
        margin-top: 14px;
    }

    .progress-fill {
        height: 100%;
        border-radius: 999px;
        background: linear-gradient(90deg, #fbbf24, #ff4d6d);
    }

    .warning-fill {
        background: linear-gradient(90deg, #22d3ee, #7c5cff);
    }

    .green-fill {
        background: linear-gradient(90deg, #38ef7d, #22d3ee);
    }

    .insight-box {
        display: grid;
        grid-template-columns: 54px 1fr;
        gap: 14px;
        align-items: start;
        background: rgba(255,255,255,.075);
        border: 1px solid rgba(182,222,255,.18);
        border-radius: 22px;
        padding: 16px;
    }

    .bot-icon {
        width: 54px;
        height: 54px;
        border-radius: 18px;
        background: linear-gradient(135deg, #2fe1ee, #316fff);
        display: grid;
        place-items: center;
        font-size: 25px;
        box-shadow: 0 0 24px rgba(47,225,238,.30);
    }

    .mini-text {
        color: #d7e8f8;
        font-size: 12px;
        line-height: 1.65;
    }

    .recommend-grid {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 12px;
    }

    .recommend-card {
        min-height: 135px;
        padding: 15px;
        border-radius: 22px;
        background: linear-gradient(180deg, rgba(255,255,255,.105), rgba(255,255,255,.060));
        border: 1px solid rgba(182,222,255,.17);
    }

    .recommend-title {
        color: #ffffff;
        font-size: 13.5px;
        font-weight: 900;
        margin-bottom: 9px;
    }

    .recommend-body {
        color: #d4e4f3;
        font-size: 11.5px;
        line-height: 1.55;
        margin-bottom: 10px;
    }

    .recommend-basis {
        color: #9fc4dc;
        font-size: 10.2px;
        line-height: 1.35;
        border-top: 1px solid rgba(255,255,255,.10);
        padding-top: 8px;
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

    [data-testid="stDataFrame"] div {
        font-size: 11px !important;
    }

    @media (max-width: 1000px) {
        .prediction-grid {
            grid-template-columns: 1fr;
        }

        .prediction-arrow {
            display: none;
        }

        .recommend-grid {
            grid-template-columns: 1fr;
        }

        .ranking-row {
            grid-template-columns: 38px 1fr;
        }
    }
    </style>
    """,
    unsafe_allow_html=True
)

df = load_data()

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
        unsafe_allow_html=True
    )

    page = st.radio(
        "Dashboard Navigation",
        [
            "Executive Overview",
            "Site Intelligence",
            "Environmental Dynamics",
            "Predictive Outlook",
            "Resource Recommendations",
        ],
        label_visibility="collapsed"
    )

    st.markdown("---")
    st.markdown("**Data Basis**")
    st.caption("All values are read from geosentinel_dashboard_data.csv or calculated directly from its columns.")
    st.markdown("**Coverage**")
    st.caption(f"{len(df)} monitored data center facilities")

# -----------------------------
# Header
# -----------------------------
st.markdown('<div class="badge">HACKATHON DEMO · GEOAI RESOURCE INTELLIGENCE</div>', unsafe_allow_html=True)
st.markdown('<div class="main-title">DC-Resource Intelligence Platform</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="subtitle">GeoAI-based environmental monitoring and resource risk assessment for large-scale data centers.</div>',
    unsafe_allow_html=True
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
        render_kpi("Monitored Facilities", f"{len(df)}", "Data center locations in the CSV dataset", "cyan")
    with k2:
        render_kpi("High-Risk Facilities", f"{critical_count}", "Facilities classified as critical", "red")
    with k3:
        render_kpi("Highest Change Index", f"{top_eci['ECI']:.2f}", top_eci["Monitored Facility"], "yellow")
    with k4:
        render_kpi("Highest Stress Score", f"{top_ess['ESS']:.2f}", top_ess["Monitored Facility"], "green")

    st.markdown("<br>", unsafe_allow_html=True)

    left, right = st.columns([0.42, 0.58])

    with left:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">Priority Environmental Risk Assessment</div>', unsafe_allow_html=True)
        st.markdown(
            '<div class="section-subtitle">Top-ranked monitored facilities based on environmental change and stress indicators.</div>',
            unsafe_allow_html=True
        )

        ranking = df.sort_values("Priority Score", ascending=False).head(5)[
            ["Monitored Facility", "Priority Score", "Risk Classification"]
        ]
        render_ranking_cards(ranking)
        st.markdown('</div>', unsafe_allow_html=True)

    with right:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">National Environmental Risk Distribution</div>', unsafe_allow_html=True)
        st.markdown(
            '<div class="section-subtitle">Spatial distribution of environmental resource risk surrounding monitored data center facilities.</div>',
            unsafe_allow_html=True
        )

        fig_map = px.scatter_mapbox(
            df,
            lat="lat",
            lon="lon",
            color="Risk Classification",
            size="Priority Score",
            size_max=24,
            zoom=3,
            height=500,
            hover_name="Monitored Facility",
            hover_data={
                "lat": False,
                "lon": False,
                "Priority Score": ":.1f",
                "ECI": ":.2f",
                "ESS": ":.2f",
                "Risk Classification": True,
            },
            color_discrete_map={
                "Critical": "#ff4d6d",
                "Warning": "#fbbf24",
                "Safe": "#38ef7d",
            },
        )

        fig_map.update_layout(
            mapbox_style="carto-darkmatter",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(family="Raleway", color="#f7fbff", size=11),
            margin=dict(l=0, r=0, t=0, b=0),
            legend_title_text="Risk Classification",
        )

        st.plotly_chart(fig_map, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    p_left, p_right = st.columns([0.62, 0.38])

    with p_left:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">Predictive Environmental Outlook</div>', unsafe_allow_html=True)
        st.markdown(
            '<div class="section-subtitle">Readable evidence-based outlook derived from current CSV indicators only.</div>',
            unsafe_allow_html=True
        )
        render_prediction_cards(top_priority)
        st.markdown('</div>', unsafe_allow_html=True)

    with p_right:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">GeoAI Insight Summary</div>', unsafe_allow_html=True)
        evidence_html = "".join([f"<li>{p}</li>" for p in evidence_points(top_priority)])
        st.markdown(
            f"""
            <div class="insight-box">
                <div class="bot-icon">🤖</div>
                <div class="mini-text">
                    <b>{top_priority['Monitored Facility']}</b> has the highest priority score in the current dataset.<br><br>
                    <b>Evidence from CSV:</b>
                    <ul>{evidence_html}</ul>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )
        st.markdown('</div>', unsafe_allow_html=True)

    r_left, r_right = st.columns([0.62, 0.38])

    with r_left:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">Recommended Mitigation Actions</div>', unsafe_allow_html=True)
        st.markdown(
            '<div class="section-subtitle">Action areas are selected from observed environmental change signals.</div>',
            unsafe_allow_html=True
        )
        st.markdown('<div class="recommend-grid">', unsafe_allow_html=True)
        render_recommendation_cards(top_priority)
        st.markdown('</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with r_right:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">Risk Classification Summary</div>', unsafe_allow_html=True)
        summary = pd.DataFrame({
            "Risk Classification": ["Critical", "Warning", "Safe"],
            "Number of Facilities": [critical_count, warning_count, safe_count],
        })
        fig = px.bar(
            summary,
            x="Risk Classification",
            y="Number of Facilities",
            color="Risk Classification",
            color_discrete_map={
                "Critical": "#ff4d6d",
                "Warning": "#fbbf24",
                "Safe": "#38ef7d",
            },
            height=300,
            text="Number of Facilities"
        )
        fig.update_traces(textposition="outside", textfont_color="#ffffff")
        st.plotly_chart(style_figure(fig), use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Executive Summary Table</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="section-subtitle">Presentation-ready labels are used. No raw column names or underscores are displayed.</div>',
        unsafe_allow_html=True
    )

    table = df.sort_values("Priority Score", ascending=False)[
        ["Monitored Facility", "Priority Score", "ECI", "ESS", "Risk Classification", "Risk Outlook"]
    ].rename(columns={
        "ECI": "Environmental Change Index",
        "ESS": "Environmental Stress Score",
    })
    st.dataframe(table, use_container_width=True, hide_index=True, height=min(440, 78 + len(table) * 38))
    st.markdown('</div>', unsafe_allow_html=True)

# -----------------------------
# Site Intelligence
# -----------------------------
elif page == "Site Intelligence":
    selected_site = st.selectbox("Select Monitored Facility", df["Monitored Facility"].tolist())
    row = df[df["Monitored Facility"] == selected_site].iloc[0]

    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown(f'<div class="section-title">Site-Level Environmental Assessment: {selected_site}</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-subtitle">Detailed environmental profile for the selected data center facility.</div>', unsafe_allow_html=True)

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
        st.markdown('<div class="section-subtitle">All metric labels are formatted for dashboard presentation.</div>', unsafe_allow_html=True)

        indicator_df = pd.DataFrame({
            "Environmental Indicator": [
                "Land Surface Temperature",
                "Surface Water Availability",
                "Soil Water Content",
                "Temperature Change",
                "Water Availability Change",
                "Soil Water Change",
                "Environmental Change Index",
                "Environmental Stress Score",
                "Priority Score",
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
                row["Priority Score"],
            ]
        })

        fig = px.bar(
            indicator_df,
            x="Value",
            y="Environmental Indicator",
            orientation="h",
            color="Value",
            color_continuous_scale=["#7c5cff", "#22d3ee", "#38ef7d"],
            height=460
        )
        fig.update_layout(showlegend=False, coloraxis_showscale=False)
        st.plotly_chart(style_figure(fig), use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with right:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">GeoAI Analytical Interpretation</div>', unsafe_allow_html=True)
        evidence_html = "".join([f"<li>{p}</li>" for p in evidence_points(row)])
        st.markdown(
            f"""
            <div class="insight-box">
                <div class="bot-icon">◈</div>
                <div class="mini-text">
                    <b>Risk Outlook:</b> {row['Risk Outlook']}<br>
                    <b>Change Direction:</b> {row['Change Direction']}<br><br>
                    <b>Evidence from CSV:</b>
                    <ul>{evidence_html}</ul>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )
        st.caption("This interpretation is rule-based and uses only CSV environmental indicators.")
        st.markdown('</div>', unsafe_allow_html=True)

# -----------------------------
# Environmental Dynamics
# -----------------------------
elif page == "Environmental Dynamics":
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Environmental Change Dynamics</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-subtitle">Comparison of observed environmental change indicators across monitored facilities.</div>', unsafe_allow_html=True)

    trend_df = df.sort_values("Priority Score", ascending=False).copy()

    fig = go.Figure()
    fig.add_trace(go.Bar(
        name="Temperature Change",
        x=trend_df["Monitored Facility"],
        y=trend_df["lst_change"],
        marker_color="#ff4d6d"
    ))
    fig.add_trace(go.Bar(
        name="Water Availability Change",
        x=trend_df["Monitored Facility"],
        y=trend_df["ndwi_change"],
        marker_color="#22d3ee"
    ))
    fig.add_trace(go.Bar(
        name="Soil Water Change",
        x=trend_df["Monitored Facility"],
        y=trend_df["soil_moisture_change"],
        marker_color="#38ef7d"
    ))

    fig.update_layout(barmode="group", height=540, xaxis_tickangle=-25)
    st.plotly_chart(style_figure(fig), use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Environmental Indicator Comparison Table</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-subtitle">Formal labels are used for presentation clarity.</div>', unsafe_allow_html=True)

    table = trend_df[
        ["Monitored Facility", "lst_change", "ndwi_change", "soil_moisture_change", "Risk Classification", "Change Direction"]
    ].rename(columns={
        "lst_change": "Temperature Change",
        "ndwi_change": "Water Availability Change",
        "soil_moisture_change": "Soil Water Change",
    })
    st.dataframe(table, use_container_width=True, hide_index=True, height=min(440, 78 + len(table) * 38))
    st.markdown('</div>', unsafe_allow_html=True)

# -----------------------------
# Predictive Outlook
# -----------------------------
elif page == "Predictive Outlook":
    selected_site = st.selectbox("Select Facility for Outlook", df["Monitored Facility"].tolist())
    row = df[df["Monitored Facility"] == selected_site].iloc[0]

    left, right = st.columns([0.64, 0.36])

    with left:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">Predictive Environmental Outlook</div>', unsafe_allow_html=True)
        st.markdown(
            '<div class="section-subtitle">A simple, readable outlook derived from current CSV indicators. No external forecast values are introduced.</div>',
            unsafe_allow_html=True
        )
        render_prediction_cards(row)
        st.markdown('</div>', unsafe_allow_html=True)

    with right:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">Outlook Explanation</div>', unsafe_allow_html=True)
        st.markdown(
            f"""
            <div class="insight-box">
                <div class="bot-icon">🤖</div>
                <div class="mini-text">
                    <b>{row['Monitored Facility']}</b><br><br>
                    <b>Current status:</b> {row['Risk Classification']}<br>
                    <b>Observed direction:</b> {row['Change Direction']}<br>
                    <b>Outlook:</b> {row['Risk Outlook']}
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Forward Monitoring Priority Table</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-subtitle">Facilities ranked for continued environmental monitoring.</div>', unsafe_allow_html=True)

    focus = df.sort_values("Priority Score", ascending=False)[
        ["Monitored Facility", "Priority Score", "Risk Classification", "Change Direction", "Risk Outlook"]
    ]
    st.dataframe(focus, use_container_width=True, hide_index=True, height=min(440, 78 + len(focus) * 38))
    st.markdown('</div>', unsafe_allow_html=True)

# -----------------------------
# Resource Recommendations
# -----------------------------
else:
    selected_site = st.selectbox("Select Facility for Resource Guidance", df["Monitored Facility"].tolist())
    row = df[df["Monitored Facility"] == selected_site].iloc[0]

    k1, k2, k3 = st.columns(3)
    with k1:
        render_kpi("Risk Classification", row["Risk Classification"], "Current category from CSV", "red")
    with k2:
        render_kpi("Risk Outlook", row["Risk Outlook"], "Derived from observed change signals", "cyan")
    with k3:
        render_kpi("Priority Score", f"{row['Priority Score']:.1f}", "Calculated from ECI and ESS ranks", "green")

    left, right = st.columns([0.58, 0.42])

    with left:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">Recommended Mitigation Actions</div>', unsafe_allow_html=True)
        st.markdown(
            '<div class="section-subtitle">Action cards are selected from environmental change signals available in the CSV dataset.</div>',
            unsafe_allow_html=True
        )
        st.markdown('<div class="recommend-grid">', unsafe_allow_html=True)
        render_recommendation_cards(row)
        st.markdown('</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with right:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">Evidence Supporting Recommendation</div>', unsafe_allow_html=True)
        evidence_html = "".join([f"<li>{p}</li>" for p in evidence_points(row)])
        st.markdown(
            f"""
            <div class="insight-box">
                <div class="bot-icon">📌</div>
                <div class="mini-text">
                    <b>{row['Monitored Facility']}</b>
                    <ul>{evidence_html}</ul>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )
        st.caption("No external forecast values or unverified impact estimates are added.")
        st.markdown('</div>', unsafe_allow_html=True)