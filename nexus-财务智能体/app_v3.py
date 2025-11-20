# -*- coding: utf-8 -*-
import streamlit as st
import os
import time
import json
import pandas as pd
import plotly.graph_objects as go
from dotenv import load_dotenv
from google import genai
from google.genai import types

# Load environment variables
load_dotenv()

# Page Config
st.set_page_config(
    page_title="Nexus 财务智能体 v3.0",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==========================================
# 🎨 ULTRA-FIDELITY CSS STYLING (V3.0)
# ==========================================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;800&family=JetBrains+Mono:wght@400;700&display=swap');

    /* ----------------------------------------
       GLOBAL THEME OVERRIDES 
       ---------------------------------------- */
    .stApp {
        background-color: #030712 !important; /* slate-950 */
        color: #e2e8f0 !important;
        font-family: 'Inter', sans-serif;
    }
    
    /* Text Visibility Fixes */
    p, h1, h2, h3, h4, h5, h6, span, div, li, label, .stMarkdown {
        color: #e2e8f0 !important;
    }
    h1, h2, h3, h4 {
        font-weight: 800;
        letter-spacing: -0.025em;
        color: white !important;
    }
    
    /* Hide Default Elements */
    #MainMenu, footer, header, div[data-testid="stToolbar"] {visibility: hidden;}
    div[data-testid="stDecoration"] {display: none;}
    
    /* ----------------------------------------
       INPUT FIELDS (Deep Dark Mode)
       ---------------------------------------- */
    div[data-baseweb="input"] {
        background-color: #0f172a !important;
        border: 1px solid rgba(255, 255, 255, 0.15) !important;
        border-radius: 8px !important;
    }
    div[data-baseweb="input"] > div { background-color: transparent !important; }
    input[type="text"], input[type="password"] {
        color: white !important;
        caret-color: #00f3ff !important;
    }
    input::placeholder { color: rgba(255, 255, 255, 0.4) !important; }

    /* ----------------------------------------
       TABS & EXPANDERS (New in v3.0)
       ---------------------------------------- */
    .stTabs [data-baseweb="tab-list"] {
        gap: 2px;
        background-color: rgba(255,255,255,0.05);
        border-radius: 8px;
        padding: 4px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 40px;
        border-radius: 6px;
        color: #94a3b8 !important;
        border: none !important;
        font-weight: 600;
    }
    .stTabs [aria-selected="true"] {
        background-color: #1e293b !important;
        color: #00f3ff !important;
        box-shadow: 0 2px 4px rgba(0,0,0,0.2);
    }
    
    /* Expander Styling */
    .streamlit-expanderHeader {
        background-color: rgba(255,255,255,0.02) !important;
        border: 1px solid rgba(255,255,255,0.1) !important;
        color: #e2e8f0 !important;
    }
    div[data-testid="stExpanderDetails"] {
        border: 1px solid rgba(255,255,255,0.1);
        border-top: none;
        background-color: rgba(0,0,0,0.2) !important;
    }

    /* ----------------------------------------
       CUSTOM COMPONENTS
       ---------------------------------------- */
    .nexus-card {
        background: rgba(255, 255, 255, 0.03);
        backdrop-filter: blur(12px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 16px;
        padding: 24px;
        margin-bottom: 20px;
    }
    
    /* Terminal Log Style */
    .terminal-log {
        font-family: 'JetBrains Mono', monospace;
        font-size: 12px;
        color: #33ff00 !important;
        background-color: #000000 !important;
        padding: 15px;
        border-radius: 8px;
        border: 1px solid #333;
        height: 300px;
        overflow-y: auto;
        line-height: 1.5;
        box-shadow: inset 0 0 20px rgba(0,0,0,0.8);
    }
    
    /* Agent Step Active/Inactive */
    .agent-step {
        display: flex;
        align-items: center;
        gap: 12px;
        padding: 10px;
        border-radius: 6px;
        margin-bottom: 6px;
        border-left: 2px solid transparent;
        background: rgba(255,255,255,0.02);
    }
    .agent-step.active {
        background: rgba(0, 243, 255, 0.05);
        border-left: 2px solid #00f3ff;
    }
    .agent-step.completed {
        opacity: 0.5;
    }

    /* File Artifact */
    .file-artifact {
        display: flex;
        align-items: center;
        gap: 10px;
        padding: 8px;
        font-size: 12px;
        font-family: 'JetBrains Mono', monospace;
        border-bottom: 1px solid rgba(255,255,255,0.05);
        color: #94a3b8 !important;
    }
    .file-artifact:hover {
        background: rgba(255,255,255,0.05);
        color: white !important;
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 🧠 WORKFLOW ENGINE
# ==========================================

def render_workflow(current_stage_index):
    """Visualizes the complex multi-agent workflow from the logs."""
    stages = [
        {"name": "PlannerAgent", "desc": "任务拆解与路径规划", "status": "done" if current_stage_index > 0 else "active" if current_stage_index == 0 else "pending"},
        {"name": "DataAgent", "desc": "AkShare 财报数据获取", "status": "done" if current_stage_index > 1 else "active" if current_stage_index == 1 else "pending"},
        {"name": "DataAnalysisAgent", "desc": "比率计算与趋势评估", "status": "done" if current_stage_index > 2 else "active" if current_stage_index == 2 else "pending"},
        {"name": "ChartGeneratorAgent", "desc": "生成可视化图表产物", "status": "done" if current_stage_index > 3 else "active" if current_stage_index == 3 else "pending"},
        {"name": "FinancialAnalysisAgent", "desc": "深度财务解读与风险识别", "status": "done" if current_stage_index > 4 else "active" if current_stage_index == 4 else "pending"},
        {"name": "ReportAgent", "desc": "编译 HTML/PDF 最终报告", "status": "done" if current_stage_index > 5 else "active" if current_stage_index == 5 else "pending"},
    ]
    
    st.markdown("##### ⚡ 智能体协作状态 (Agent Orchestration)")
    for stage in stages:
        icon = "✅" if stage['status'] == 'done' else "🔄" if stage['status'] == 'active' else "⏳"
        color = "#00f3ff" if stage['status'] == 'active' else "#0aff68" if stage['status'] == 'done' else "#64748b"
        bg = "rgba(0,243,255,0.1)" if stage['status'] == 'active' else "transparent"
        
        st.markdown(f"""
        <div class="agent-step {stage['status']}" style="background-color: {bg};">
            <div style="font-size: 18px;">{icon}</div>
            <div style="flex: 1;">
                <div style="color: {color}; font-weight: bold; font-size: 13px;">{stage['name']}</div>
                <div style="color: #94a3b8; font-size: 11px;">{stage['desc']}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

def get_simulated_logs():
    """Returns specific log lines based on the user's provided PDF."""
    return [
        "2025-11-20 20:16:13 - orchestra - INFO - [PlannerAgent] planning_start - started",
        ">> 新智能体: planner_agent 已上线",
        "分析目标: 陕西建工(600248.SH) 2025年三季度财报表现",
        "2025-11-20 20:16:27 - orchestra - INFO - Plan creation completed (13266ms)",
        ">> 新智能体: data_agent 已上线",
        "[工具调用] get_financial_reports({'stock_code': '600248', 'type': 'financial'})",
        "WARNING: 2025三季度财报数据不完整，自动回退至最新可用数据",
        "[DataAgent] 成功获取 102 行资产负债表数据",
        ">> 新智能体: data_analysis_agent 已上线",
        "[工具调用] calculate_ratios({'net_profit_margin': 1.92, 'roe': 2.70})",
        "检测到异常: 净利润率 (1.92%) 低于行业平均水平",
        ">> 新智能体: chart_generator_agent 已上线",
        "生成图表: ./run_workdir/revenue_trend.png ... 成功",
        "生成图表: ./run_workdir/debt_structure.png ... 成功",
        ">> 新智能体: report_agent 已上线",
        "正在编译 Markdown 报告...",
        "正在生成 PDF: stock_analysis_report.pdf (156KB)",
        "任务完成: 耗时 45.2s"
    ]

def get_gemini_data(api_key, query):
    """Real API Call (Placeholder for structure)"""
    # In a real scenario, this would call the backend agents
    # For this demo, we return the pre-canned structure matching the report
    time.sleep(2) # Simulate network
    return {
        "title": f"陕西建工 (600248.SH) 深度财务诊断报告",
        "summary": "基于现有数据，陕西建工表现出高风险特征。营收规模庞大（573.88亿元）但盈利能力偏弱（净利率1.92%）。资产负债率高达 88.13%，财务杠杆处于高位。建议投资者保持谨慎，等待完整三季度财报发布。",
        "metrics": [
            {"label": "总营收", "value": "¥573.9亿", "delta": "+146%", "trend": "up"},
            {"label": "净利润", "value": "¥11.0亿", "delta": "-69%", "trend": "down"},
            {"label": "资产负债率", "value": "88.1%", "delta": "高风险", "trend": "down"},
            {"label": "ROE", "value": "2.70%", "delta": "偏低", "trend": "neutral"}
        ]
    }

# ==========================================
# 📱 MAIN APP LAYOUT
# ==========================================

# Sidebar: File Artifacts (Simulating the output folder)
with st.sidebar:
    st.markdown("### 📂 项目产物 (Artifacts)")
    st.caption("生成的文件 (Run Workdir)")
    
    files = [
        {"icon": "📄", "name": "analysis_report.pdf", "size": "156 KB"},
        {"icon": "📊", "name": "revenue_trend.png", "size": "90 KB"},
        {"icon": "📊", "name": "debt_structure.png", "size": "85 KB"},
        {"icon": "🌐", "name": "report_preview.html", "size": "12 KB"},
        {"icon": "📝", "name": "raw_logs.txt", "size": "4 KB"},
    ]
    
    for f in files:
        st.markdown(f"""
        <div class="file-artifact">
            <span>{f['icon']}</span>
            <div style="flex:1;">{f['name']}</div>
            <div style="opacity:0.5;">{f['size']}</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    st.markdown("### ⚙️ 系统配置")
    api_key = st.text_input("API Key", type="password")

# Main Header
st.markdown("""
    <div class="nexus-card" style="border-color: #00f3ff33; background: radial-gradient(circle at top right, rgba(0, 243, 255, 0.05), transparent); padding: 30px;">
        <div style="display:flex; justify-content:space-between; align-items:center;">
            <div>
                <h1 style="margin-bottom: 8px; font-size: 2.5rem;">Nexus <span style="color: #00f3ff; text-shadow: 0 0 20px rgba(0,243,255,0.5);">财务智能体 v3.0</span></h1>
                <p style="color: #94a3b8; margin-bottom: 0; font-family: 'JetBrains Mono';">Autonomous Financial Intelligence Terminal // 6-Agent Swarm</p>
            </div>
            <div style="text-align:right;">
                <div style="color:#0aff68; font-weight:bold;">● SYSTEM ONLINE</div>
                <div style="color:#64748b; font-size:12px;">Latency: 24ms</div>
            </div>
        </div>
    </div>
""", unsafe_allow_html=True)

# Input Area
c1, c2 = st.columns([4, 1])
with c1:
    query = st.text_input("", placeholder="指令: 分析 陕西建工 2025年三季度财报...", label_visibility="collapsed")
with c2:
    start_btn = st.button("启动智能体集群", use_container_width=True)

# Logic
if start_btn or query:
    # Use Tabs to organize the complexity
    tab_main, tab_viz, tab_logs = st.tabs(["📊 智能分析报告", "📉 趋势可视化", "💻 终端日志"])
    
    with tab_main:
        # Layout: Left for Workflow, Right for Content
        col_flow, col_content = st.columns([1, 3])
        
        with col_flow:
            flow_placeholder = st.empty()
            
        with col_content:
            report_placeholder = st.empty()
            
            # 1. Simulation Loop
            logs_text = ""
            simulated_logs = get_simulated_logs()
            
            # Iterate through stages
            for i in range(7):
                # Update Workflow Sidebar
                with col_flow:
                    render_workflow(i)
                
                # Simulate Processing Time & Logs
                if i < 6:
                    with report_placeholder.container():
                        st.info(f"正在执行步骤 {i+1}/6: {['任务规划', '数据获取', '数据清洗', '图表生成', '深度分析', '报告编译'][i]}...")
                        # Stream logs to the Logs Tab (we handle this logically, but UI updates sequentially)
                        time.sleep(0.8) 
            
            # 2. Final Result Display
            data = get_gemini_data(api_key, query)
            
            report_placeholder.empty()
            with report_placeholder.container():
                # Success Banner
                st.markdown("""
                <div style="background: rgba(10, 255, 104, 0.1); border: 1px solid #0aff68; padding: 15px; border-radius: 8px; margin-bottom: 20px; display: flex; align-items: center; gap: 10px;">
                    <span style="font-size: 20px;">✅</span>
                    <span style="color: #0aff68; font-weight: bold;">分析完成：已生成深度诊断报告</span>
                </div>
                """, unsafe_allow_html=True)
                
                st.markdown(f"## {data['title']}")
                st.markdown(f"> {data['summary']}")
                
                # Metrics
                cols = st.columns(4)
                for idx, m in enumerate(data['metrics']):
                    with cols[idx]:
                        st.metric(m['label'], m['value'], m['delta'], delta_color="inverse" if m['trend'] == 'down' else "normal")

                st.markdown("### ⚠️ 关键风险提示")
                st.warning("数据时效性：当前分析基于可获得的最新数据（2025年数据可能不完整）。建议在10月底后获取完整三季度报告。")
                
                st.markdown("### 💡 投资建议")
                st.info("谨慎偏中性：鉴于负债率过高（88.13%）且盈利能力偏弱，建议保守型投资者观望。")

    with tab_viz:
        st.markdown("### 关键指标可视化 (Generated by ChartGeneratorAgent)")
        v_c1, v_c2 = st.columns(2)
        with v_c1:
            # Mock Chart 1
            fig1 = go.Figure(data=[
                go.Bar(name='2024', x=['Q1', 'Q2', 'Q3'], y=[1511, 1018, 980], marker_color='#3b82f6'),
                go.Bar(name='2025', x=['Q1', 'Q2', 'Q3'], y=[573, 232, 0], marker_color='#bc13fe')
            ])
            fig1.update_layout(title="营收对比 (单位: 亿元)", template="plotly_dark", bg_color="rgba(0,0,0,0)")
            st.plotly_chart(fig1, use_container_width=True)
            
        with v_c2:
             # Mock Chart 2
            fig2 = go.Figure(data=[go.Pie(labels=['总负债', '净资产'], values=[88.13, 11.87], hole=.3)])
            fig2.update_layout(title="资产负债结构", template="plotly_dark", bg_color="rgba(0,0,0,0)")
            st.plotly_chart(fig2, use_container_width=True)

    with tab_logs:
        st.markdown("### 📟 实时终端日志 (Orchestra Logs)")
        log_content = "\n".join(get_simulated_logs())
        # Fix: Perform the replacement outside the f-string to avoid backslash syntax error
        formatted_logs = log_content.replace("\n", "<br>")
        st.markdown(f"""
        <div class="terminal-log">
            {formatted_logs}
            <br><span class="blink">_</span>
        </div>
        """, unsafe_allow_html=True)
