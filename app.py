import json
from pathlib import Path
import pandas as pd
import streamlit as st
import streamlit.components.v1 as components

# 1. ตั้งค่าหน้าเพจ Streamlit ให้กว้างเต็มจอและซ่อนองค์ประกอบเริ่มต้น
st.set_page_config(
    page_title="DC-Resource Intelligence Platform",
    page_icon="🛰️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

DATA_FILE = Path("geosentinel_monthly_dashboard_data.csv")

@st.cache_data
def load_data():
    if not DATA_FILE.exists():
        st.error("ไม่พบไฟล์ geosentinel_monthly_dashboard_data.csv กรุณาวางไฟล์ไว้ในโฟลเดอร์เดียวกับสคริปต์นี้")
        st.stop()
    df = pd.read_csv(DATA_FILE)
    
    # แปลงชื่อคอลัมน์และเตรียมความพร้อมข้อมูล
    df["year_month"] = df["year_month"].astype(str)
    df["Year"] = df["year_month"].str.slice(0, 4)
    df["Display Name"] = df["data_center_name"].astype(str).str.replace("_", " ", regex=False)
    df = df.sort_values(["data_center_name", "year_month"])
    return df

df = load_data()

# แปลงข้อมูลเป็น JSON เพื่อส่งไปทำงานบน Frontend ฝั่ง HTML/JS
records_json = json.dumps(df.to_dict("records"), ensure_ascii=False)
years_json = json.dumps(sorted(df["Year"].unique().tolist()), ensure_ascii=False)
months_json = json.dumps(sorted(df["year_month"].unique().tolist()), ensure_ascii=False)
latest_year = sorted(df["Year"].unique().tolist())[-1]
latest_month = sorted(df[df["Year"] == latest_year]["year_month"].unique().tolist())[-1]

# ซ่อน Streamlit Elements เพื่อให้ผลลัพธ์ UI คุมหน้าจอได้สมบูรณ์แบบตามรูปภาพ
st.markdown(
    """
    <style>
      header[data-testid="stHeader"] {display:none!important;}
      #MainMenu, footer {visibility:hidden!important;}
      div[data-testid="stToolbar"] {display:none!important;}
      .block-container {padding:0!important; max-width:100%!important;}
      iframe {display:block; border:0!important;}
    </style>
    """,
    unsafe_allow_html=True,
)

# 2. HTML / CSS / JavaScript Template ปรับแต่งดีไซน์ตามตัวอย่างรูปภาพระดับ Pixel-Perfect
html_template = """
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8" />
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap" rel="stylesheet">
<style>
:root {
  --navy: #061A2F; --navy2: #03111F; --blue: #1268E8; --text: #08142D; --muted: #51627A;
  --line: #E8EEF5; --bg: #F5F8FC; --card: #FFFFFF; --red: #E63145; --orange: #F97316;
  --yellow: #FACC15; --green: #22C55E; --purple: #6D42E8; --softBlue: #E8F3FF;
}
* { box-sizing: border-box; font-family: 'Inter', sans-serif; }
html, body { margin: 0; padding: 0; background: var(--bg); color: var(--text); overflow-x: auto; }

/* โครงสร้างหลัก 3 คอลัมน์ ตามภาพตัวอย่าง */
.app { width: 1620px; min-height: 1080px; display: grid; grid-template-columns: 200px 780px 640px; background: var(--bg); }

/* คอลัมน์ที่ 1: Sidebar (ซ้าย) */
.sidebar { background: linear-gradient(180deg, var(--navy), var(--navy2)); padding: 24px 16px; color: white; position: relative; border-right: 1px solid var(--line); }
.brand { display: flex; align-items: center; gap: 10px; margin-bottom: 6px; }
.logo { width: 28px; height: 28px; border-radius: 8px; background: #0EBA74; display: flex; align-items: center; justify-content: center; font-size: 16px; font-weight: bold; color: white; }
.brand-title { font-size: 16px; font-weight: 800; letter-spacing: -0.01em; }
.brand-sub { font-size: 11px; color: #8FA0B5; margin-bottom: 32px; line-height: 1.4; }
.nav { display: flex; flex-direction: column; gap: 8px; }
.nav-btn { height: 40px; border: 0; background: transparent; color: #A3B8CC; border-radius: 8px; padding: 0 12px; text-align: left; font-size: 13px; font-weight: 600; cursor: pointer; display: flex; align-items: center; gap: 12px; transition: all 0.2s; }
.nav-btn.active, .nav-btn:hover { background: #0F2942; color: white; }
.nav-btn.active { background: #1268E8; }
.source-box { position: absolute; left: 16px; right: 16px; bottom: 24px; background: rgba(255,255,255,0.04); border: 1px solid rgba(255,255,255,0.08); border-radius: 10px; padding: 12px; font-size: 11px; color: #8FA0B5; line-height: 1.5; }

/* คอลัมน์ที่ 2: Overview (กลาง) */
.main { padding: 24px; border-right: 1px solid var(--line); overflow-y: auto; }
.header { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 24px; }
.header-text h1 { font-size: 24px; font-weight: 800; margin: 0 0 4px 0; letter-spacing: -0.02em; }
.header-text p { font-size: 13px; margin: 0; color: var(--muted); }
.date-box { height: 38px; padding: 0 14px; border: 1px solid var(--line); border-radius: 8px; display: flex; align-items: center; gap: 8px; background: #fff; font-size: 13px; font-weight: 600; cursor: pointer; position: relative; box-shadow: 0 2px 4px rgba(0,0,0,0.02); }
.filter-pop { display: none; position: absolute; top: 44px; right: 0; width: 220px; background: #fff; border: 1px solid var(--line); border-radius: 10px; box-shadow: 0 10px 25px rgba(0,0,0,0.1); padding: 16px; z-index: 1000; }
.date-box.open .filter-pop { display: block; }
.f-title { font-size: 11px; color: var(--muted); font-weight: 700; text-transform: uppercase; margin-bottom: 6px; }
.pop-select { width: 100%; border: 1px solid var(--line); border-radius: 6px; height: 32px; padding: 0 8px; font-size: 12px; margin-bottom: 12px; }

/* KPIs Grid */
.kpis { display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px; margin-bottom: 20px; }
.kpi { background: #fff; border: 1px solid var(--line); border-radius: 12px; padding: 16px; display: flex; align-items: center; gap: 12px; box-shadow: 0 2px 6px rgba(9,36,70,0.02); }
.kpi-icon { width: 42px; height: 42px; border-radius: 10px; display: flex; align-items: center; justify-content: center; font-size: 20px; }
.kpi-title { font-size: 11px; font-weight: 700; color: var(--muted); text-transform: uppercase; }
.kpi-value { font-size: 24px; font-weight: 800; margin-top: 2px; }
.kpi-sub { font-size: 11px; color: var(--muted); margin-top: 4px; }

/* Maps & Tables */
.grid-2 { display: grid; grid-template-columns: 1fr 1fr; gap: 14px; margin-bottom: 16px; }
.card { background: #fff; border: 1px solid var(--line); border-radius: 12px; padding: 16px; box-shadow: 0 2px 6px rgba(9,36,70,0.02); }
.card-title { font-size: 13px; font-weight: 700; display: flex; justify-content: space-between; align-items: center; margin-bottom: 4px; }
.card-sub { font-size: 11px; color: var(--muted); margin-bottom: 12px; }
.mapbox { height: 240px; border-radius: 8px; background: #EBF3FC; position: relative; overflow: hidden; border: 1px solid var(--line); }
.us-shape { position: absolute; inset: 10px; background: #FFFFFF; clip-path: polygon(10% 30%, 25% 15%, 45% 20%, 65% 10%, 90% 20%, 95% 50%, 85% 80%, 60% 75%, 40% 85%, 15% 70%); border-radius: 20px; opacity: 0.7; }
.map-point { position: absolute; width: 12px; height: 12px; border-radius: 50%; border: 2px solid white; transform: translate(-50%, -50%); cursor: pointer; box-shadow: 0 2px 4px rgba(0,0,0,0.2); }
.map-point.active { ring: 3px solid var(--blue); scale: 1.3; z-index: 10; }
.map-legend { position: absolute; left: 10px; bottom: 10px; background: white; padding: 6px 10px; border-radius: 6px; font-size: 9px; border: 1px solid var(--line); line-height: 1.4; }

/* Tables */
table { width: 100%; border-collapse: collapse; font-size: 12px; }
th { text-align: left; padding: 8px; color: var(--muted); font-weight: 600; border-bottom: 1px solid var(--line); font-size: 11px; }
td { padding: 8px; border-bottom: 1px solid #F0F4F8; vertical-align: middle; }
.badge { padding: 2px 6px; border-radius: 4px; font-size: 10px; font-weight: 700; display: inline-block; }
.badge.Critical { background: #FFE5E7; color: #D92D20; }
.badge.Concern { background: #FFEAD5; color: #E05300; }
.badge.Watch { background: #FEF3C7; color: #B57F1E; }
.badge.Stable, .badge.Low { background: #ECFDF3; color: #039855; }

/* คอลัมน์ที่ 3: Hotspot & Alerts Detail (ขวา) */
.right-panel { padding: 24px; overflow-y: auto; height: 1080px; background: white; }
.r-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px; border-bottom: 1px solid var(--line); padding-bottom: 12px; }
.r-title { font-size: 16px; font-weight: 800; }
.r-crumb { font-size: 11px; color: var(--muted); margin-top: 2px; }
.select-box { height: 32px; border: 1px solid var(--line); border-radius: 6px; padding: 0 8px; font-size: 12px; font-weight: 600; }

.mini-grid { display: grid; grid-template-columns: 1.2fr 1fr 1fr 1.2fr; gap: 8px; margin-bottom: 16px; }
.mini-card { border: 1px solid var(--line); border-radius: 8px; padding: 10px; background: var(--bg); }
.mini-title { font-size: 10px; font-weight: 700; color: var(--muted); text-transform: uppercase; }
.mini-value { font-size: 20px; font-weight: 800; margin: 4px 0; }

.chart-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin-bottom: 16px; }
.chart-card { border: 1px solid var(--line); border-radius: 8px; padding: 12px; }
.chart-title { font-size: 11px; font-weight: 700; margin-bottom: 8px; color: var(--text); }
.spark-svg { width: 100%; height: 100px; }

/* Alert Boxes */
.alert-banner { background: #FFF5F5; border: 1px solid #FEE4E4; border-radius: 10px; padding: 14px; display: flex; gap: 12px; align-items: flex-start; margin-bottom: 20px; }
.alert-icon-box { width: 36px; height: 36px; border-radius: 50%; background: var(--red); color: white; display: flex; align-items: center; justify-content: center; font-weight: bold; font-size: 18px; }
.alert-banner-text { flex: 1; font-size: 12px; line-height: 1.5; }
.risk-badge-large { background: var(--red); color: white; padding: 6px 12px; border-radius: 6px; font-weight: 800; text-align: center; font-size: 14px; margin-top: 4px; }

.section-divider { font-size: 13px; font-weight: 700; margin: 24px 0 12px 0; display: flex; align-items: center; gap: 8px; }
.sub-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin-bottom: 12px; }
.info-block { border: 1px solid var(--line); border-radius: 8px; padding: 12px; font-size: 11px; line-height: 1.5; }
.info-block-title { font-size: 11px; font-weight: 700; margin-bottom: 6px; color: var(--text); }

/* Email Subscribe */
.email-box { display: flex; gap: 6px; margin-top: 8px; }
.email-input { height: 30px; flex: 1; border: 1px solid var(--line); border-radius: 4px; padding: 0 8px; font-size: 11px; }
.email-btn { background: var(--blue); color: white; border: 0; border-radius: 4px; padding: 0 12px; font-size: 11px; font-weight: 600; cursor: pointer; }

.footer-bar { margin-top: 24px; padding-top: 12px; border-top: 1px solid var(--line); font-size: 10px; color: var(--muted); display: flex; justify-content: space-between; }
</style>
</head>
<body>

<div class="app">
  <aside class="sidebar">
    <div class="brand">
      <div class="logo">🛰️</div>
      <div class="brand-title">GeoSentinel AI</div>
    </div>
    <div class="brand-sub">Environmental<br/>Early Warning System</div>
    <div class="nav">
      <button class="nav-btn active">📊 Overview</button>
      <button class="nav-btn">🎯 Hotspot Detail</button>
      <button class="nav-btn">🔔 Alerts</button>
      <button class="nav-btn">🏢 Data Centers</button>
      <button class="nav-btn">📈 Trends</button>
      <button class="nav-btn">📄 Reports</button>
      <button class="nav-btn">ℹ️ About</button>
    </div>
    <div class="source-box">
      <b>Data Source</b><br/>
      Google Earth Engine<br/>
      (2019 – 2026)
    </div>
  </aside>

  <main class="main">
    <div class="header">
      <div class="header-text">
        <h1>Overview Dashboard</h1>
        <p>Real-time environmental monitoring of data centers across the United States</p>
      </div>
      <div class="date-box" id="filterToggle">
          <span id="dateLabel">-</span> ▾
        <div class="filter-pop" onclick="event.stopPropagation()">
          <div class="f-title">Year Filter</div>
          <select id="yearSelect" class="pop-select"></select>
          <div class="f-title">Month Filter</div>
          <select id="monthSelect" class="pop-select"></select>
        </div>
      </div>
    </div>

    <div class="kpis" id="kpiContainer"></div>

    <div class="grid-2">
      <div class="card" id="eciMapCard"></div>
      <div class="card" id="essMapCard"></div>
    </div>

    <div class="grid-2">
      <div class="card">
        <div class="card-title"><span>Top 5 by Environmental Change (ECI)</span><span style="color:var(--blue);cursor:pointer;font-size:11px;">View all</span></div>
        <div class="card-sub">Highest rates of environmental change detection</div>
        <table id="eciTable"><thead><tr><th>Rank</th><th>Data Center</th><th>ECI Score</th><th>Level</th><th>Trend</th></tr></thead><tbody></tbody></table>
      </div>
      <div class="card">
        <div class="card-title"><span>Top 5 by Environmental Stress (ESS)</span><span style="color:var(--blue);cursor:pointer;font-size:11px;">View all</span></div>
        <div class="card-sub">Highest active environmental stress indicators</div>
        <table id="essTable"><thead><tr><th>Rank</th><th>Data Center</th><th>ESS Score</th><th>Level</th><th>Trend</th></tr></thead><tbody></tbody></table>
      </div>
    </div>

    <div style="background:linear-gradient(90deg, #E8F3FF, #F5F9FF); border:1px solid #CCE3FC; border-radius:10px; padding:12px; font-size:11px; display:flex; gap:16px; align-items:center; color:#1E3A8A;">
      <span style="font-size:16px;">ℹ️</span>
      <div><b>DC-Resource Intelligence Platform</b> transforms satellite-derived environmental indicators into early warning insights. <br/>🟢 <b>ECI</b> detects rapid historical deviation. 🟠 <b>ESS</b> monitors active current ecosystem pressure.</div>
    </div>
  </main>

  <section class="right-panel">
    <div class="r-header">
      <div>
        <div class="r-title">Hotspot Detail</div>
        <div class="r-crumb">Overview • Hotspot Assessment</div>
      </div>
      <select class="select-box" id="hotspotSelect"></select>
    </div>

    <div class="mini-grid" id="miniGridContainer"></div>

    <div class="chart-grid">
      <div class="chart-card">
        <div class="chart-title">Land Surface Temperature (LST) ⓘ</div>
        <svg class="spark-svg" id="lstChartSvg"></svg>
      </div>
      <div class="chart-card">
        <div class="chart-title">Normalized Difference Water Index (NDWI) ⓘ</div>
        <svg class="spark-svg" id="ndwiChartSvg"></svg>
      </div>
    </div>

    <div class="alert-banner" id="aiAlertBox"></div>

    <div class="section-divider"><span>🔔 Community Alert</span></div>
    
    <div class="sub-grid">
      <div class="info-block" id="alertLevelCard"></div>
      <div class="info-block">
        <div class="info-block-title">Issue Detected</div>
        <b>High Heat & Water Stress Trend</b><br/>
        <span style="color:var(--muted); font-size:10.5px;">Satellite records indicate notable heat retention and drop in surface moisture profiles over the last quarter.</span>
      </div>
    </div>

    <div class="sub-grid">
      <div class="info-block">
        <div class="info-block-title">What does this mean?</div>
        <span style="color:var(--muted);">The surrounding microclimate is currently carrying high operational stress loads. Localized warming or vegetation reduction may affect immediate infrastructure resource demands.</span>
      </div>
      <div class="info-block">
        <div class="info-block-title">Recommended Actions</div>
        <span style="font-size:10px; line-height:1.4;">
          ✔️ Optimize cooling resource cycles<br/>
          ✔️ Monitor local watershed changes<br/>
          ✔️ Review sustainability compliance<br/>
          ✔️ Coordinate updates with local authorities
        </span>
      </div>
    </div>

    <div class="sub-grid">
      <div class="info-block">
        <div class="info-block-title">Community Resources</div>
        <span style="color:var(--blue); font-weight:500; cursor:pointer;">
          💧 Local Water Authority ↗<br/>
          🌡️ Microclimate Safety Guidelines ↗<br/>
          📋 Submit Field Report ↗
        </span>
      </div>
      <div class="info-block">
        <div class="info-block-title">Stay Informed</div>
        <span style="color:var(--muted);">Get automated changes alerts.</span>
        <div class="email-box">
          <input class="email-input" placeholder="name@domain.com"/>
          <button class="email-btn">Subscribe</button>
        </div>
      </div>
    </div>

    <div class="footer-bar">
      <span>🛡️ GeoSentinel Platform v2.4</span>
      <span>System Update: 2026</span>
    </div>
  </section>
</div>

<script>
// จัดการข้อมูลที่ถูกส่งมาจากฝั่ง Python Pandas ข้ามมายัง JS
const DATA = __RECORDS_JSON__;
const YEARS = __YEARS_JSON__;
const ALL_MONTHS = __MONTHS_JSON__;

let state = {
  year: __LATEST_YEAR_JSON__,
  month: __LATEST_MONTH_JSON__,
  hotspot: null
};

function cleanName(s) { return String(s || '').replace(/_/g, ' '); }
function fmt(n) { return Number.isFinite(Number(n)) ? Number(n).toFixed(2) : '-'; }

function getLevel(score) {
  const s = Number(score);
  if (s >= 70) return 'Critical';
  if (s >= 50) return 'Concern';
  if (s >= 35) return 'Watch';
  return 'Stable';
}

function getColor(level) {
  return { 'Critical': '#E63145', 'Concern': '#F97316', 'Watch': '#FACC15', 'Stable': '#22C55E', 'Low': '#22C55E' }[level] || '#64748B';
}

// ผูกฟังก์ชันเปิด/ปิดตัวเลือกกรองวันที่
document.getElementById('filterToggle').onclick = function(e) {
  this.classList.toggle('open');
};

function initFilters() {
  document.getElementById('dateLabel').textContent = state.month;
  
  const ySel = document.getElementById('yearSelect');
  ySel.innerHTML = YEARS.map(y => `<option value="${y}" ${state.year===y?'selected':''}>${y}</option>`).join('');
  ySel.onchange = (e) => {
    state.year = e.target.value;
    const available = ALL_MONTHS.filter(m => m.startsWith(state.year));
    state.month = available[available.length - 1];
    renderAll();
  };

  const mSel = document.getElementById('monthSelect');
  const filteredMonths = ALL_MONTHS.filter(m => m.startsWith(state.year));
  mSel.innerHTML = filteredMonths.map(m => `<option value="${m}" ${state.month===m?'selected':''}>${m}</option>`).join('');
  mSel.onchange = (e) => {
    state.month = e.target.value;
    renderAll();
  };
}

// วาดกราฟเส้นจิ๋ว (Sparklines) ด้านในตาราง Top 5 เพื่อความสวยงามเหมือนต้นฉบับ
function generateTableSparkline(dcName, scoreCol, color) {
  const history = DATA.filter(r => r.data_center_name === dcName).sort((a,b) => String(a.year_month).localeCompare(String(b.year_month)));
  if (history.length < 2) return '-';
  const vals = history.map(h => Number(h[scoreCol])).filter(Number.isFinite);
  const min = Math.min(...vals), max = Math.max(...vals);
  const range = (max - min) === 0 ? 1 : (max - min);
  
  const w = 60, h = 16;
  const points = history.map((h, i) => {
    const x = (i / (history.length - 1)) * w;
    const y = h - ((Number(h[scoreCol]) - min) / range) * h;
    return `${x.toFixed(1)},${y.toFixed(1)}`;
  }).join(' ');
  
  return `<svg width="${w}" height="${h}"><polyline points="${points}" fill="none" stroke="${color}" stroke-width="1.5"/></svg>`;
}

function renderKPIs(currentData) {
  const uniqueDCs = new Set(DATA.map(r => r.data_center_name)).size;
  const criticalECI = currentData.filter(r => Number(r.ECI_score) >= 60).length;
  const criticalESS = currentData.filter(r => Number(r.ESS_score) >= 60).length;
  
  const topDC = [...currentData].sort((a,b) => Number(b.risk_score) - Number(a.risk_score))[0];
  const topName = topDC ? cleanName(topDC.data_center_name) : 'None';

  document.getElementById('kpiContainer').innerHTML = `
    <div class="kpi">
      <div class="kpi-icon" style="background:#EBF3FC; color:#1268E8;">🏢</div>
      <div>
        <div class="kpi-title">Monitored Facilities</div>
        <div class="kpi-value">${uniqueDCs}</div>
        <div class="kpi-sub">Data centers active</div>
      </div>
    </div>
    <div class="kpi">
      <div class="kpi-icon" style="background:#FFE5E7; color:#E63145;">📈</div>
      <div>
        <div class="kpi-title">Critical ECI</div>
        <div class="kpi-value">${criticalECI}</div>
        <div class="kpi-sub">Rapid shift zones</div>
      </div>
    </div>
    <div class="kpi">
      <div class="kpi-icon" style="background:#FFEAD5; color:#F97316;">⚠️</div>
      <div>
        <div class="kpi-title">Critical ESS</div>
        <div class="kpi-value">${criticalESS}</div>
        <div class="kpi-sub">High stress zones</div>
      </div>
    </div>
    <div class="kpi">
      <div class="kpi-icon" style="background:#F0EBFB; color:#6D42E8;">🎯</div>
      <div>
        <div class="kpi-title">Top Hotspot</div>
        <div class="kpi-value" style="font-size:14px; color:var(--purple); max-width:130px; overflow:hidden; text-overflow:ellipsis; white-space:nowrap;">${topName}</div>
        <div class="kpi-sub">Risk Score: ${topDC ? fmt(topDC.risk_score) : '-'}</div>
      </div>
    </div>
  `;
}

function renderMaps(currentData) {
  // ฟังก์ชันแปลงพิกัดจำลองพิกัด US บรรจุลงในกล่อง SVG ของการ์ด
  const getPointsHTML = (scoreField) => currentData.map(r => {
    const lat = Number(r.latitude), lon = Number(r.longitude);
    const x = ((lon + 125) / (-66 + 125)) * 100;
    const y = (1 - (lat - 24) / (50 - 24)) * 100;
    const color = getColor(getLevel(r[scoreField]));
    const isTarget = r.data_center_name === state.hotspot ? 'active' : '';
    return `<div class="map-point ${isTarget}" style="left:${x}%; top:${y}%; background:${color};" onclick="selectHotspot('${r.data_center_name}')" title="${cleanName(r.data_center_name)}"></div>`;
  }).join('');

  const legendHTML = `<div class="map-legend"><span style="color:#22C55E">●</span> Stable <span style="color:#FACC15">●</span> Watch <span style="color:#F97316">●</span> Concern <span style="color:#E63145">●</span> Critical</div>`;

  document.getElementById('eciMapCard').innerHTML = `
    <div class="card-title">ECI Map (Environmental Change Index) ⓘ</div>
    <div class="card-sub">Geospatial change detection rates</div>
    <div class="mapbox"><div class="us-shape"></div>${getPointsHTML('ECI_score')}${legendHTML}</div>
  `;
  document.getElementById('essMapCard').innerHTML = `
    <div class="card-title">ESS Map (Environmental Stress Score) ⓘ</div>
    <div class="card-sub">Active ecosystem pressure mapping</div>
    <div class="mapbox"><div class="us-shape"></div>${getPointsHTML('ESS_score')}${legendHTML}</div>
  `;
}

function renderTables(currentData) {
  const topECI = [...currentData].sort((a,b) => Number(b.ECI_score) - Number(a.ECI_score)).slice(0, 5);
  const topESS = [...currentData].sort((a,b) => Number(b.ESS_score) - Number(a.ESS_score)).slice(0, 5);

  document.getElementById('eciTable').querySelector('tbody').innerHTML = topECI.map((r, i) => `
    <tr style="cursor:pointer;" onclick="selectHotspot('${r.data_center_name}')">
      <td>${i+1}</td>
      <td><b>${cleanName(r.data_center_name)}</b></td>
      <td>${fmt(r.ECI_score)}</td>
      <td><span class="badge ${getLevel(r.ECI_score)}">${getLevel(r.ECI_score)}</span></td>
      <td>${generateTableSparkline(r.data_center_name, 'ECI_score', '#E63145')}</td>
    </tr>
  `).join('');

  document.getElementById('essTable').querySelector('tbody').innerHTML = topESS.map((r, i) => `
    <tr style="cursor:pointer;" onclick="selectHotspot('${r.data_center_name}')">
      <td>${i+1}</td>
      <td><b>${cleanName(r.data_center_name)}</b></td>
      <td>${fmt(r.ESS_score)}</td>
      <td><span class="badge ${getLevel(r.ESS_score)}">${getLevel(r.ESS_score)}</span></td>
      <td>${generateTableSparkline(r.data_center_name, 'ESS_score', '#F97316')}</td>
    </tr>
  `).join('');
}

function renderHotspotSection(currentData) {
  const hSel = document.getElementById('hotspotSelect');
  hSel.innerHTML = currentData.map(r => `<option value="${r.data_center_name}" ${r.data_center_name===state.hotspot?'selected':''}>${cleanName(r.data_center_name)}</option>`).join('');
  hSel.onchange = (e) => { selectHotspot(e.target.value); };

  const activeRec = currentData.find(r => r.data_center_name === state.hotspot) || currentData[0];
  if (!activeRec) return;

  // Mini Cards Setup
  document.getElementById('miniGridContainer').innerHTML = `
    <div class="mini-card"><div class="mini-title">Facility Cluster</div><div class="mini-value" style="font-size:12px;margin-top:8px;color:#111827;"><b>${cleanName(activeRec.data_center_name)}</b></div></div>
    <div class="mini-card"><div class="mini-title">ECI Score</div><div class="mini-value">${fmt(activeRec.ECI_score)}</div><span class="badge ${getLevel(activeRec.ECI_score)}">${getLevel(activeRec.ECI_score)}</span></div>
    <div class="mini-card"><div class="mini-title">ESS Score</div><div class="mini-value">${fmt(activeRec.ESS_score)}</div><span class="badge ${getLevel(activeRec.ESS_score)}">${getLevel(activeRec.ESS_score)}</span></div>
    <div class="mini-card"><div class="mini-title">Risk Level</div><div class="mini-value" style="font-size:15px;color:${getColor(getLevel(activeRec.risk_score))}">${getLevel(activeRec.risk_score).toUpperCase()}</div></div>
  `;

  // Draw Detailed Line Charts (LST & NDWI)
  drawPanelChart('lstChartSvg', activeRec.data_center_name, 'mean_LST_C', '#E63145', 'rgba(230,49,69,0.1)');
  drawPanelChart('ndwiChartSvg', activeRec.data_center_name, 'mean_NDWI', '#1268E8', 'rgba(18,104,232,0.1)');

  // AI Alert Content
  const overallLevel = getLevel(activeRec.risk_score);
  document.getElementById('aiAlertBox').innerHTML = `
    <div class="alert-icon-box">⚠️</div>
    <div class="alert-banner-text">
      <b>AI Alert Summary (${cleanName(activeRec.data_center_name)})</b><br/>
      The platform detected an elevation in climate variability markers relative to core spatial baselines. Active optimization protocols are advised.
    </div>
    <div>
      <div class="risk-badge-large" style="background:${getColor(overallLevel)}">${overallLevel.toUpperCase()}</div>
    </div>
  `;

  // Community Alert Summary Card
  document.getElementById('alertLevelCard').innerHTML = `
    <div class="info-block-title">Alert Status</div>
    <span class="badge ${overallLevel}" style="font-size:14px; padding:4px 10px;">${overallLevel.toUpperCase()}</span>
    <div style="margin-top:10px; color:var(--muted); font-size:10px;">Period Focus:<br/><b>${state.month}</b></div>
  `;
}

function drawPanelChart(svgId, dcName, col, color, fillBg) {
  const svg = document.getElementById(svgId);
  const history = DATA.filter(r => r.data_center_name === dcName).sort((a,b) => String(a.year_month).localeCompare(String(b.year_month)));
  if (!history.length) { svg.innerHTML = ''; return; }

  const width = 260, height = 100, padding = 15;
  const vals = history.map(h => Number(h[col])).filter(Number.isFinite);
  const min = Math.min(...vals), max = Math.max(...vals);
  const delta = (max - min) === 0 ? 1 : (max - min);

  const points = history.map((h, i) => {
    const x = padding + (i / (history.length - 1)) * (width - padding * 2);
    const y = (height - padding) - ((Number(h[col]) - min) / delta) * (height - padding * 2);
    return [x, y];
  });

  const linePath = points.map(p => p.join(',')).join(' ');
  const areaPath = `${padding},${height-padding} ` + linePath + ` ${width-padding},${height-padding}`;

  svg.setAttribute('viewBox', `0 0 ${width} ${height}`);
  svg.innerHTML = `
    <line x1="${padding}" y1="${height/2}" x2="${width-padding}" y2="${height/2}" stroke="#F0F4F8" stroke-dasharray="3,3" />
    <polygon points="${areaPath}" fill="${fillBg}"></polygon>
    <polyline points="${linePath}" fill="none" stroke="${color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"></polyline>
    <circle cx="${points[points.length-1][0]}" cy="${points[points.length-1][1]}" r="3.5" fill="${color}"></circle>
    <text x="${width - padding}" y="${height - 2}" text-anchor="end" font-size="9" fill="#718096">${history[history.length-1].year_month}</text>
    <text x="${padding}" y="${padding - 4}" font-size="10" font-weight="bold" fill="${color}">${fmt(history[history.length-1][col])}</text>
  `;
}

function selectHotspot(name) {
  state.hotspot = name;
  const currentData = DATA.filter(r => String(r.year_month) === state.month);
  renderHotspotSection(currentData);
  renderMaps(currentData);
}

function renderAll() {
  initFilters();
  const currentData = DATA.filter(r => String(r.year_month) === state.month);
  
  if (currentData.length && (!state.hotspot || !currentData.find(r => r.data_center_name === state.hotspot))) {
    state.hotspot = currentData[0].data_center_name;
  }
  
  renderKPIs(currentData);
  renderMaps(currentData);
  renderTables(currentData);
  renderHotspotSection(currentData);
}

// เริ่มต้นเรียกใช้งานระบบครั้งแรก
renderAll();
</script>

</body>
</html>
"""

# 3. นำข้อมูลความปลอดภัยมาประกอบร่าง (Plain-string replacement ตัดโอกาส Error)
html_rendered = html_template.replace("__RECORDS_JSON__", records_json)\
                             .replace("__YEARS_JSON__", years_json)\
                             .replace("__MONTHS_JSON__", months_json)\
                             .replace("__LATEST_YEAR_JSON__", json.dumps(latest_year))\
                             .replace("__LATEST_MONTH_JSON__", json.dumps(latest_month))

# ส่งผลลัพธ์แสดงผลในความกว้างหน้าจอขนาดใหญ่ตามตารางจัดวาง
components.html(html_rendered, height=1100, scrolling=True)