import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path

st.set_page_config(page_title="DC-Resource Intelligence Platform", page_icon="🛡️", layout="wide", initial_sidebar_state="expanded")

CSV_FILE = "geosentinel_monthly_dashboard_data.csv"

@st.cache_data
def load_data():
    p = Path(CSV_FILE)
    if not p.exists():
        st.error(f"ไม่พบไฟล์ {CSV_FILE} กรุณาวางไฟล์ CSV ไว้ในโฟลเดอร์เดียวกับไฟล์นี้")
        st.stop()
    df = pd.read_csv(p)
    df["Date"] = pd.to_datetime(df["year_month"] + "-01")
    df["Year"] = df["Date"].dt.year.astype(int)
    df["Month"] = df["Date"].dt.strftime("%Y-%m")
    df["Data Center"] = df["data_center_name"].str.replace("_", " ", regex=False)
    return df

df = load_data()

# ---------- Session filters ----------
def init_state(key, value):
    if key not in st.session_state:
        st.session_state[key] = value

init_state("selected_year", int(df["Year"].max()))
init_state("selected_month", str(df["Month"].max()))
init_state("selected_risk", "All")
init_state("selected_page", "Overview")
init_state("selected_center", df.sort_values("risk_score", ascending=False).iloc[0]["data_center_name"])

# ---------- CSS: clone target layout ----------
st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap');

