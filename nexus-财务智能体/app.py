# -*- coding: utf-8 -*-
import streamlit as st
import os
import time
import plotly.graph_objects as go
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Page Config
st.set_page_config(
    page_title="Nexus 财务智能体 v3.2",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==========================================
# 🎨 NEXUS UI ENGINE v3.2 (CSS INJECTION)
# ==========================================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;800&family=JetBrains+Mono:wght@400;700&display=swap');

    /* --- GLOBAL RESET & TYPOGRAPHY --- */
    .stApp {
        background: #050505; /* Deepest Black */
        background-image: 
            radial-gradient(at 0% 0%, rgba(56, 189, 248, 0.1) 0px, transparent 50%),
            radial-gradient(at 100% 100%, rgba(139, 92, 246, 0.1) 0px, transparent 50%);
        color: #e2e8f0;
        font-family: 'Inter', sans-serif;
        /* Critical: Makes text sharper on dark backgrounds */
        -webkit-font-smoothing: antialiased; 
        -moz-osx-font-smoothing: grayscale;
    }

    /* Force all text to be readable */
    h1, h2, h3, h4, h5, h6 {
        color: #ffffff !important;
        font-weight: 700;
        letter-spacing: -0.5px;
    }
    p, li, label, .stMarkdown {
        color: #cbd5e1 !important; /* Slate-300 (High readability gray) */
        font-weight: 400;
        line-height: 1.6;
    }
    
    /* --- SIDEBAR REINVENTION --- */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #020617 0%, #0f172a 100%);
        border-right: 1px solid rgba(30, 41, 59, 0.8);
        box-shadow: 10px 0 30px rgba(0,0,0,0.5);
    }
    
    /* Sidebar Text Specifics */
    section[data-testid="stSidebar"] h1, 
    section[data-testid="stSidebar"] h2, 
    section[data-testid="stSidebar"] h3 {
        color: #38bdf8 !important; /* Light Blue Title */
        text-transform: uppercase;
        font-size: 12px;
        letter-spacing: 1px;
        margin-top: 20px;
    }
    section[data-testid="stSidebar"] p, 
    section[data-testid="stSidebar"] span,
    section[data-testid="stSidebar"] div {
        color: #f1f5f9 !important; /* Pure White Text in Sidebar */
        font-size: 14px;
    }

    /* --- COMPONENT STYLING --- */
    
    /* Input Fields (HUD Style) */
    div[data-baseweb="input"] {
        background-color: rgba(15, 23, 42, 0.8) !important; /* Darker background for text contrast */
        border: 1px solid #334155 !important;
        border-radius: 6px !important;
    }
    input[type="text"] {
        color: #ffffff !important;
        font-family: 'JetBrains Mono', monospace;
    }
    /* Focus state for input */
    div[data-baseweb="input"]:focus-within {
        border-color: #00f3ff !important;
        box-shadow: 0 0 10px rgba(0, 243, 255, 0.2);
    }

    /* Buttons */
    button[kind="primary"] {
        background: linear-gradient(90deg, #2563eb, #7c3aed) !important;
        border: none !important;
        color: white !important;
        font-weight: 600 !important;
        box-shadow: 0 4px 14px rgba(124, 58, 237, 0.4) !important;
        transition: all 0.2s;
    }
    button[kind="primary"]:hover {
        transform: translateY(-1px);
        box-shadow: 0 6px 20px rgba(124, 58, 237, 0.6) !important;
    }

    /* --- CUSTOM CARDS --- */
    .nexus-card {
        background: rgba(17, 24, 39, 0.7); /* Darker glass */
        backdrop-filter: blur(12px);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 12px;
        padding: 24px;
        margin-bottom: 20px;
        position: relative;
        overflow: hidden;
    }
    .nexus-card::before {
        content: '';
        position: absolute;
        top: 0; left: 0; w: 2px; h: 100%;
        background: linear-gradient(to bottom, #00f3ff, transparent);
        opacity: 0.5;
    }

    /* Metric Box */
    .metric-box {
        background: rgba(0,0,0,0.4);
        border: 1px solid #1e293b;
        border-radius: 8px;
        padding: 16px;
        text-align: center;
    }
    .metric-label { font-size: 12px; color: #94a3b8; text-transform: uppercase; letter-spacing: 0.5px; }
    .metric-value { font-size: 28px; font-weight: 700; color: #f8fafc; font-family: 'JetBrains Mono'; }
    
    /* File Artifacts in Sidebar */
    .file-item {
        display: flex;
        align-items: center;
        padding: 10px;
        background: rgba(255,255,255,0.03);
        border: 1px solid rgba(255,255,255,0.05);
        border-radius: 6px;
        margin-bottom: 8px;
        transition: all 0.2s;
    }
    .file-item:hover {
        background: rgba(255,255,255,0.08);
        border-color: #38bdf8;
    }
    
    /* Hide Default Streamlit clutter */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# ==========================================
# 🧠 LOGIC & COMPONENTS
# ==========================================

def render_header():
    st.markdown("""
    <div class="nexus-card" style="border-left: 4px solid #00f3ff; padding-left: 24px;">
        <div style="display:flex; justify-content:space-between; align-items:center;">
            <div>
                <h1 style="margin:0; font-size: 42px; background: linear-gradient(to right, #fff, #94a3b8); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">
                    NEXUS <span style="font-weight:300;">INTELLIGENCE</span>
                </h1>
                <div style="display:flex; gap:10px; align-items:center; margin-top:8px;">
                    <span style="padding:2px 8px; background:rgba(16, 185, 129, 0.2); color:#34d399; border-radius:4px; font-size:11px; font-weight:600; border:1px solid rgba(16, 185, 129, 0.3);">
                        ● SYSTEM ONLINE
                    </span>
                    <span style="font-family:'JetBrains Mono'; font-size:12px; color:#64748b;">
                        v3.2.0 // CLASSIFIED
                    </span>
                </div>
            </div>
            <div style="text-align:right; opacity:0.8;">
                <div style="font-family:'JetBrains Mono'; font-size:32px; color:#38bdf8; font-weight:bold;">06</div>
                <div style="font-size:11px; color:#94a3b8; letter-spacing:1px;">ACTIVE AGENTS</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

def render_terminal_logs(logs):
    # Modern Terminal Look: Black background, bright distinct text
    log_html = ""
    for log in logs:
        color = "#94a3b8" # Default gray
        if "[INFO]" in log: color = "#60a5fa" # Blue
        if "[SUCCESS]" in log: color = "#4ade80" # Green
        if "[WARNING]" in log: color = "#fbbf24" # Amber
        if "[ALERT]" in log: color = "#f87171" # Red
        if ">>" in log: color = "#c084fc" # Purple
        
        log_html += f'<div style="color:{color}; margin-bottom:4px;">{log}</div>'
        
    st.markdown(f"""
    <div style="
        background: #09090b; 
        border: 1px solid #27272a; 
        border-radius: 8px; 
        padding: 16px; 
        font-family: 'JetBrains Mono', monospace; 
        font-size: 13px; 
        height: 350px; 
        overflow-y: auto;
        box-shadow: inset 0 0 20px rgba(0,0,0,0.8);">
        {log_html}
        <div style="margin-top:10px; color:#00f3ff; animation: blink 1s infinite;">▋</div>
    </div>
    <style>@keyframes blink {{ 0%, 100% {{ opacity: 1; }} 50% {{ opacity: 0; }} }}</style>
    """, unsafe_allow_html=True)

# ==========================================
# 🚀 MAIN EXECUTION
# ==========================================

# Sidebar
with st.sidebar:
    st.markdown("### 📁 ARTIFACTS REPOSITORY")
    files = [
        {"icon": "📄", "name": "analysis_report.pdf", "meta": "PDF • 156 KB"},
        {"icon": "📉", "name": "trend_viz.png", "meta": "PNG • 90 KB"},
        {"icon": "🕸️", "name": "debt_struct.json", "meta": "JSON • 85 KB"},
    ]
    for f in files:
        st.markdown(f"""
        <div class="file-item">
            <span style="font-size: 18px; margin-right: 10px;">{f['icon']}</span>
            <div style="flex:1;">
                <div style="color:#e2e8f0; font-weight:500; font-size:13px;">{f['name']}</div>
                <div style="color:#64748b; font-size:10px; font-family:'JetBrains Mono';">{f['meta']}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
    st.markdown("---")
    st.markdown("### 🔑 ACCESS CONTROL")
    # Password input is naturally readable due to global CSS overrides
    st.text_input("API Key Configuration", type="password", placeholder="sk-...", help="Secure Enclave")

# Main Content
render_header()

# Input Section
c1, c2 = st.columns([4, 1])
with c1:
    query = st.text_input("MISSION OBJECTIVE", placeholder="输入指令: 分析 陕西建工 2025年三季度财报...", label_visibility="collapsed")
with c2:
    st.markdown("<div style='height: 2px'></div>", unsafe_allow_html=True) # Spacer align
    start = st.button("INITIALIZE", use_container_width=True, type="primary")

if start or query:
    t1, t2, t3 = st.tabs(["📊 INTELLIGENCE", "📉 VISUALIZATION", "💻 TERMINAL"])
    
    with t1:
        # Report Card
        st.markdown("""
        <div class="nexus-card">
            <h2 style="margin-top:0; border-bottom:1px solid rgba(255,255,255,0.1); padding-bottom:10px; margin-bottom:20px;">
                陕西建工 (600248.SH) 深度诊断
            </h2>
            <p style="font-size:16px; color:#cbd5e1;">
                基于2025年最新数据，陕西建工展现出强劲的营收规模（573.88亿元），但盈利能力（净利率1.92%）面临严峻挑战。
                资产负债率维持在 <span style="color:#f87171; font-weight:bold;">88.13%</span> 的高位，财务杠杆风险需重点关注。
            </p>
            <br>
            <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px;">
                <div class="metric-box">
                    <div class="metric-label">总营收</div>
                    <div class="metric-value">¥573.9亿</div>
                    <div style="color:#4ade80; font-size:12px;">▲ 14.6%</div>
                </div>
                <div class="metric-box">
                    <div class="metric-label">净利润</div>
                    <div class="metric-value">¥11.0亿</div>
                    <div style="color:#f87171; font-size:12px;">▼ 6.9%</div>
                </div>
                <div class="metric-box">
                    <div class="metric-label">负债率</div>
                    <div class="metric-value" style="color:#fbbf24;">88.1%</div>
                    <div style="color:#94a3b8; font-size:12px;">Risk High</div>
                </div>
                <div class="metric-box">
                    <div class="metric-label">ROE</div>
                    <div class="metric-value">2.70%</div>
                    <div style="color:#94a3b8; font-size:12px;">-0.3%</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with t2:
        c_v1, c_v2 = st.columns(2)
        with c_v1:
            st.markdown("#### 营收趋势 (Revenue Trend)")
            # Plotly with transparent background
            fig = go.Figure(data=[go.Bar(x=['Q1', 'Q2', 'Q3'], y=[150, 230, 180], marker_color='#38bdf8')])
            fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font={'color': '#fff'})
            st.plotly_chart(fig, use_container_width=True)
        with c_v2:
            st.markdown("#### 成本结构 (Cost Structure)")
            fig2 = go.Figure(data=[go.Pie(labels=['成本', '利润'], values=[90, 10], hole=.6)])
            fig2.update_layout(paper_bgcolor='rgba(0,0,0,0)', font={'color': '#fff'})
            st.plotly_chart(fig2, use_container_width=True)

    with t3:
        logs = [
            "2025-11-20 20:16:13 [INFO] System initialized",
            "2025-11-20 20:16:14 >> Orchestrator: Assigning tasks...",
            "2025-11-20 20:16:15 [INFO] DataAgent: Fetching 600248.SH",
            "2025-11-20 20:16:18 [SUCCESS] AkShare API: 200 OK (102 rows)",
            "2025-11-20 20:16:20 [WARNING] Debt ratio > 80% detected",
            "2025-11-20 20:16:22 >> AnalysisAgent: Computing ROE/ROA...",
            "2025-11-20 20:16:25 [ALERT] Margin anomaly detected in Q3",
            "2025-11-20 20:16:28 [SUCCESS] Report generation complete"
        ]
        render_terminal_logs(logs)

