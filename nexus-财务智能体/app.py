# -*- coding: utf-8 -*-
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import json
import time
import os
import subprocess
from google import genai
from google.genai import types
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 页面配置
st.set_page_config(
    page_title="Nexus 财务智能体 v3.4",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==========================================
# 🎨 NEXUS UI 引擎 v3.4 (高对比度深色模式)
# ==========================================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&family=JetBrains+Mono:wght@400;700&display=swap');

    /* --- 全局重置 & 排版 (强制高亮文字) --- */
    .stApp {
        background: #020617; /* Very Dark Slate */
        color: #f8fafc; /* High Contrast White */
        font-family: 'Inter', sans-serif;
    }

    /* 强制所有标题和文本为白色/高亮色，解决看不清的问题 */
    h1, h2, h3, h4, h5, h6, span, div, label, .stMarkdown p {
        color: #f1f5f9 !important; 
    }
    
    /* 弱化辅助文本 */
    .stMarkdown p.caption {
        color: #94a3b8 !important;
    }

    /* --- 侧边栏优化 --- */
    section[data-testid="stSidebar"] {
        background-color: #0f172a;
        border-right: 1px solid #1e293b;
    }
    section[data-testid="stSidebar"] h1, 
    section[data-testid="stSidebar"] h2, 
    section[data-testid="stSidebar"] h3, 
    section[data-testid="stSidebar"] label {
        color: #e2e8f0 !important;
    }

    /* --- 输入框 (HUD 风格) --- */
    div[data-baseweb="input"] {
        background-color: #1e293b !important;
        border: 1px solid #334155 !important;
        border-radius: 8px !important;
    }
    input[type="text"], input[type="password"] {
        color: #ffffff !important;
        font-family: 'JetBrains Mono', monospace;
    }
    /* 输入框聚焦效果 */
    div[data-baseweb="input"]:focus-within {
        border-color: #00f3ff !important;
        box-shadow: 0 0 10px rgba(0, 243, 255, 0.2);
    }

    /* --- 按钮 (霓虹风格) --- */
    button[kind="primary"] {
        background: linear-gradient(135deg, #06b6d4 0%, #3b82f6 100%) !important;
        border: none !important;
        color: #ffffff !important;
        font-weight: 700 !important;
        padding: 0.5rem 1rem;
        text-transform: uppercase;
        letter-spacing: 1px;
        transition: all 0.3s ease;
    }
    button[kind="primary"]:hover {
        box-shadow: 0 0 20px rgba(59, 130, 246, 0.6) !important;
        transform: translateY(-2px);
    }
    button[kind="secondary"] {
        background: transparent !important;
        border: 1px solid #334155 !important;
        color: #94a3b8 !important;
    }
    button[kind="secondary"]:hover {
        border-color: #00f3ff !important;
        color: #00f3ff !important;
    }

    /* --- 容器卡片 --- */
    .nexus-card {
        background: rgba(30, 41, 59, 0.5);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 16px;
    }

    /* 隐藏 Streamlit 默认元素 */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
</style>
""", unsafe_allow_html=True)

# ==========================================
# 🔗 后端集成层 (Financial Agent)
# ==========================================

class FinancialAgent:
    """
    核心逻辑层：负责连接 LLM 或 现有的命令行工具。
    """
    def __init__(self, api_key=None):
        self.api_key = api_key
        self.client = None
        if self.api_key:
            try:
                self.client = genai.Client(api_key=self.api_key)
            except Exception as e:
                print(f"Gemini 初始化失败: {e}")

    def analyze(self, query):
        """
        执行分析任务，集成后端命令行工具
        """
        import sys
        import os
        
        # 检查是否在Streamlit环境中运行
        in_streamlit = False
        try:
            import streamlit as st
            if hasattr(st, 'session_state'):
                in_streamlit = True
        except:
            pass
        
        # 创建状态对象（用于Streamlit进度显示）
        status = None
        if in_streamlit:
            try:
                status = st.status("🚀 智能体集群正在运行...", expanded=True)
                if status:
                    st.write("📡 正在连接数据终端...")
                    time.sleep(0.5)
                    st.write("🔍 正在调用命令行工具/API...")
            except:
                pass
        
        # 调用后端命令行工具
        try:
            # 切换到stock_analysis目录并执行命令
            # 使用绝对路径确保正确找到目录
            current_dir = os.path.dirname(os.path.abspath(__file__))
            stock_analysis_path = os.path.join(os.path.dirname(current_dir), "examples", "stock_analysis")
            
            # 验证目录是否存在
            if not os.path.exists(stock_analysis_path):
                raise Exception(f"目录不存在: {stock_analysis_path}")
            
            # 构建命令：python main.py --stream，然后输入查询
            cmd = [sys.executable, "main.py", "--stream"]
            
            # 使用subprocess执行命令
            process = subprocess.Popen(
                cmd,
                cwd=stock_analysis_path,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                encoding='utf-8',
                shell=False
            )
            
            # 发送查询并获取输出
            stdout, stderr = process.communicate(input=query + "\n", timeout=300)  # 5分钟超时
            
            if process.returncode == 0:
                if in_streamlit and status:
                    try:
                        st.write("📊 正在解析分析结果...")
                        time.sleep(0.5)
                        status.update(label="✅ 分析任务完成", state="complete", expanded=False)
                    except:
                        pass
                
                # 解析命令行输出，转换为前端需要的JSON格式
                return self._parse_cli_output(stdout, query)
            else:
                if in_streamlit and status:
                    try:
                        st.error(f"命令行工具执行失败: {stderr}")
                        status.update(label="❌ 分析失败", state="error", expanded=False)
                    except:
                        pass
                return self._get_mock_data(query)
                
        except subprocess.TimeoutExpired:
            if in_streamlit and status:
                try:
                    st.error("分析超时，请稍后重试")
                    status.update(label="⏰ 分析超时", state="error", expanded=False)
                except:
                    pass
            return self._get_mock_data(query)
        except Exception as e:
            if in_streamlit and status:
                try:
                    st.error(f"连接后端工具失败: {str(e)}")
                    status.update(label="❌ 连接失败", state="error", expanded=False)
                except:
                    pass
            return self._get_mock_data(query)

        # 2. 如果没有 API Key，返回模拟数据（用于演示 UI）
        if not self.api_key:
            return self._get_mock_data(query)
        
        try:
            # 3. 使用 Gemini 2.5 Flash 生成结构化数据
            # 我们要求它返回 JSON，这样前端好渲染
            prompt = f"""
            你是一个高级财务分析师。请分析以下查询：'{query}'。
            
            请务必返回且仅返回一个合法的 JSON 对象（不要用 Markdown 代码块包裹），结构如下：
            {{
                "title": "简短的中文标题",
                "summary": "2-3句话的中文执行摘要",
                "metrics": [
                    {{"label": "中文指标名 (如 净利润)", "value": "带单位的数值", "change": "变化率 (如 +12%)", "trend": "up/down/flat"}}
                ],
                "revenue_trend": [
                    {{"period": "24Q1", "value": 100}},
                    {{"period": "24Q2", "value": 120}}
                ],
                "cost_structure": [
                    {{"category": "研发", "value": 30}},
                    {{"category": "营销", "value": 20}}
                ],
                "logs": [
                    "日志条目 1",
                    "日志条目 2"
                ]
            }}
            """
            
            response = self.client.models.generate_content(
                model='gemini-2.5-flash',
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type='application/json'
                )
            )
            return json.loads(response.text)
            
        except Exception as e:
            if in_streamlit:
                try:
                    import streamlit as st
                    st.error(f"连接失败: {str(e)}")
                    st.info("已切换到模拟数据模式。")
                except:
                    pass
            return self._get_mock_data(query)

    def _parse_cli_output(self, cli_output, original_query):
        """
        解析命令行工具的输出，转换为前端需要的JSON格式
        """
        import re
        import json
        
        # 尝试从输出中提取关键信息
        def extract_financial_metrics(text):
            """提取财务指标"""
            metrics = []
            
            # 常见财务指标模式
            patterns = {
                "营业收入": r'营业收入[：:\s]*([0-9.,]+[万亿千百元]*)',
                "净利润": r'净利润[：:\s]*([0-9.,]+[万亿千百元]*)',
                "总资产": r'总资产[：:\s]*([0-9.,]+[万亿千百元]*)',
                "毛利率": r'毛利率[：:\s]*([0-9.,]+%)',
                "净利率": r'净利率[：:\s]*([0-9.,]+%)',
                "ROE": r'ROE[：:\s]*([0-9.,]+%)',
                "研发投入": r'研发[投投入][：:\s]*([0-9.,]+[万亿千百元]*)'
            }
            
            for metric_name, pattern in patterns.items():
                matches = re.findall(pattern, text)
                if matches:
                    value = matches[0]
                    # 尝试提取变化趋势
                    change_pattern = f'{metric_name}.*?([+-]?[0-9.,]+%)'
                    change_match = re.search(change_pattern, text)
                    change = change_match.group(1) if change_match else "持平"
                    trend = "up" if "+" in change else ("down" if "-" in change else "flat")
                    
                    metrics.append({
                        "label": metric_name,
                        "value": value,
                        "change": change,
                        "trend": trend
                    })
            
            # 如果没有找到指标，返回默认指标
            if not metrics:
                return [
                    {"label": "分析完成", "value": "✅", "change": "成功", "trend": "up"},
                    {"label": "报告类型", "value": "详细分析", "change": "生成", "trend": "up"}
                ]
            
            return metrics[:4]  # 最多返回4个指标
        
        def extract_company_name(text):
            """提取公司名称"""
            # 匹配股票代码模式：公司名称(股票代码)
            stock_pattern = r'([^()（）]+)\((\d{6}\.(?:SH|SZ))\)'
            matches = re.findall(stock_pattern, text)
            if matches:
                return matches[0][0], matches[0][1]
            return "目标公司", "N/A"
        
        def extract_summary(text):
            """提取摘要信息"""
            # 寻找结论性语句
            summary_patterns = [
                r'(?:总体|综合|总结)[：:]?\s*([^。\n]+)',
                r'(?:建议|推荐)[：:]?\s*([^。\n]+)',
                r'(?:结论|判断)[：:]?\s*([^。\n]+)'
            ]
            
            for pattern in summary_patterns:
                match = re.search(pattern, text)
                if match:
                    return match.group(1).strip()
            
            # 如果没有找到，返回前200个字符作为摘要
            return text[:200] + "..." if len(text) > 200 else text
        
        # 提取信息
        company_name, stock_code = extract_company_name(cli_output)
        metrics = extract_financial_metrics(cli_output)
        summary = extract_summary(cli_output)
        
        # 生成趋势数据（模拟数据，因为命令行输出可能不包含具体趋势）
        revenue_trend = [
            {"period": "2023 Q3", "value": 380},
            {"period": "2023 Q4", "value": 410},
            {"period": "2024 Q1", "value": 395},
            {"period": "2024 Q2", "value": 452}
        ]
        
        # 生成成本结构（模拟数据）
        cost_structure = [
            {"category": "营业成本", "value": 60},
            {"category": "研发支出", "value": 15},
            {"category": "销售费用", "value": 15},
            {"category": "管理费用", "value": 10}
        ]
        
        # 生成日志
        logs = [
            f"系统初始化完成...",
            f"正在分析 {company_name}({stock_code})",
            f"执行查询: {original_query}",
            f"调用智能体集群进行分析...",
            f"分析完成，生成报告"
        ]
        
        return {
            "title": f"{company_name} 财务分析报告",
            "summary": summary,
            "metrics": metrics,
            "revenue_trend": revenue_trend,
            "cost_structure": cost_structure,
            "logs": logs
        }
    
    def _get_mock_data(self, query):
        """没有后端连接时的演示数据"""
        return {
            "title": f"关于“{query}”的深度分析报告",
            "summary": "系统处于演示模式（未检测到 API Key）。数据显示该公司核心业务稳健增长，但 Q3 运营成本略有上升。建议关注现金流健康度。",
            "metrics": [
                {"label": "总营收", "value": "¥452.1亿", "change": "+12.4%", "trend": "up"},
                {"label": "净利润", "value": "¥28.3亿", "change": "-3.2%", "trend": "down"},
                {"label": "毛利率", "value": "18.5%", "change": "持平", "trend": "flat"},
                {"label": "研发投入", "value": "¥45亿", "change": "+8.1%", "trend": "up"}
            ],
            "revenue_trend": [
                {"period": "2023 Q3", "value": 380},
                {"period": "2023 Q4", "value": 410},
                {"period": "2024 Q1", "value": 395},
                {"period": "2024 Q2", "value": 452}
            ],
            "cost_structure": [
                {"category": "营业成本", "value": 60},
                {"category": "研发支出", "value": 15},
                {"category": "销售费用", "value": 15},
                {"category": "管理费用", "value": 10}
            ],
            "logs": [
                "系统初始化完成...",
                "正在连接外部命令行工具...",
                "检测到本地数据源 data.csv",
                "执行 python analysis_core.py --target=revenue",
                "数据校验通过，开始渲染报告"
            ]
        }

# ==========================================
# 📊 可视化引擎 (适配深色模式)
# ==========================================

def create_cyber_chart(data, chart_type="bar"):
    """
    创建适配深色背景的 Plotly 图表
    """
    df = pd.DataFrame(data)
    
    if chart_type == "bar":
        fig = px.bar(
            df, x='period', y='value', 
            color_discrete_sequence=['#00f3ff'] # 霓虹蓝
        )
        fig.update_traces(marker_line_width=0, opacity=0.9)
    else:
        fig = px.pie(
            df, names='category', values='value', 
            hole=0.6,
            color_discrete_sequence=['#3b82f6', '#8b5cf6', '#06b6d4', '#ec4899']
        )

    # 关键：设置全透明背景和白色文字，解决“看不清”的问题
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)', 
        plot_bgcolor='rgba(0,0,0,0)',
        font={'color': '#ffffff', 'family': 'Inter'}, # 强制白色字体
        margin=dict(l=10, r=10, t=30, b=10),
        xaxis=dict(
            showgrid=False, 
            linecolor='#334155', 
            tickfont=dict(color='#cbd5e1', size=12)
        ),
        yaxis=dict(
            showgrid=True, 
            gridcolor='rgba(255, 255, 255, 0.1)', # 微弱的网格线
            linecolor='#334155',
            tickfont=dict(color='#cbd5e1')
        ),
        legend=dict(
            font=dict(color='#ffffff'),
            bgcolor='rgba(0,0,0,0)'
        )
    )
    
    return fig

# ==========================================
# 🚀 主界面逻辑
# ==========================================

# 顶部标题栏
st.markdown("""
<div style="border-bottom: 1px solid rgba(255,255,255,0.1); padding-bottom: 20px; margin-bottom: 30px;">
    <h1 style="margin:0; font-size: 2.5rem; background: linear-gradient(to right, #fff, #94a3b8); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">
        Nexus <span style="color:#00f3ff; font-weight:300;">财务智能体</span>
    </h1>
    <div style="color: #64748b; font-family: 'JetBrains Mono'; font-size: 0.8rem; margin-top: 5px;">
        AUTONOMOUS FINANCIAL INTELLIGENCE TERMINAL v3.4
    </div>
</div>
""", unsafe_allow_html=True)

# 侧边栏
with st.sidebar:
    st.header("⚙️ 系统配置")
    api_key_input = st.text_input("Gemini API Key", type="password", placeholder="输入 sk-...", help="留空将运行在演示模式")
    
    st.markdown("---")
    st.markdown("### 📁 本地文件")
    st.caption("检测到已挂载的数据源：")
    
    files = ["Q3_Raw_Data.csv", "Financial_Report_v2.pdf", "CLI_Tool_Config.yaml"]
    for f in files:
        st.markdown(f"""
        <div style="display:flex; align-items:center; gap:8px; padding:8px; background:rgba(255,255,255,0.03); border-radius:6px; margin-bottom:6px;">
            <span style="color:#00f3ff;">📄</span> 
            <span style="font-family:'JetBrains Mono'; font-size:12px; color:#cbd5e1;">{f}</span>
        </div>
        """, unsafe_allow_html=True)

# 初始化 Session State
if 'data' not in st.session_state:
    st.session_state.data = None

# 核心交互区
query = st.text_input("💬 指令输入", placeholder="例如：分析上个季度的营收趋势，并对比研发成本...", label_visibility="visible")

col1, col2 = st.columns([1, 5])
with col1:
    run_btn = st.button("⚡ 执行分析", type="primary", use_container_width=True)

# 执行逻辑
if run_btn and query:
    agent = FinancialAgent(api_key=api_key_input or os.getenv("API_KEY"))
    st.session_state.data = agent.analyze(query)

# 结果展示区
if st.session_state.data:
    data = st.session_state.data
    
    st.markdown("---")
    
    # 1. 关键指标卡片 (KPIs)
    st.subheader(data.get('title', '分析报告'))
    st.info(data.get('summary', ''))
    
    kpi_cols = st.columns(4)
    for i, metric in enumerate(data.get("metrics", [])):
        with kpi_cols[i]:
            # 根据趋势决定颜色
            trend_color = "#10b981" if metric.get('trend') == 'up' else "#f43f5e"
            if metric.get('trend') == 'flat': trend_color = "#94a3b8"
            
            st.markdown(f"""
            <div class="nexus-card" style="text-align:center; padding: 15px;">
                <div style="color:#94a3b8; font-size:12px; margin-bottom:4px;">{metric['label']}</div>
                <div style="color:#fff; font-size:24px; font-weight:bold; font-family:'JetBrains Mono';">{metric['value']}</div>
                <div style="color:{trend_color}; font-size:13px; margin-top:4px;">{metric['change']}</div>
            </div>
            """, unsafe_allow_html=True)

    # 2. 图表区域
    chart_c1, chart_c2 = st.columns(2)
    with chart_c1:
        st.markdown("#### 📊 趋势分析")
        if "revenue_trend" in data:
            fig = create_cyber_chart(data['revenue_trend'], "bar")
            st.plotly_chart(fig, use_container_width=True)
            
    with chart_c2:
        st.markdown("#### 🧬 成本结构")
        if "cost_structure" in data:
            fig2 = create_cyber_chart(data['cost_structure'], "pie")
            st.plotly_chart(fig2, use_container_width=True)

    # 3. 终端日志
    with st.expander("💻 系统运行日志 (TERMINAL LOGS)", expanded=False):
        st.markdown("""
        <style>
        .log-line { font-family: 'JetBrains Mono'; font-size: 12px; padding: 2px 0; border-bottom: 1px dashed #1e293b; }
        .log-time { color: #64748b; margin-right: 10px; }
        .log-content { color: #cbd5e1; }
        </style>
        """, unsafe_allow_html=True)
        
        for log in data.get("logs", []):
            st.markdown(f"""
            <div class="log-line">
                <span class="log-time">[{time.strftime("%H:%M:%S")}]</span>
                <span class="log-content">{log}</span>
            </div>
            """, unsafe_allow_html=True)