:root{
    --navy:#061B33;
    --navy2:#08213E;
    --blue:#1167E8;
    --text:#0F172A;
    --muted:#64748B;
    --border:#DCE6F2;
    --bg:#F3F7FB;
    --card:#FFFFFF;
    --danger:#E11D48;
    --orange:#F97316;
    --yellow:#FACC15;
    --green:#22C55E;
    --purple:#7C3AED;
}
html, body, [class*="css"], [data-testid="stAppViewContainer"]{font-family:'Inter',sans-serif;}
[data-testid="stAppViewContainer"]{background:var(--bg);}
.main .block-container{
    max-width: 100% !important;
    padding: 0.25rem 0.95rem 0.8rem 0.95rem !important;
}
[data-testid="stSidebar"]{
    background:linear-gradient(180deg,#04172C 0%,#08213E 100%) !important;
    min-width:220px !important;
    max-width:220px !important;
}
[data-testid="stSidebar"] *{color:#EAF2FF !important;}
[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p{margin:0;}
[data-testid="stSidebar"] div.stButton > button{
    width:100%; border:1px solid rgba(255,255,255,.12); background:rgba(14,76,145,.22);
    color:#EAF2FF; border-radius:12px; padding:.78rem .75rem; text-align:left; font-weight:700;
}
[data-testid="stSidebar"] div.stButton > button:hover{background:#0B5ED7;border-color:#0B5ED7;color:#fff;}

button[kind="secondary"]{
    border-radius:14px !important; border:1px solid #D8E4F2 !important; background:white !important;
    color:#2563EB !important; font-weight:800 !important; box-shadow:0 6px 16px rgba(15,23,42,.04) !important;
}
button[kind="secondary"]:hover{border-color:#2563EB !important; background:#EFF6FF !important;}

h1,h2,h3,p{margin:0;}
.hero{
    background:#fff; border:1px solid var(--border); border-radius:18px; padding:20px 22px;
    box-shadow:0 12px 30px rgba(15,23,42,.06); min-height:100px;
}
.hero-title{font-size:30px;line-height:1.1;font-weight:900;color:#0B1226;letter-spacing:-1.2px;}
.hero-sub{font-size:13px;color:#53667E;font-weight:600;margin-top:10px;}
.pill-row{display:flex;gap:8px;justify-content:flex-end;flex-wrap:wrap;}
.pill{background:#F1F7FF;color:#1863DF;border:1px solid #D7E8FF;border-radius:14px;padding:10px 14px;font-weight:800;font-size:13px;display:inline-flex;align-items:center;gap:7px;}

.card{background:#fff;border:1px solid var(--border);border-radius:16px;box-shadow:0 12px 28px rgba(15,23,42,.05);}
.kpi{height:120px;padding:15px 16px;position:relative;overflow:hidden;}
.kpi-icon{position:absolute;right:14px;top:16px;width:44px;height:44px;border-radius:18px;display:flex;align-items:center;justify-content:center;font-size:23px;font-weight:900;}
.kpi-label{font-size:12px;text-transform:uppercase;letter-spacing:.9px;color:#53667E;font-weight:900;line-height:1.55;max-width:135px;}
.kpi-value{font-size:29px;font-weight:900;color:#081226;margin-top:10px;letter-spacing:-.8px;line-height:1;}
.kpi-sub{font-size:12px;color:#8A9AB0;font-weight:800;margin-top:12px;line-height:1.4;}
.section-card{padding:14px 15px;margin-top:12px;}
.section-title{font-size:15px;font-weight:900;color:#0F172A;display:flex;align-items:center;gap:8px;}
.section-sub{font-size:12px;color:#64748B;font-weight:700;margin-top:7px;}
.detail-title{font-size:20px;font-weight:900;color:#0F172A;margin-bottom:8px;}
.breadcrumb{font-size:11px;color:#6B7C91;font-weight:800;margin-bottom:12px;}
.score-card{padding:16px;min-height:112px;}
.score-label{font-size:11px;text-transform:uppercase;color:#53667E;letter-spacing:.8px;font-weight:900;}
.score-value{font-size:29px;font-weight:900;color:#0F172A;margin-top:10px;}
.badge{display:inline-block;padding:5px 10px;border-radius:999px;font-size:11px;font-weight:900;margin-left:6px;}
.badge-danger{background:#FFE4E8;color:#BE123C;}
.badge-orange{background:#FFEDD5;color:#C2410C;}
.badge-yellow{background:#FEF3C7;color:#A16207;}
.badge-green{background:#DCFCE7;color:#15803D;}
.alert-box{background:#FFF1F2;border:1px solid #FDA4AF;border-radius:14px;padding:15px;display:flex;align-items:center;gap:16px;margin-top:12px;}
.alert-icon{font-size:37px;color:#E11D48;}
.alert-title{font-size:15px;font-weight:900;color:#0F172A;margin-bottom:6px;}
.alert-text{font-size:12px;color:#1F2937;line-height:1.55;font-weight:600;}
.big-risk{background:#EF4444;color:white;border-radius:9px;padding:11px 16px;font-weight:900;text-align:center;font-size:18px;letter-spacing:.8px;}
.mini-card{padding:15px;min-height:96px;}
.mini-title{font-size:13px;font-weight:900;color:#0F172A;margin-bottom:6px;}
.mini-text{font-size:12px;color:#475569;line-height:1.5;font-weight:600;}
.table-wrap{background:#fff;border:1px solid var(--border);border-radius:16px;box-shadow:0 12px 28px rgba(15,23,42,.05);padding:12px;margin-top:12px;}
table.clone-table{width:100%;border-collapse:collapse;font-size:12px;}
table.clone-table th{color:#52667D;text-align:left;font-weight:900;padding:9px 8px;border-bottom:1px solid #E5EDF6;font-size:11px;}
table.clone-table td{padding:9px 8px;border-bottom:1px solid #EDF2F7;color:#0F172A;font-weight:600;}
.footer{background:linear-gradient(90deg,#061B33,#08213E);color:white;border-radius:12px;padding:13px 16px;margin-top:12px;font-size:12px;font-weight:700;display:flex;justify-content:space-between;align-items:center;}
.stPlotlyChart{background:#fff;border-radius:0 0 16px 16px;}
[data-testid="stVerticalBlock"]{gap:.55rem !important;}
</style>
""",
    unsafe_allow_html=True,
)

# ---------- Helpers ----------
def level_from_score(score):
    if score >= 75: return "Critical"
    if score >= 50: return "Concern"
    if score >= 25: return "Watch"
    return "Stable"

def risk_color(level_or_score):
    if isinstance(level_or_score, (int, float)):
        level = level_from_score(level_or_score)
    else:
        level = str(level_or_score)
    return {"Critical":"#E11D48", "Concern":"#F97316", "Watch":"#FACC15", "Stable":"#22C55E", "Low":"#22C55E"}.get(level, "#64748B")

def badge_class(level):
    level = str(level)
    if level == "Critical": return "badge-danger"
    if level == "Concern": return "badge-orange"
    if level == "Watch": return "badge-yellow"
    return "badge-green"

def display_name(name):
    return str(name).replace("_", " ")

def compact_name(name):
    return display_name(name).replace("Microsoft SanAntonio TX", "Microsoft SanAntonio TX")

def make_map(data, value_col, title):
    color_scale = [[0, "#22C55E"], [0.35, "#FACC15"], [0.65, "#F97316"], [1, "#E11D48"]]
    fig = px.scatter_mapbox(
        data,
        lat="latitude",
        lon="longitude",
        size=value_col,
        color=value_col,
        color_continuous_scale=color_scale,
        hover_name="Data Center",
        hover_data={"latitude":":.3f", "longitude":":.3f", value_col:":.2f"},
        zoom=2.55,
        height=280,
    )
    fig.update_layout(
        mapbox_style="carto-positron",
        margin=dict(l=0, r=0, t=0, b=0),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        coloraxis_colorbar=dict(title="Score", thickness=13, len=.66, y=.48),
        font=dict(family="Inter", size=12, color="#64748B"),
    )
    fig.update_traces(marker=dict(opacity=.90, sizemin=10))
    return fig

def line_chart(center_df, y, color, ytitle):
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=center_df["Date"], y=center_df[y], mode="lines+markers",
        line=dict(width=3, color=color), marker=dict(size=5, color=color), fill="tozeroy",
        fillcolor="rgba(239,68,68,.10)" if color == "#E11D48" else "rgba(37,99,235,.10)"
    ))
    fig.update_layout(
        height=210, margin=dict(l=35,r=16,t=8,b=28),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(showgrid=True, gridcolor="#E9EFF6", tickfont=dict(size=10)),
        yaxis=dict(title=ytitle, showgrid=True, gridcolor="#E9EFF6", tickfont=dict(size=10), titlefont=dict(size=10)),
        font=dict(family="Inter", color="#64748B"),
    )
    return fig

def table_html(data, score_col, title_col):
    rows = []
    for i, (_, r) in enumerate(data.iterrows(), 1):
        lvl = r.get("risk_level", level_from_score(r[score_col]))
        rows.append(f"""
        <tr>
            <td>{i}</td>
            <td>{display_name(r['data_center_name'])}</td>
            <td>{r[score_col]:.2f}</td>
            <td><span class='badge {badge_class(lvl)}'>{lvl}</span></td>
            <td><span style='color:{risk_color(lvl)};font-weight:900'>●</span></td>
        </tr>
        """)
    return f"""
    <div class='table-wrap'>
        <div class='section-title'>▧ {title_col}</div>
        <table class='clone-table'>
            <thead><tr><th>Rank</th><th>Data Center</th><th>Score</th><th>Level</th><th>Status</th></tr></thead>
            <tbody>{''.join(rows)}</tbody>
        </table>
    </div>
    """

def kpi_card(label, value, sub, icon, bg, color):
    return f"""
    <div class='card kpi'>
        <div class='kpi-icon' style='background:{bg}; color:{color};'>{icon}</div>
        <div class='kpi-label'>{label}</div>
        <div class='kpi-value'>{value}</div>
        <div class='kpi-sub'>{sub}</div>
    </div>
    """

# ---------- Sidebar navigation and filters ----------
with st.sidebar:
    st.markdown("""
    <div style='height:26px'></div>
    <div style='font-size:20px;font-weight:900;line-height:1.05;margin-bottom:8px;'>🛡️ DC-Resource<br>Intelligence</div>
    <div style='font-size:11px;color:#B6C6DA!important;font-weight:700;line-height:1.45;margin-bottom:28px;'>GeoAI Environmental Monitoring<br>for Data Centers</div>
    <div style='font-size:11px;color:#8EA7C5!important;letter-spacing:1.6px;font-weight:900;margin-bottom:10px;'>NAVIGATION</div>
    """, unsafe_allow_html=True)
    pages = ["Overview", "Hotspot Detail", "Alerts", "Data Centers", "Trends", "Forecast", "Reports", "About"]
    icons = ["▣", "◎", "△", "⌂", "↗", "◷", "▤", "ⓘ"]
    for icon, page in zip(icons, pages):
        if st.button(f"{icon} {page}", key=f"page_{page}"):
            st.session_state.selected_page = page
            st.rerun()

    st.markdown("<div style='height:18px'></div><div style='font-size:11px;color:#8EA7C5!important;letter-spacing:1.6px;font-weight:900;margin-bottom:10px;'>FILTERS</div>", unsafe_allow_html=True)
    years = sorted(df["Year"].unique().tolist())
    for y in years:
        if st.button(f"Year {y}", key=f"year_{y}"):
            st.session_state.selected_year = int(y)
            months_y = sorted(df.loc[df["Year"].eq(y), "Month"].unique())
            st.session_state.selected_month = months_y[-1]
            st.rerun()

    risks = ["All"] + sorted(df["risk_level"].dropna().unique().tolist())
    for r in risks:
        if st.button(f"Risk {r}", key=f"risk_{r}"):
            st.session_state.selected_risk = r
            st.rerun()

    st.markdown("""
    <div style='position:fixed;bottom:18px;width:172px;border:1px solid rgba(255,255,255,.15);border-radius:14px;padding:14px;background:rgba(255,255,255,.04);'>
        <div style='font-size:12px;font-weight:900;'>Data Source</div>
        <div style='font-size:11px;color:#B6C6DA!important;font-weight:700;margin-top:8px;line-height:1.45;'>Google Earth Engine<br>2020 – 2025</div>
        <div style='font-size:30px;margin-top:12px;text-align:center;'>🛰️</div>
    </div>
    """, unsafe_allow_html=True)

# ---------- Apply filters ----------
available_months = sorted(df.loc[df["Year"].eq(st.session_state.selected_year), "Month"].unique().tolist())
if st.session_state.selected_month not in available_months:
    st.session_state.selected_month = available_months[-1]

# Main top filter buttons: months in selected year
header_left, header_right = st.columns([5.8, 2.4], gap="medium")
with header_left:
    st.markdown(
        """
        <div class='hero'>
            <div class='hero-title'>DC-Resource Intelligence Platform</div>
            <div class='hero-sub'>GeoAI-Based Environmental Monitoring and Resource Risk Assessment for Data Centers</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
with header_right:
    st.markdown("<div class='pill-row'>", unsafe_allow_html=True)
    st.markdown(f"<span class='pill'>📅 Year: {st.session_state.selected_year}</span>", unsafe_allow_html=True)
    st.markdown(f"<span class='pill'>📌 Risk: {st.session_state.selected_risk}</span>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)
    st.write("")
    month_cols = st.columns(3, gap="small")
    show_months = available_months[-6:]
    for i, m in enumerate(show_months):
        with month_cols[i % 3]:
            label = m if m != st.session_state.selected_month else f"✓ {m}"
            if st.button(label, key=f"month_{m}"):
                st.session_state.selected_month = m
                st.rerun()

filtered = df[df["Month"].eq(st.session_state.selected_month)].copy()
if st.session_state.selected_risk != "All":
    filtered = filtered[filtered["risk_level"].eq(st.session_state.selected_risk)].copy()
if filtered.empty:
    filtered = df[df["Month"].eq(st.session_state.selected_month)].copy()

# Choose hotspot after filter
if st.session_state.selected_center not in filtered["data_center_name"].values:
    st.session_state.selected_center = filtered.sort_values("risk_score", ascending=False).iloc[0]["data_center_name"]

top_hotspot = filtered.sort_values("risk_score", ascending=False).iloc[0]
monitored = filtered["data_center_name"].nunique()
critical_eci = int((filtered["ECI_score"] >= filtered["ECI_score"].quantile(.85)).sum())
critical_ess = int((filtered["ESS_score"] >= filtered["ESS_score"].quantile(.85)).sum())

# ---------- Horizontal app body ----------
main_col, detail_col = st.columns([1.55, 1.20], gap="medium")

with main_col:
    k1, k2, k3, k4 = st.columns(4, gap="small")
    with k1:
        st.markdown(kpi_card("Monitored<br>Data Centers", monitored, "Across selected filter", "▦", "#E8F3FF", "#2563EB"), unsafe_allow_html=True)
    with k2:
        st.markdown(kpi_card("Critical ECI<br>Areas", critical_eci, "High rate of change", "↗", "#FFE5EA", "#E11D48"), unsafe_allow_html=True)
    with k3:
        st.markdown(kpi_card("Critical ESS<br>Areas", critical_ess, "High environmental stress", "⚠", "#FFEEDB", "#F97316"), unsafe_allow_html=True)
    with k4:
        st.markdown(kpi_card("Top Hotspot", display_name(top_hotspot["data_center_name"]).split()[0] + "<br>" + " ".join(display_name(top_hotspot["data_center_name"]).split()[1:])[:15], "Ranked by selected filter", "⌖", "#EEE7FF", "#7C3AED"), unsafe_allow_html=True)

    map1, map2 = st.columns(2, gap="medium")
    with map1:
        st.markdown("""
        <div class='card section-card' style='border-bottom-left-radius:0;border-bottom-right-radius:0;'>
            <div class='section-title'>▧ ECI Map</div>
            <div class='section-sub'>Environmental Change Index by data center location</div>
        </div>
        """, unsafe_allow_html=True)
        st.plotly_chart(make_map(filtered, "ECI_score", "ECI Map"), use_container_width=True, config={"displayModeBar": False})
    with map2:
        st.markdown("""
        <div class='card section-card' style='border-bottom-left-radius:0;border-bottom-right-radius:0;'>
            <div class='section-title'>▧ ESS Map</div>
            <div class='section-sub'>Environmental Stress Score by data center location</div>
        </div>
        """, unsafe_allow_html=True)
        st.plotly_chart(make_map(filtered, "ESS_score", "ESS Map"), use_container_width=True, config={"displayModeBar": False})

    t1, t2 = st.columns(2, gap="medium")
    with t1:
        top_eci = filtered.sort_values("ECI_score", ascending=False).head(5)
        st.markdown(table_html(top_eci, "ECI_score", "Top 5 by Environmental Change"), unsafe_allow_html=True)
    with t2:
        top_ess = filtered.sort_values("ESS_score", ascending=False).head(5)
        st.markdown(table_html(top_ess, "ESS_score", "Top 5 by Environmental Stress"), unsafe_allow_html=True)

    st.markdown(
        """
        <div class='footer'>
            <span>ⓘ GeoAI transforms satellite-derived environmental indicators into early warning insights for decision-makers.</span>
            <span>ECI = environmental change | ESS = current environmental stress</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

with detail_col:
    st.markdown("<div class='card section-card'>", unsafe_allow_html=True)
    st.markdown("<div class='breadcrumb'>← Overview  ›  Hotspot Detail</div>", unsafe_allow_html=True)
    dsel = st.selectbox(
        "Select Hotspot",
        options=filtered["data_center_name"].tolist(),
        index=filtered["data_center_name"].tolist().index(st.session_state.selected_center),
        format_func=display_name,
        key="hotspot_selectbox",
    )
    st.session_state.selected_center = dsel
    selected = filtered[filtered["data_center_name"].eq(dsel)].iloc[0]
    center_df = df[df["data_center_name"].eq(dsel)].sort_values("Date")

    ctop1, ctop2, ctop3, ctop4 = st.columns([1.1,1,1,.95], gap="small")
    with ctop1:
        st.markdown(f"""
        <div class='card score-card'>
            <div style='font-size:14px;font-weight:900;color:#0F172A'>{display_name(dsel)}</div>
            <div style='font-size:11px;color:#64748B;font-weight:700;margin-top:10px;'>Data Center</div>
            <div style='font-size:11px;color:#64748B;font-weight:700;'>Lat {selected['latitude']:.3f}, Lon {selected['longitude']:.3f}</div>
        </div>
        """, unsafe_allow_html=True)
    with ctop2:
        lvl = level_from_score(selected["ECI_score"])
        st.markdown(f"""
        <div class='card score-card'>
            <div class='score-label'>ECI Score</div>
            <div class='score-value'>{selected['ECI_score']:.2f}<span class='badge {badge_class(lvl)}'>{lvl}</span></div>
            <div class='section-sub'>High rate of change</div>
        </div>
        """, unsafe_allow_html=True)
    with ctop3:
        lvl2 = level_from_score(selected["ESS_score"])
        st.markdown(f"""
        <div class='card score-card'>
            <div class='score-label'>ESS Score</div>
            <div class='score-value'>{selected['ESS_score']:.2f}<span class='badge {badge_class(lvl2)}'>{lvl2}</span></div>
            <div class='section-sub'>High environmental stress</div>
        </div>
        """, unsafe_allow_html=True)
    with ctop4:
        st.markdown(f"""
        <div class='card score-card'>
            <div class='score-label'>Key Drivers</div>
            <div style='font-size:11px;line-height:1.85;font-weight:800;color:#0F172A;margin-top:8px;'>
                🌡 High Surface Temperature<br>🌿 Vegetation Health<br>💧 Water Availability
            </div>
        </div>
        """, unsafe_allow_html=True)

    chart1, chart2 = st.columns(2, gap="medium")
    with chart1:
        st.markdown("""
        <div class='card section-card' style='border-bottom-left-radius:0;border-bottom-right-radius:0;'>
            <div class='section-title'>Land Surface Temperature</div>
            <div class='section-sub'>Monthly LST trend</div>
        </div>
        """, unsafe_allow_html=True)
        st.plotly_chart(line_chart(center_df, "mean_LST_C", "#E11D48", "°C"), use_container_width=True, config={"displayModeBar": False})
    with chart2:
        st.markdown("""
        <div class='card section-card' style='border-bottom-left-radius:0;border-bottom-right-radius:0;'>
            <div class='section-title'>Water Availability</div>
            <div class='section-sub'>Normalized Difference Water Index</div>
        </div>
        """, unsafe_allow_html=True)
        st.plotly_chart(line_chart(center_df, "mean_NDWI", "#2563EB", "Index"), use_container_width=True, config={"displayModeBar": False})

    cur_level = level_from_score(selected["risk_score"])
    st.markdown(f"""
    <div class='alert-box'>
        <div class='alert-icon'>⚠</div>
        <div style='flex:1'>
            <div class='alert-title'>AI Alert Summary</div>
            <div class='alert-text'>{display_name(dsel)} shows current environmental stress with rising heat pressure and reduced water availability compared with historical baseline. Continuous monitoring and proactive mitigation are recommended.</div>
        </div>
        <div style='width:150px'>
            <div style='font-size:11px;font-weight:900;color:#64748B;margin-bottom:7px;text-align:center;'>Overall Risk Level</div>
            <div class='big-risk' style='background:{risk_color(cur_level)}'>{cur_level.upper()}</div>
            <div style='font-size:10px;text-align:center;color:#64748B;font-weight:800;margin-top:6px;'>Priority Action Required</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    low1, low2 = st.columns(2, gap="medium")
    with low1:
        st.markdown(f"""
        <div class='card mini-card'>
            <div class='mini-title'>Community Alert</div>
            <div class='mini-text'><b>Alert Level:</b> {cur_level}<br><b>Issue Detected:</b> Heat stress and water stress near {display_name(dsel)}.</div>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("""
        <div class='card mini-card'>
            <div class='mini-title'>Community Resources</div>
            <div class='mini-text'>🔗 Local Water Authority<br>🔗 Heat Safety Tips<br>🔗 Report an Issue</div>
        </div>
        """, unsafe_allow_html=True)
    with low2:
        st.markdown("""
        <div class='card mini-card'>
            <div class='mini-title'>Recommended Actions</div>
            <div class='mini-text'>✅ Monitor local water storage and usage<br>✅ Avoid peak-hour outdoor activity<br>✅ Save water and use efficiently<br>✅ Follow official announcements</div>
        </div>
        """, unsafe_allow_html=True)
        st.markdown(f"""
        <div class='card mini-card'>
            <div class='mini-title'>AI Forecast</div>
            <div class='mini-text'><b>6 Months:</b> {selected['forecast_risk_score_6m']:.2f} / {selected['forecast_risk_level_6m']}<br><b>12 Months:</b> {selected['forecast_risk_score_12m']:.2f} / {selected['forecast_risk_level_12m']}</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

# ---------- Page behavior note for other nav buttons ----------
if st.session_state.selected_page != "Overview":
    st.toast(f"{st.session_state.selected_page} filter/page selected", icon="✅")
