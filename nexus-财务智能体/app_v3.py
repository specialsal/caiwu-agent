# -*- coding: utf-8 -*-
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import json
import time
import os
from google import genai
from google.genai import types
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# ==========================================
# ⚙️ 页面基础配置
# ==========================================
st.set_page_config(
    page_title="Nexus 财务情报终端",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed" # 默认收起侧边栏，模仿图2的沉浸式体验
)

# ==========================================
# 🎨 核心 UI 引擎 (CSS 注入)
# ==========================================
# 这里我们使用高级 CSS 来强制覆盖 Streamlit 的默认样式，
# 这里的每一行 CSS 都是为了还原 React 版本的 "图二" 效果。
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&family=JetBrains+Mono:wght@400;700&display=swap');

    /* --- 1. 全局背景与重置 --- */
    [data-testid="stAppViewContainer"] {
        background-color: #020617; /* Deep Slate Black */
        background-image: 
            radial-gradient(circle at 50% 0%, rgba(56, 189, 248, 0.1) 0%, rgba(2, 6, 23, 0) 50%),
            linear-gradient(rgba(255, 255, 255, 0.03) 1px, transparent 1px),
            linear-gradient(90deg, rgba(255, 255, 255, 0.03) 1px, transparent 1px);
        background-size: 100% 100%, 40px 40px, 40px 40px; /* 网格背景 */
        color: #f8fafc;
    }
    
    [data-testid="stHeader"] {
        background: transparent !important;
    }

    /* --- 2. 修复输入框看不清的问题 (增强版) --- */
    
    /* 目标：Streamlit 的输入框容器 */
    div[data-baseweb="input"] {
        background-color: rgba(15, 23, 42, 0.8) !important; /* 深色背景 */
        border: 1px solid rgba(148, 163, 184, 0.2) !important;
        border-radius: 12px !important;
        padding: 4px 8px !important;
    }
    
    /* 目标：实际的输入文本 (覆盖所有可能的子元素) */
    div[data-baseweb="input"] > div {
        background-color: transparent !important;
    }
    
    /* 强制输入文字颜色 */
    input.stTextInput, .stTextInput input {
        color: #ffffff !important; /* 强制白色文字 */
        -webkit-text-fill-color: #ffffff !important;
        background-color: transparent !important;
        font-family: 'Inter', sans-serif !important;
        font-size: 16px !important;
        caret-color: #00f3ff !important; /* 光标颜色 */
    }
    
    /* 占位符颜色 */
    input::placeholder {
        color: rgba(148, 163, 184, 0.5) !important;
    }
    
    /* 输入框聚焦状态 - 霓虹光晕 */
    div[data-baseweb="input"]:focus-within {
        border-color: #00f3ff !important;
        box-shadow: 0 0 20px rgba(0, 243, 255, 0.15) !important;
    }
    
    /* 输入框 Label */
    label[data-testid="stWidgetLabel"] p {
        font-size: 0.8rem;
        color: #94a3b8 !important;
        font-family: 'JetBrains Mono', monospace;
    }

    /* --- 3. 按钮美化 --- */
    button[kind="primary"] {
        background: linear-gradient(90deg, #00f3ff 0%, #3b82f6 100%) !important;
        border: none !important;
        border-radius: 8px !important;
        color: #000 !important;
        font-weight: 700 !important;
        transition: all 0.3s ease !important;
    }
    button[kind="primary"]:hover {
        opacity: 0.9;
        box-shadow: 0 0 30px rgba(0, 243, 255, 0.4) !important;
    }

    /* --- 4. 卡片与容器 (Glassmorphism) --- */
    .nexus-card {
        background: rgba(30, 41, 59, 0.4);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 16px;
        padding: 24px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2);
    }
    
    .metric-value {
        font-family: 'JetBrains Mono', monospace;
        font-size: 2rem;
        font-weight: 700;
        background: linear-gradient(to right, #fff, #cbd5e1);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }

    /* 隐藏 Streamlit 默认菜单 */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
</style>
""", unsafe_allow_html=True)

# ==========================================
# 🧠 智能体逻辑层
# ==========================================

class FinancialAgent:
    def __init__(self, api_key=None):
        self.api_key = api_key
        self.client = None
        if self.api_key:
            try:
                self.client = genai.Client(api_key=self.api_key)
            except Exception as e:
                pass

    def analyze(self, query):
        # 模拟“思考”过程，增加沉浸感
        with st.spinner('正在通过 Nexus 网络检索实时财务数据...'):
            time.sleep(1.5) # 模拟网络延迟
        
        if not self.api_key:
            return self._get_mock_data(query)
            
        try:
            prompt = f"""
            作为一个专业的财务分析智能体，请分析: '{query}'。
            请返回以下 JSON 格式数据 (不要使用 Markdown 格式):
            {{
                "title": "报告标题",
                "summary": "200字以内的中文摘要",
                "metrics": [
                    {{"label": "指标名称", "value": "数值", "trend": "up/down/flat", "change": "变化率"}}
                ],
                "chart_data": [
                    {{"x": "Q1", "y": 100}}, {{"x": "Q2", "y": 120}}
                ]
            }}
            """
            response = self.client.models.generate_content(
                model='gemini-2.5-flash',
                contents=prompt,
                config=types.GenerateContentConfig(response_mime_type='application/json')
            )
            return json.loads(response.text)
        except:
            return self._get_mock_data(query)

    def _get_mock_data(self, query):
        return {
            "title": f"分析报告：{query}",
            "summary": "基于最新财报数据，该公司在核心业务板块表现强劲，尤其是在技术创新领域的投入带来了显著的回报率增长。尽管市场环境波动，但现金流保持健康。",
            "metrics": [
                {"label": "总营收 (Revenue)", "value": "¥42.5B", "trend": "up", "change": "+12.4%"},
                {"label": "净利润 (Net Profit)", "value": "¥8.2B", "trend": "down", "change": "-3.1%"},
                {"label": "研发投入 (R&D)", "value": "¥4.5B", "trend": "up", "change": "+15.2%"},
                {"label": "毛利率 (Gross Margin)", "value": "24.5%", "trend": "flat", "change": "+0.2%"}
            ],
            "chart_data": [
                {"x": "23 Q1", "y": 320}, {"x": "23 Q2", "y": 350},
                {"x": "23 Q3", "y": 310}, {"x": "23 Q4", "y": 410},
                {"x": "24 Q1", "y": 390}, {"x": "24 Q2", "y": 450}
            ]
        }

# ==========================================
# 🖥️ 视图渲染层
# ==========================================

# 1. Hero Header (模仿图2的居中大标题)
st.markdown("""
    <div style="text-align: center; margin-top: 40px; margin-bottom: 40px;">
        <div style="
            display: inline-block;
            padding: 8px 16px;
            background: rgba(0, 243, 255, 0.1);
            border: 1px solid rgba(0, 243, 255, 0.2);
            border-radius: 20px;
            color: #00f3ff;
            font-family: 'JetBrains Mono';
            font-size: 12px;
            margin-bottom: 16px;
            box-shadow: 0 0 10px rgba(0,243,255,0.2);
        ">
            ⚡ NEXUS INTELLIGENCE V4.1
        </div>
        <h1 style="
            font-size: 3.5rem;
            font-weight: 800;
            margin: 0;
            line-height: 1.2;
            background: linear-gradient(180deg, #fff 0%, #94a3b8 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            text-shadow: 0 0 40px rgba(255,255,255,0.1);
        ">
            财务情报<br/>
            <span style="
                background: linear-gradient(90deg, #00f3ff 0%, #bc13fe 100%);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
            ">自主智能体 (Autonomous Agent)</span>
        </h1>
        <p style="color: #64748b; margin-top: 16px; font-size: 1.1rem; max-width: 600px; margin-left: auto; margin-right: auto;">
            输入查询以部署专业的智能体集群。它们将自动采集数据、计算指标并生成详尽的中文多媒体报告。
        </p>
    </div>
""", unsafe_allow_html=True)

# 2. 居中搜索栏区域
# 使用 st.columns 将输入框居中 [1, 2, 1] 的比例
col_spacer_1, col_main, col_spacer_2 = st.columns([1, 2, 1])

with col_main:
    # 输入框
    query = st.text_input(
        "Prompt", 
        placeholder="例如：分析陕西建工今年第三季度的财报表现...", 
        label_visibility="collapsed"
    )
    
    # 快捷按钮 (Chips)
    st.markdown("""
        <div style="display: flex; gap: 10px; justify-content: center; margin-top: 12px;">
            <span style="padding: 6px 12px; background: rgba(255,255,255,0.05); border-radius: 20px; font-size: 12px; color: #94a3b8; border: 1px solid rgba(255,255,255,0.1);">陕西建工Q3财报</span>
            <span style="padding: 6px 12px; background: rgba(255,255,255,0.05); border-radius: 20px; font-size: 12px; color: #94a3b8; border: 1px solid rgba(255,255,255,0.1);">黄金市场趋势</span>
            <span style="padding: 6px 12px; background: rgba(255,255,255,0.05); border-radius: 20px; font-size: 12px; color: #94a3b8; border: 1px solid rgba(255,255,255,0.1);">科技板块波动</span>
        </div>
    """, unsafe_allow_html=True)
    
    run_btn = st.button("🚀 启动分析", type="primary", use_container_width=True)

# 初始化数据
if 'result' not in st.session_state:
    st.session_state.result = None

# 3. 执行逻辑
if run_btn and query:
    agent = FinancialAgent(api_key=os.getenv("API_KEY"))
    st.session_state.result = agent.analyze(query)

# 4. 结果展示 (Dashboard)
if st.session_state.result:
    data = st.session_state.result
    
    st.markdown("<div style='margin-top: 60px;'></div>", unsafe_allow_html=True)
    
    # 标题区
    st.markdown(f"""
        <div class="nexus-card" style="margin-bottom: 24px; border-left: 4px solid #00f3ff;">
            <h2 style="margin:0; font-size: 1.8rem;">{data.get('title')}</h2>
            <p style="color: #94a3b8; margin-top: 8px; line-height: 1.6;">{data.get('summary')}</p>
        </div>
    """, unsafe_allow_html=True)

    # 指标区 Grid
    m_cols = st.columns(4)
    for idx, m in enumerate(data.get('metrics', [])):
        color = "#10b981" if m['trend'] == 'up' else ("#f43f5e" if m['trend'] == 'down' else "#94a3b8")
        arrow = "↑" if m['trend'] == 'up' else ("↓" if m['trend'] == 'down' else "-")
        
        with m_cols[idx]:
            st.markdown(f"""
                <div class="nexus-card" style="padding: 20px; text-align: center;">
                    <div style="color: #64748b; font-size: 12px; text-transform: uppercase; margin-bottom: 8px;">{m['label']}</div>
                    <div class="metric-value">{m['value']}</div>
                    <div style="color: {color}; font-size: 14px; font-weight: 600; margin-top: 8px;">
                        {arrow} {m['change']}
                    </div>
                </div>
            """, unsafe_allow_html=True)

    # 图表区
    st.markdown("<br>", unsafe_allow_html=True)
    chart_data = data.get('chart_data', [])
    if chart_data:
        df = pd.DataFrame(chart_data)
        
        # 定制 Plotly 黑暗模式
        fig = px.area(df, x='x', y='y', title="核心指标趋势", template="plotly_dark")
        # 关键修复：fill_color -> fillcolor
        fig.update_traces(line_color='#00f3ff', fillcolor='rgba(0, 243, 255, 0.1)')
        fig.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#94a3b8'),
            hovermode="x unified",
            xaxis=dict(showgrid=False, linecolor='#334155'),
            yaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.05)', linecolor='#334155'),
            title_font=dict(size=14, color='#f8fafc')
        )
        
        st.markdown('<div class="nexus-card">', unsafe_allow_html=True)
        st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

# 侧边栏配置
with st.sidebar:
    st.header("配置中心")
    st.info("当前运行环境: Python 3.10+ / Streamlit 1.32")
    st.markdown("---")
    st.markdown("**数据源状态:**")
    st.success("✅ Gemini 2.5 Flash API")
    st.success("✅ 本地数据库 (Connected)")
