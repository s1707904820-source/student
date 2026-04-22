"""
可视化看板 (Streamlit)
功能：数据展示看板，展示分析成果
优化：添加筛选功能和动画效果
"""
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import warnings
warnings.filterwarnings('ignore')

# 全局图表主题 - 深色背景
import plotly.io as pio
pio.templates["dark_theme"] = go.layout.Template(
    layout=go.Layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#ffffff', size=12),
        title=dict(font=dict(color='#00d9ff', size=18)),
        xaxis=dict(
            gridcolor='rgba(255,255,255,0.1)',
            linecolor='rgba(255,255,255,0.3)',
            tickfont=dict(color='#ffffff'),
            title=dict(font=dict(color='#ffffff', size=14)),
            zerolinecolor='rgba(255,255,255,0.2)'
        ),
        yaxis=dict(
            gridcolor='rgba(255,255,255,0.1)',
            linecolor='rgba(255,255,255,0.3)',
            tickfont=dict(color='#ffffff'),
            title=dict(font=dict(color='#ffffff', size=14)),
            zerolinecolor='rgba(255,255,255,0.2)'
        ),
        legend=dict(
            font=dict(color='#ffffff', size=12),
            bgcolor='rgba(0,0,0,0)',
            title=dict(font=dict(color='#ffffff', size=14))
        ),
        coloraxis=dict(
            colorbar=dict(
                tickfont=dict(color='#ffffff'),
                title=dict(font=dict(color='#ffffff'))
            )
        )
    )
)
pio.templates.default = "dark_theme"

# 设置页面配置
st.set_page_config(
    page_title="大学生行为分析与干预系统",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 自定义CSS样式 - 高大上外观
st.markdown("""
<style>
    /* 全局背景 */
    .stApp {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
        background-attachment: fixed;
    }
    
    /* 卡片容器背景 */
    .main .block-container {
        background: rgba(255, 255, 255, 0.02);
        border-radius: 20px;
        padding: 2rem;
    }
    
    /* 标题样式 */
    h1, h2, h3 {
        color: #ffffff !important;
        font-weight: 700 !important;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    }
    
    /* 正文文字颜色 - 增强对比度 */
    p, span, div {
        color: #e0e0e0 !important;
    }
    
    /* 标签页文字 */
    .stTabs [data-baseweb="tab-list"] button [data-testid="stMarkdownContainer"] p {
        color: #ffffff !important;
    }
    
    /* 展开面板 */
    .streamlit-expanderHeader {
        background: rgba(0,217,255,0.1) !important;
        color: #ffffff !important;
    }
    
    /* 表格文字 */
    .dataframe {
        color: #ffffff !important;
    }
    
    /* 表格行 */
    .dataframe tbody tr {
        background: rgba(255,255,255,0.05) !important;
        color: #ffffff !important;
    }
    
    /* 表格表头 */
    .dataframe thead th {
        background: rgba(0,217,255,0.2) !important;
        color: #00d9ff !important;
    }
    
    /* 指标数值 */
    [data-testid="stMetricValue"] {
        color: #00d9ff !important;
        text-shadow: 0 0 10px rgba(0,217,255,0.5) !important;
    }
    
    /* 指标标签 */
    [data-testid="stMetricLabel"] {
        color: #b0b0b0 !important;
    }
    
    /* 下拉框选项 */
    [data-testid="stSelectbox"] label {
        color: #ffffff !important;
    }
    
    h1 {
        font-size: 3rem !important;
        background: linear-gradient(90deg, #00d9ff, #00ff88, #00d9ff) !important;
        background-size: 200% auto !important;
        -webkit-background-clip: text !important;
        -webkit-text-fill-color: transparent !important;
        background-clip: text !important;
        animation: shine 3s linear infinite !important;
    }
    
    @keyframes shine {
        to { background-position: 200% center; }
    }
    
    h2 {
        border-bottom: 3px solid;
        border-image: linear-gradient(90deg, #00d9ff, #00ff88) 1;
        padding-bottom: 10px;
        margin-bottom: 20px;
    }
    
    /* 指标卡片 */
    .stMetric {
        background: linear-gradient(135deg, rgba(0,217,255,0.1) 0%, rgba(0,255,136,0.1) 100%);
        border: 1px solid rgba(0,217,255,0.3);
        border-radius: 15px;
        padding: 20px;
        transition: all 0.3s ease !important;
    }
    .stMetric:hover {
        transform: translateY(-5px);
        box-shadow: 0 10px 30px rgba(0,217,255,0.3);
        border-color: #00d9ff;
    }
    .stMetric label {
        color: #aaa !important;
    }
    .stMetric [data-testid="stMetricValue"] {
        color: #00d9ff !important;
        font-size: 2rem !important;
    }
    
    /* 卡片悬停动画 */
    .stMetric {
        transition: all 0.3s ease !important;
    }
    .stMetric:hover {
        transform: scale(1.05);
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    }
    
    /* 数据表格行悬停效果 */
    .dataframe tbody tr:hover {
        background-color: rgba(51, 102, 204, 0.1) !important;
        transform: scale(1.01);
        transition: all 0.2s ease;
    }
    
    /* 按钮悬停动画 */
    .stButton>button {
        transition: all 0.3s ease !important;
        background: linear-gradient(90deg, #00d9ff, #00ff88) !important;
        border: none !important;
        color: #1a1a2e !important;
        font-weight: bold !important;
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 15px rgba(0,217,255,0.5) !important;
    }
    
    /* 信息卡片动画 */
    .stInfo, .stSuccess, .stWarning, .stError {
        transition: all 0.3s ease !important;
        border-radius: 10px !important;
    }
    .stInfo { background: rgba(0,217,255,0.1) !important; border: 1px solid rgba(0,217,255,0.3) !important; }
    .stSuccess { background: rgba(0,255,136,0.1) !important; border: 1px solid rgba(0,255,136,0.3) !important; }
    .stWarning { background: rgba(255,170,0,0.1) !important; border: 1px solid rgba(255,170,0,0.3) !important; }
    .stError { background: rgba(255,68,68,0.1) !important; border: 1px solid rgba(255,68,68,0.3) !important; }
    
    /* 侧边栏 - 深色背景 */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0f3460 0%, #16213e 100%) !important;
    }
    
    /* 侧边栏文字 */
    [data-testid="stSidebar"] h1, 
    [data-testid="stSidebar"] h2, 
    [data-testid="stSidebar"] h3,
    [data-testid="stSidebar"] p,
    [data-testid="stSidebar"] span {
        color: #ffffff !important;
    }
    
    /* 导航菜单 */
    [data-testid="stSidebar"] .stRadio label {
        color: #ffffff !important;
        font-size: 1.1em !important;
    }
    
    /* 下拉框和输入框 - 深色背景 */
    .stSelectbox, .stMultiselect, .stTextInput, .stSlider {
        background: rgba(0,0,0,0.3) !important;
        border-radius: 10px !important;
        border: 1px solid rgba(0,217,255,0.3) !important;
    }
    
    /* 下拉框内部文字 */
    .stSelectbox div[data-baseweb="select"] {
        color: #ffffff !important;
    }
    
    /* 下拉框输入区域 */
    .stSelectbox div[data-baseweb="select"] > div {
        background: #1a1a2e !important;
        color: #ffffff !important;
    }
    
    /* 下拉框选中文字 */
    .stSelectbox div[data-baseweb="select"] span {
        color: #ffffff !important;
    }
    
    /* 下拉选项菜单 - 弹出层 */
    div[role="listbox"],
    div[data-baseweb="menu"] {
        background: #1a1a2e !important;
        border: 1px solid rgba(0,217,255,0.3) !important;
    }
    
    /* 下拉选项 */
    div[role="option"],
    div[data-baseweb="menu"] div {
        color: #ffffff !important;
        background: #1a1a2e !important;
    }
    
    /* 下拉选项悬停 */
    div[role="option"]:hover,
    div[data-baseweb="menu"] div:hover {
        background: rgba(0,217,255,0.3) !important;
        color: #00d9ff !important;
    }
    
    /* 下拉选项选中状态 */
    div[role="option"][aria-selected="true"],
    div[data-baseweb="menu"] [aria-selected="true"] {
        background: rgba(0,217,255,0.2) !important;
        color: #00d9ff !important;
    }
    
    /* 下拉框主容器 */
    [data-baseweb="select"] {
        background: #1a1a2e !important;
    }
    
    /* 下拉框内部所有div */
    [data-baseweb="select"] div {
        background: #1a1a2e !important;
        color: #ffffff !important;
    }
    
    /* 下拉框箭头 */
    [data-baseweb="select"] svg {
        color: #00d9ff !important;
    }
    
    /* 下拉框输入框 */
    [data-baseweb="select"] input {
        color: #ffffff !important;
        background: transparent !important;
    }
    
    /* 文本输入框容器 */
    .stTextInput > div {
        background: #1a1a2e !important;
        border: 1px solid rgba(0,217,255,0.3) !important;
        border-radius: 10px !important;
    }
    
    /* 输入框文字 */
    .stTextInput input {
        color: #ffffff !important;
        background: transparent !important;
    }
    
    /* 输入框占位符 */
    .stTextInput input::placeholder {
        color: #888888 !important;
    }
    
    /* 文本输入框标签 */
    .stTextInput label {
        color: #00d9ff !important;
    }
    
    /* 搜索框通用样式 */
    .stTextInput input[type="text"] {
        color: #ffffff !important;
        background: #1a1a2e !important;
    }
    
    /* 所有输入框 */
    input[type="text"], 
    input[type="search"] {
        background: #1a1a2e !important;
        color: #ffffff !important;
        border: 1px solid rgba(0,217,255,0.3) !important;
    }
    
    /* 搜索图标颜色 */
    .stTextInput svg {
        color: #00d9ff !important;
    }
    
    /* 筛选框标签 */
    .stSelectbox label, .stMultiselect label, .stTextInput label {
        color: #00d9ff !important;
        font-weight: bold !important;
    }
    
    /* 多选下拉框 */
    .stMultiselect div[data-baseweb="select"] > div {
        background: #1a1a2e !important;
    }
    
    /* 多选标签 */
    .stMultiselect span[data-baseweb="tag"] {
        background: rgba(0,217,255,0.2) !important;
        color: #00d9ff !important;
        border: 1px solid rgba(0,217,255,0.3) !important;
    }
    
    /* 分隔线 */
    hr {
        border-color: rgba(0,217,255,0.3) !important;
    }
    
    /* 数据框样式 */
    .stDataFrame {
        background: rgba(255,255,255,0.05) !important;
        border-radius: 15px !important;
    }
    
    /* 标签 */
    .stBadge {
        background: linear-gradient(90deg, #00d9ff, #00ff88) !important;
        color: #1a1a2e !important;
    }
    
    /* 进度条 */
    .stProgress .stProgress-bar {
        background: linear-gradient(90deg, #00d9ff, #00ff88) !important;
    }
    
    /* 表格表头 */
    thead tr th {
        background: linear-gradient(90deg, #00d9ff, #00ff88) !important;
        color: #1a1a2e !important;
    }
    
    /* 筛选框样式 */
    .stSelectbox, .stMultiselect, .stTextInput {
        transition: all 0.3s ease;
    }
    .stSelectbox:hover, .stMultiselect:hover, .stTextInput:hover {
        transform: translateY(-1px);
    }
    
    /* 图表容器动画 */
    [data-testid="stPlotlyChart"] {
        transition: all 0.3s ease;
    }
    [data-testid="stPlotlyChart"]:hover {
        transform: scale(1.01);
    }
</style>
""", unsafe_allow_html=True)

# 加载数据
@st.cache_data
def load_data():
    """加载清洗后的数据"""
    try:
        df = pd.read_csv('cleaned_data.csv', encoding='utf-8-sig')
        return df
    except:
        return None

@st.cache_data
def load_analysis_results():
    """加载分析结果"""
    import json
    try:
        with open('behavior_analysis_results.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return None

@st.cache_data
def load_risk_students():
    """加载高风险学生列表"""
    try:
        return pd.read_csv('high_risk_students.csv', encoding='utf-8-sig')
    except:
        return None

def filter_data(data, college_filter, major_filter, gender_filter, score_range, search_query):
    """根据筛选条件过滤数据"""
    filtered = data.copy()
    
    # 学院筛选
    if college_filter and len(college_filter) > 0:
        filtered = filtered[filtered['college'].isin(college_filter)]
    
    # 专业筛选
    if major_filter and len(major_filter) > 0:
        filtered = filtered[filtered['major'].isin(major_filter)]
    
    # 性别筛选
    if gender_filter and len(gender_filter) > 0:
        filtered = filtered[filtered['gender'].isin(gender_filter)]
    
    # 成绩范围筛选
    filtered = filtered[
        (filtered['avg_score'] >= score_range[0]) & 
        (filtered['avg_score'] <= score_range[1])
    ]
    
    # 模糊搜索
    if search_query:
        search_mask = (
            filtered['student_id'].astype(str).str.contains(search_query, case=False, na=False) |
            filtered.get('college', '').astype(str).str.contains(search_query, case=False, na=False) |
            filtered.get('major', '').astype(str).str.contains(search_query, case=False, na=False)
        )
        filtered = filtered[search_mask]
    
    return filtered

def main():
    """主函数"""
    # 侧边栏
    st.sidebar.title("📚 导航菜单")
    page = st.sidebar.radio(
        "选择页面",
        ["🏠 首页概览", "👤 学生画像", "📈 行为分析", "📉 学业轨迹", "🔬 高级模型", "⚠️ 风险预警", "📋 个性化报告"]
    )
    
    # 加载数据
    data = load_data()
    analysis_results = load_analysis_results()
    risk_students_df = load_risk_students()
    
    if data is None:
        st.error("❌ 数据加载失败，请先运行数据清洗模块")
        return
    
    # 页面路由
    if page == "🏠 首页概览":
        show_home(data, analysis_results)
    elif page == "👤 学生画像":
        show_profiles(data, analysis_results)
    elif page == "📈 行为分析":
        show_analysis(data, analysis_results)
    elif page == "📉 学业轨迹":
        show_trajectory(data)
    elif page == "🔬 高级模型":
        show_advanced_models(data)
    elif page == "⚠️ 风险预警":
        show_risk_warning(data, risk_students_df)
    elif page == "📋 个性化报告":
        show_reports(data)

def show_home(data, analysis_results):
    """首页概览"""
    st.title("🎓 大学生行为分析与干预系统")
    
    # 炫酷的介绍区域
    st.markdown("""
    <div style='background: linear-gradient(135deg, rgba(0,217,255,0.15) 0%, rgba(0,255,136,0.15) 100%); 
                padding: 30px; border-radius: 20px; border: 1px solid rgba(0,217,255,0.4); 
                margin-bottom: 30px;'>
        <h2 style='color: #00d9ff; text-align: center; margin-bottom: 15px;'>📊 数据驱动的大学生行为分析平台</h2>
        <p style='color: #ccc; text-align: center; font-size: 1.1em;'>
            基于多源数据融合与智能分析，输出8-10项学习行为分析成果<br>
            构建学业风险预测模型(AUC≥80%)，实现个性化干预建议
        </p>
        <div style='display: flex; justify-content: center; gap: 30px; margin-top: 20px;'>
            <span style='color: #00d9ff; font-size: 1.5em;'>🎯 精准画像</span>
            <span style='color: #00ff88; font-size: 1.5em;'>📈 深度分析</span>
            <span style='color: #ffaa00; font-size: 1.5em;'>⚠️ 风险预警</span>
            <span style='color: #ff6692; font-size: 1.5em;'>📋 个性化报告</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # 关键指标卡片 - 带悬停动画
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        with st.container():
            st.metric("👥 学生总数", len(data), help="系统中记录的学生总数")
    
    with col2:
        avg_score = data['avg_score'].mean()
        with st.container():
            st.metric("📚 平均成绩", f"{avg_score:.1f}", 
                     delta=f"{avg_score-75:.1f}", help="全体学生平均成绩")
    
    with col3:
        fail_rate = (data['fail_count'] > 0).mean() * 100
        with st.container():
            st.metric("⚠️ 挂科率", f"{fail_rate:.1f}%", 
                     delta=f"-{100-fail_rate:.1f}%", delta_color="inverse",
                     help="有挂科记录的学生比例")
    
    with col4:
        if 'library_visits' in data.columns:
            avg_lib = data['library_visits'].mean()
            with st.container():
                st.metric("📖 平均图书馆访问", f"{avg_lib:.1f}次", help="人均图书馆访问次数")
    
    # 新增统计卡片
    st.markdown("<br>", unsafe_allow_html=True)
    col5, col6, col7, col8 = st.columns(4)
    
    with col5:
        if 'college' in data.columns:
            college_count = data['college'].nunique()
            st.metric("🏫 学院数量", int(college_count))
    
    with col6:
        if 'major' in data.columns:
            major_count = data['major'].nunique()
            st.metric("📚 专业数量", int(major_count))
    
    with col7:
        high_fail = (data['fail_count'] >= 2).sum()
        st.metric("🔴 重修人数", int(high_fail), help="挂科2门及以上")
    
    with col8:
        if 'total_online_duration' in data.columns:
            avg_online = data['total_online_duration'].mean()
            st.metric("💻 日均上网", f"{avg_online/60:.0f}分钟", help="学生日均上网时长")
    
    st.markdown("---")
    
    # 数据概览
    st.subheader("📋 数据概览")
    
    col_left, col_right = st.columns(2)
    
    with col_left:
        # 成绩分布 - 带主题色
        fig = px.histogram(
            data, 
            x='avg_score',
            nbins=20,
            title='📊 成绩分布',
            labels={'avg_score': '平均成绩', 'count': '学生人数'},
            color_discrete_sequence=['#00d9ff']
        )
        fig.add_vline(x=avg_score, line_dash="dash", line_color="#ff6692", 
                     annotation_text=f"均值: {avg_score:.1f}", annotation_font_color="#ffffff")
        fig.update_traces(
            hovertemplate='成绩: %{x}<br>人数: %{y}<extra></extra>',
            marker_line_width=1,
            marker_line_color='white'
        )
        fig.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='white', size=12),
            title=dict(font=dict(color='#00d9ff', size=16)),
            xaxis=dict(title_font=dict(color='white'), tickfont=dict(color='white')),
            yaxis=dict(title_font=dict(color='white'), tickfont=dict(color='white')),
            yaxis_range=[0, None]
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col_right:
        # 性别分布 - 带主题色
        if 'gender' in data.columns:
            gender_dist = data['gender'].value_counts()
            fig = px.pie(
                values=gender_dist.values,
                names=gender_dist.index,
                title='👥 性别分布',
                color_discrete_sequence=['#00d9ff', '#ff6692']
            )
            fig.update_traces(
                hovertemplate='性别: %{label}<br>人数: %{value}<br>占比: %{percent}<extra></extra>',
                pull=[0.02, 0.02],
                textfont=dict(color='white', size=14)
            )
            fig.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                font_color='white',
                title=dict(font=dict(color='#00d9ff', size=16)),
                legend=dict(
                    font=dict(color='white', size=14),
                    bgcolor='rgba(0,0,0,0)'
                )
            )
            st.plotly_chart(fig, use_container_width=True)
    
    # 学院分布
    if 'college' in data.columns:
        st.markdown("<br>", unsafe_allow_html=True)
        col_dept1, col_dept2 = st.columns(2)
        
        with col_dept1:
            college_dist = data['college'].value_counts().head(10)
            fig = px.bar(
                x=college_dist.values,
                y=college_dist.index,
                orientation='h',
                title='🏫 各学院学生人数 Top10',
                labels={'x': '学生人数', 'y': '学院'},
                color_discrete_sequence=['#00ff88']
            )
            fig.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color='white', size=12),
                title=dict(font=dict(color='#00d9ff', size=16)),
                xaxis=dict(title_font=dict(color='white'), tickfont=dict(color='white')),
                yaxis=dict(title_font=dict(color='white'), tickfont=dict(color='white')),
                height=400
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col_dept2:
            # 成绩排名前10的学院
            college_avg = data.groupby('college')['avg_score'].mean().sort_values(ascending=False).head(10)
            fig = px.bar(
                x=college_avg.values,
                y=college_avg.index,
                orientation='h',
                title='📈 各学院平均成绩 Top10',
                labels={'x': '平均成绩', 'y': '学院'},
                color_discrete_sequence=['#ffaa00']
            )
            fig.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color='white', size=12),
                title=dict(font=dict(color='#00d9ff', size=16)),
                xaxis=dict(title_font=dict(color='white'), tickfont=dict(color='white'), range=[0, 100]),
                yaxis=dict(title_font=dict(color='white'), tickfont=dict(color='white')),
                height=400
            )
            st.plotly_chart(fig, use_container_width=True)
    
    # 系统介绍
    st.markdown("---")
    st.subheader("🎯 系统功能")
    
    features = [
        ("👤 学生画像", "生成学生个体画像与群体画像，涵盖学业水平、学习行为、生活习惯等多维度标签"),
        ("📈 行为分析", "输出8-10项学习行为数据分析成果，识别学生行为规律"),
        ("⚠️ 风险预警", "构建学业风险预测模型，实现高风险学生动态识别"),
        ("📋 个性化报告", "生成包含多维度解释的个性化学生分析报告")
    ]
    
    cols = st.columns(4)
    for i, (title, desc) in enumerate(features):
        with cols[i]:
            with st.container():
                st.markdown(f"""
                <div style='background: linear-gradient(135deg, rgba(0,217,255,0.1) 0%, rgba(0,255,136,0.1) 100%); 
                            padding: 20px; border-radius: 15px; border: 1px solid rgba(0,217,255,0.3); 
                            height: 100%;'>
                    <h4 style='color: #00d9ff; margin: 0 0 10px 0;'>{title}</h4>
                    <p style='color: #ccc; margin: 0; font-size: 0.9em;'>{desc}</p>
                </div>
                """, unsafe_allow_html=True)

def show_profiles(data, analysis_results):
    """学生画像页面 - 添加筛选功能"""
    st.title("👤 学生画像")
    st.markdown("---")
    
    # ========== 筛选区域 ==========
    st.subheader("🔍 数据筛选")
    
    # 获取筛选选项
    colleges = ['全部'] + sorted(data['college'].dropna().unique().tolist()) if 'college' in data.columns else ['全部']
    majors = ['全部'] + sorted(data['major'].dropna().unique().tolist()) if 'major' in data.columns else ['全部']
    genders = ['全部'] + sorted(data['gender'].dropna().unique().tolist()) if 'gender' in data.columns else ['全部']
    
    # 筛选控件布局
    col_f1, col_f2, col_f3 = st.columns(3)
    
    with col_f1:
        college_filter = st.multiselect(
            "🏫 选择学院",
            options=colleges,
            default=[],
            help="可选择一个或多个学院进行筛选"
        )
    
    with col_f2:
        major_filter = st.multiselect(
            "📚 选择专业",
            options=majors,
            default=[],
            help="可选择一个或多个专业进行筛选"
        )
    
    with col_f3:
        gender_filter = st.multiselect(
            "👤 选择性别",
            options=genders,
            default=[],
            help="可选择一个或多个性别进行筛选"
        )
    
    # 成绩范围筛选
    col_f4, col_f5 = st.columns([1, 2])
    
    with col_f4:
        score_range = st.slider(
            "📊 成绩范围",
            min_value=0,
            max_value=100,
            value=(0, 100),
            help="拖动滑块筛选成绩范围"
        )
    
    with col_f5:
        search_query = st.text_input(
            "🔎 模糊搜索",
            placeholder="输入学号、学院或专业关键词...",
            help="支持学号、学院名称、专业名称的模糊搜索"
        )
    
    # 处理筛选条件
    if '全部' in college_filter or len(college_filter) == 0:
        college_filter = None
    if '全部' in major_filter or len(major_filter) == 0:
        major_filter = None
    if '全部' in gender_filter or len(gender_filter) == 0:
        gender_filter = None
    
    # 应用筛选
    filtered_data = filter_data(data, college_filter, major_filter, gender_filter, score_range, search_query)
    
    # 显示筛选结果统计
    st.markdown("---")
    col_s1, col_s2, col_s3 = st.columns(3)
    with col_s1:
        st.metric("筛选后学生数", len(filtered_data), delta=f"{len(filtered_data)-len(data)}")
    with col_s2:
        if len(filtered_data) > 0:
            st.metric("筛选后平均成绩", f"{filtered_data['avg_score'].mean():.1f}")
    with col_s3:
        if len(filtered_data) > 0:
            risk_count = ((filtered_data['fail_count'] >= 2) | (filtered_data['avg_score'] < 60)).sum()
            st.metric("筛选后风险学生", int(risk_count))
    
    st.markdown("---")
    
    # ========== 群体画像 ==========
    st.subheader("👥 群体画像")
    
    # 使用筛选后的数据
    display_data = filtered_data if len(filtered_data) > 0 else data
    
    # 学院分布 - 添加动画
    if 'college' in display_data.columns and len(display_data) > 0:
        college_stats = display_data.groupby('college').agg({
            'student_id': 'count',
            'avg_score': 'mean',
            'avg_gpa': 'mean'
        }).reset_index()
        college_stats.columns = ['学院', '学生数', '平均成绩', '平均绩点']
        college_stats = college_stats.sort_values('学生数', ascending=True)
        
        # 静态水平柱状图
        fig = px.bar(
            college_stats,
            x='学生数',
            y='学院',
            color='平均成绩',
            title='各学院学生分布与成绩',
            labels={'学生数': '学生人数', '平均成绩': '平均成绩'},
            color_continuous_scale='Viridis',
            orientation='h'
        )
        fig.update_traces(
            hovertemplate='学院: %{y}<br>学生数: %{x}<br>平均成绩: %{marker.color:.1f}<extra></extra>',
            marker_line_width=1,
            marker_line_color='white'
        )
        fig.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font_color='white',
            title_font_color='#00d9ff',
            xaxis=dict(gridcolor='rgba(255,255,255,0.1)', linecolor='rgba(255,255,255,0.3)'),
            yaxis=dict(gridcolor='rgba(255,255,255,0.1)', linecolor='rgba(255,255,255,0.3)'),
            coloraxis_colorbar=dict(tickfont=dict(color='white'), title_font=dict(color='white'))
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # 行为特征雷达图
    st.subheader("📊 行为特征分析")
    
    # 计算群体平均行为特征
    behavior_features = {
        '图书馆访问': display_data.get('library_visits', pd.Series([0]*len(display_data))).mean(),
        '任务参与': display_data.get('task_participation', pd.Series([0]*len(display_data))).mean(),
        '考勤记录': display_data.get('total_attendance', pd.Series([0]*len(display_data))).mean(),
        '平均成绩': display_data['avg_score'].mean(),
        '平均绩点': display_data['avg_gpa'].mean() * 25
    }
    
    # 归一化到0-100
    max_vals = {
        '图书馆访问': 50,
        '任务参与': 50,
        '考勤记录': 100,
        '平均成绩': 100,
        '平均绩点': 100
    }
    
    normalized_features = {k: min(v/max_vals[k]*100, 100) for k, v in behavior_features.items()}
    
    # 动态雷达图
    fig = go.Figure()
    
    # 添加雷达图
    # 静态雷达图
    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=list(normalized_features.values()),
        theta=list(normalized_features.keys()),
        fill='toself',
        name='群体平均',
        fillcolor='rgba(0, 217, 255, 0.3)',
        line=dict(color='rgb(0, 217, 255)', width=2)
    ))
    fig.update_layout(
        polar=dict(
            radialaxis=dict(visible=True, range=[0, 100], gridcolor='rgba(255,255,255,0.2)', linecolor='rgba(255,255,255,0.3)'),
            angularaxis=dict(gridcolor='rgba(255,255,255,0.2)', linecolor='rgba(255,255,255,0.3)'),
            bgcolor='rgba(0,0,0,0.2)'
        ),
        showlegend=True,
        title='群体行为特征雷达图',
        paper_bgcolor='rgba(0,0,0,0)',
        font_color='white',
        title_font_color='#00d9ff'
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # ========== 个体画像查询 ==========
    st.markdown("---")
    st.subheader("🔍 个体画像查询")
    
    # 筛选区域
    col_f1, col_f2, col_f3 = st.columns(3)
    
    with col_f1:
        # 学院筛选
        colleges = ['全部'] + sorted(display_data['college'].dropna().unique().tolist()) if 'college' in display_data.columns else ['全部']
        selected_college = st.selectbox("🏫 选择学院", colleges, key="profile_college")
    
    with col_f2:
        # 专业筛选（根据学院动态更新）
        if selected_college != '全部':
            majors = ['全部'] + sorted(display_data[display_data['college']==selected_college]['major'].dropna().unique().tolist())
        else:
            majors = ['全部'] + sorted(display_data['major'].dropna().unique().tolist()) if 'major' in display_data.columns else ['全部']
        selected_major = st.selectbox("📚 选择专业", majors, key="profile_major")
    
    with col_f3:
        # 性别筛选
        genders = ['全部'] + sorted(display_data['gender'].dropna().unique().tolist()) if 'gender' in display_data.columns else ['全部']
        selected_gender = st.selectbox("👤 选择性别", genders, key="profile_gender")
    
    # 应用筛选
    filtered_students = display_data.copy()
    if selected_college != '全部':
        filtered_students = filtered_students[filtered_students['college'] == selected_college]
    if selected_major != '全部':
        filtered_students = filtered_students[filtered_students['major'] == selected_major]
    if selected_gender != '全部':
        filtered_students = filtered_students[filtered_students['gender'] == selected_gender]
    
    # 显示筛选结果统计
    st.caption(f"筛选后共 **{len(filtered_students)}** 名学生")
    
    # 学号下拉菜单
    student_options = [''] + filtered_students['student_id'].astype(str).tolist()
    
    col_search1, col_search2 = st.columns([3, 1])
    with col_search1:
        student_id = st.selectbox(
            "👤 选择学生",
            options=student_options,
            format_func=lambda x: f"学号: {x}" if x else "-- 请选择学生 --",
            key="profile_student"
        )
    
    with col_search2:
        st.write("")
        st.write("")
        if st.button("🔄 随机选择", key="profile_random"):
            if len(filtered_students) > 0:
                import random
                student_id = str(filtered_students['student_id'].sample(1).iloc[0])
                st.rerun()
    
    # 模糊搜索框
    search_query = st.text_input("🔎 学生信息模糊搜索", "", 
                                 placeholder="输入学号、学院或专业关键词...",
                                 help="支持学号、学院名称、专业名称的模糊搜索")
    
    # 模糊匹配建议 - 显示详细信息表格
    if search_query and len(search_query) >= 2:
        # 多字段模糊匹配
        mask = (
            filtered_students['student_id'].astype(str).str.contains(search_query, case=False, na=False) |
            filtered_students['college'].astype(str).str.contains(search_query, case=False, na=False) |
            filtered_students['major'].astype(str).str.contains(search_query, case=False, na=False)
        )
        matches_df = filtered_students[mask].copy()
        
        if len(matches_df) > 0:
            st.write(f"💡 找到 **{len(matches_df)}** 名匹配的学生：")
            
            # 准备显示的数据
            display_df = matches_df[['student_id', 'college', 'major', 'gender', 'avg_score']].copy()
            display_df.columns = ['学号', '学院', '专业', '性别', '平均成绩']
            display_df['平均成绩'] = display_df['平均成绩'].round(1)
            
            # 显示为可点击的表格
            st.dataframe(
                display_df,
                use_container_width=True,
                height=min(300, len(matches_df) * 35 + 50),
                hide_index=True
            )
            
            # 提供选择按钮
            st.write("👇 点击选择学生：")
            
            # 分页显示按钮，每行5个
            match_ids = matches_df['student_id'].astype(str).tolist()
            batch_size = 5
            
            for i in range(0, len(match_ids), batch_size):
                batch = match_ids[i:i+batch_size]
                cols = st.columns(len(batch))
                for j, sid in enumerate(batch):
                    with cols[j]:
                        student_info = matches_df[matches_df['student_id'].astype(str) == sid].iloc[0]
                        btn_label = f"{sid}\n{student_info.get('college', '')[:4]}"
                        if st.button(btn_label, key=f"profile_match_{sid}", use_container_width=True):
                            student_id = sid
                            st.rerun()
        else:
            st.info("未找到匹配的学生，请尝试其他关键词")
    
    if student_id:
        student = display_data[display_data['student_id'].astype(str) == student_id]
        if len(student) > 0:
            student = student.iloc[0]
            
            # 学生信息卡片 - 带悬停效果
            with st.container():
                st.markdown(f"""
                <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                            padding: 20px; border-radius: 10px; color: white; margin: 10px 0;">
                    <h3 style="color: white; margin: 0;">👤 学生: {student['student_id']}</h3>
                    <p style="margin: 5px 0;">🏫 {student.get('college', '未知学院')} | 📚 {student.get('major', '未知专业')}</p>
                </div>
                """, unsafe_allow_html=True)
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("平均成绩", f"{student['avg_score']:.1f}")
            with col2:
                st.metric("平均绩点", f"{student['avg_gpa']:.2f}")
            with col3:
                st.metric("挂科数", int(student['fail_count']))
            
            # 个体雷达图
            individual_features = {
                '图书馆访问': min(student.get('library_visits', 0) / 50 * 100, 100),
                '任务参与': min(student.get('task_participation', 0) / 50 * 100, 100),
                '考勤记录': min(student.get('total_attendance', 0) / 100 * 100, 100),
                '平均成绩': student['avg_score'],
                '平均绩点': student['avg_gpa'] * 25
            }
            
            fig = go.Figure()
            fig.add_trace(go.Scatterpolar(
                r=list(individual_features.values()),
                theta=list(individual_features.keys()),
                fill='toself',
                name='该学生',
                fillcolor='rgba(255, 99, 71, 0.3)',
                line=dict(color='rgb(255, 99, 71)', width=2)
            ))
            fig.add_trace(go.Scatterpolar(
                r=list(normalized_features.values()),
                theta=list(normalized_features.keys()),
                fill='toself',
                name='群体平均',
                fillcolor='rgba(51, 102, 204, 0.3)',
                line=dict(color='rgb(51, 102, 204)', width=2)
            ))
            fig.update_layout(
                polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
                showlegend=True,
                title='个体 vs 群体行为特征对比'
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.error("❌ 未找到该学生")

def show_analysis(data, analysis_results):
    """行为分析页面"""
    st.title("📈 行为分析成果")
    st.markdown("""
    <div style='background: linear-gradient(90deg, rgba(0,217,255,0.1), rgba(0,255,136,0.1)); 
                padding: 20px; border-radius: 15px; border: 1px solid rgba(0,217,255,0.3);'>
        <h3 style='color: #00d9ff; margin: 0;'>🎯 核心发现</h3>
        <p style='color: #ccc; margin: 10px 0 0 0;'>
            基于2500名学生的多维度数据分析，输出10项行为分析成果，揭示学习行为与学业成绩之间的内在关联
        </p>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("---")
    
    if analysis_results is None:
        st.warning("⚠️ 分析结果未找到，请先运行行为分析模块")
        return
    
    # 综合统计卡片
    st.subheader("📊 行为分析统计概览")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("📚 分析维度", "10+", help="涵盖学习行为、图书馆、考勤、任务等维度")
    with col2:
        st.metric("👥 群体聚类", "3-5类", help="基于行为特征的学生分群")
    with col3:
        st.metric("🔗 关联分析", "多维度", help="多变量相关性分析")
    with col4:
        st.metric("⚠️ 风险识别", "精准", help="学业风险因素挖掘")
    
    st.markdown("---")
    
    # 行为模式分布图
    if 'behavior_patterns' in analysis_results and 'pattern_distribution' in analysis_results['behavior_patterns']:
        st.subheader("🎯 学生行为模式分布")
        patterns = analysis_results['behavior_patterns']['pattern_distribution']
        pattern_df = pd.DataFrame(list(patterns.items()), columns=['行为模式', '人数'])
        pattern_df = pattern_df.sort_values('人数', ascending=True)
        
        fig = px.bar(pattern_df, x='人数', y='行为模式', orientation='h',
                    title='学生行为模式分布',
                    color='人数', color_continuous_scale='Viridis')
        fig.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font_color='white'
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # 行为模式成绩对比
        if 'pattern_avg_scores' in analysis_results['behavior_patterns']:
            scores = analysis_results['behavior_patterns']['pattern_avg_scores']
            score_df = pd.DataFrame(list(scores.items()), columns=['行为模式', '平均成绩'])
            score_df = score_df.sort_values('平均成绩', ascending=False)
            
            fig2 = px.bar(score_df, x='行为模式', y='平均成绩',
                         title='不同行为模式的平均成绩对比',
                         color='平均成绩', color_continuous_scale='RdYlGn')
            fig2.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font_color='white',
                yaxis=dict(range=[0, 100])
            )
            st.plotly_chart(fig2, use_container_width=True)
    
    st.markdown("---")
    
    # 展示10个分析成果
    st.subheader("📋 详细分析成果")
    analysis_items = [
        ("📚 学习行为与成绩关联", 'study_behavior_score'),
        ("📖 图书馆行为与学业表现", 'library_performance'),
        ("📋 考勤与学业状态", 'attendance_performance'),
        ("✅ 课堂任务参与与成绩", 'task_score'),
        ("🌐 上网行为与学习效果", 'internet_learning'),
        ("👥 学生群体聚类", 'student_clustering'),
        ("📊 学业成绩分布", 'score_distribution'),
        ("🔗 多维度行为关联", 'multi_behavior_correlation'),
        ("⚠️ 学业风险因素", 'risk_factors'),
        ("🎯 学生行为模式", 'behavior_patterns')
    ]
    
    for i, (title, key) in enumerate(analysis_items):
        if key in analysis_results:
            with st.expander(f"📌 {title}", expanded=False):
                result = analysis_results[key]
                
                # 使用卡片样式展示
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    st.markdown(f"""
                    <div style='background: rgba(0,217,255,0.1); padding: 15px; border-radius: 10px; border-left: 4px solid #00d9ff;'>
                        <h4 style='color: #00d9ff; margin: 0 0 10px 0;'>💡 洞察</h4>
                        <p style='color: #fff; margin: 0;'>{result.get('insight', '暂无洞察')}</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # 显示详细信息
                    if 'correlation' in result:
                        corr_val = result['correlation']
                        if isinstance(corr_val, (int, float)) and not np.isnan(corr_val):
                            st.write(f"**📊 相关系数:** {corr_val:.3f}")
                            # 相关性强度指示条
                            st.progress(abs(corr_val), text=f"相关强度: {abs(corr_val):.1%}")
                
                with col2:
                    if 'cluster_names' in result:
                        st.write("**👥 群体类型:**")
                        for cid, name in result['cluster_names'].items():
                            st.badge(name, color="blue")
                    
                    if 'pattern_distribution' in result:
                        st.write("**🎯 行为模式分布:**")
                        for pattern, count in result['pattern_distribution'].items():
                            st.write(f"  • {pattern}: **{count}人**")
                    
                    if 'risk_rate' in result:
                        st.write(f"**⚠️ 风险率:** {result['risk_rate']:.1f}%")
                    
                    if 'risk_count' in result:
                        st.write(f"**👥 风险人数:** {result['risk_count']}人")

def show_trajectory(data):
    """学业轨迹分析页面 - 与Word文档一致"""
    st.title("📉 学业轨迹分析")
    st.markdown("---")
    
    # 介绍
    st.markdown("""
    <div style='background: linear-gradient(135deg, rgba(0,217,255,0.15) 0%, rgba(0,255,136,0.15) 100%); 
                padding: 20px; border-radius: 15px; border: 1px solid rgba(0,217,255,0.4); margin-bottom: 25px;'>
        <h4 style='color: #00d9ff; margin-bottom: 10px;'>🎯 轨迹分析说明</h4>
        <p style='color: #ccc; margin: 0;'>
            相比静态分析，本模块加入时间维度，对学生行为进行动态观察。
            通过分析学习投入、成绩变化、行为稳定性等指标，识别不同类型的学习轨迹。
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # 导入轨迹分析模块
    try:
        from trajectory_analysis import AcademicTrajectoryAnalyzer
        
        analyzer = AcademicTrajectoryAnalyzer(data)
        
        # ========== 轨迹类型分布 ==========
        st.subheader("📊 学业轨迹类型分布")
        
        trajectory_dist = analyzer.analyze_trajectory()
        
        # 创建轨迹分布图表
        traj_types = list(trajectory_dist.keys())
        traj_counts = [trajectory_dist[t]['count'] for t in traj_types]
        traj_percentages = [float(trajectory_dist[t]['percentage'].rstrip('%')) for t in traj_types]
        
        colors = ['#00ff88', '#00d9ff', '#ff3333', '#ffaa00']
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # 饼图
            fig = go.Figure(data=[go.Pie(
                labels=traj_types,
                values=traj_counts,
                hole=0.4,
                marker=dict(colors=colors),
                textinfo='label+percent',
                textfont=dict(color='white', size=12)
            )])
            
            fig.update_layout(
                title='学业轨迹类型分布',
                title_font_color='#00d9ff',
                paper_bgcolor='rgba(0,0,0,0)',
                font_color='white',
                legend=dict(font=dict(color='white')),
                height=400
            )
            
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.markdown("**📈 轨迹统计**")
            for i, traj_type in enumerate(traj_types):
                count = trajectory_dist[traj_type]['count']
                pct = trajectory_dist[traj_type]['percentage']
                
                st.markdown(f"""
                <div style='background: rgba({int(colors[i][1:3], 16)}, {int(colors[i][3:5], 16)}, {int(colors[i][5:7], 16)}, 0.2); 
                            padding: 12px; border-radius: 8px; margin: 8px 0; 
                            border-left: 4px solid {colors[i]};'>
                    <strong style='color: {colors[i]};'>{traj_type}</strong><br>
                    <span style='color: #fff;'>{count}人 ({pct})</span>
                </div>
                """, unsafe_allow_html=True)
        
        # ========== 轨迹类型说明 ==========
        st.markdown("---")
        st.subheader("📋 轨迹类型特征")
        
        traj_descriptions = {
            '稳定上升型': {
                'icon': '📈',
                'color': '#00ff88',
                '特征': '成绩优秀且稳定，学习状态良好',
                '表现': '平均成绩≥85分，无挂科记录',
                '建议': '保持良好状态，可适当挑战更高目标'
            },
            '稳定型': {
                'icon': '📊',
                'color': '#00d9ff',
                '特征': '成绩稳定，保持在良好水平',
                '表现': '平均成绩70-85分，挂科≤1门',
                '建议': '维持当前学习节奏，争取小幅提升'
            },
            '波动型': {
                'icon': '📉',
                'color': '#ffaa00',
                '特征': '成绩波动较大，学习状态不稳定',
                '表现': '成绩起伏明显，需要关注',
                '建议': '分析波动原因，建立稳定的学习习惯'
            },
            '持续下降型': {
                'icon': '⚠️',
                'color': '#ff3333',
                '特征': '成绩持续下滑，需要重点关注',
                '表现': '平均成绩<60分或挂科≥2门',
                '建议': '立即采取干预措施，制定补救计划'
            }
        }
        
        cols = st.columns(4)
        for idx, (traj_type, info) in enumerate(traj_descriptions.items()):
            with cols[idx]:
                st.markdown(f"""
                <div style='background: rgba({int(info['color'][1:3], 16)}, {int(info['color'][3:5], 16)}, {int(info['color'][5:7], 16)}, 0.15); 
                            padding: 15px; border-radius: 12px; border: 1px solid {info['color']}; height: 100%;'>
                    <h4 style='color: {info['color']}; margin: 0 0 10px 0;'>{info['icon']} {traj_type}</h4>
                    <p style='color: #ccc; font-size: 0.9em; margin: 5px 0;'><strong>特征：</strong>{info['特征']}</p>
                    <p style='color: #aaa; font-size: 0.85em; margin: 5px 0;'><strong>表现：</strong>{info['表现']}</p>
                    <p style='color: #888; font-size: 0.85em; margin: 5px 0;'><strong>建议：</strong>{info['建议']}</p>
                </div>
                """, unsafe_allow_html=True)
        
        # ========== 轨迹趋势分析 ==========
        st.markdown("---")
        st.subheader("🔍 轨迹趋势维度分析")
        
        trends = analyzer.get_trajectory_trends()
        
        for trend_name, trend_info in trends.items():
            with st.expander(f"📊 {trend_name}"):
                st.markdown(f"**描述：**{trend_info['描述']}")
                st.markdown(f"**关键指标：**{', '.join(trend_info['指标'])}")
        
        # ========== 学生轨迹查询 ==========
        st.markdown("---")
        st.subheader("👤 学生个人轨迹查询")
        
        student_id = st.selectbox(
            "选择学生",
            options=[''] + data['student_id'].astype(str).tolist(),
            format_func=lambda x: f"学号: {x}" if x else "-- 请选择学生 --"
        )
        
        if student_id:
            student_traj = analyzer.analyze_trajectory(student_id)
            if student_traj:
                col1, col2 = st.columns([1, 2])
                
                with col1:
                    st.markdown(f"""
                    <div style='background: rgba({int(student_traj['color'][1:3], 16)}, {int(student_traj['color'][3:5], 16)}, {int(student_traj['color'][5:7], 16)}, 0.2); 
                                padding: 20px; border-radius: 15px; border: 2px solid {student_traj['color']}; text-align: center;'>
                        <h3 style='color: {student_traj['color']}; margin: 0;'>{student_traj['type']}</h3>
                        <p style='color: #ccc; margin: 10px 0; font-size: 0.9em;'>{student_traj['description']}</p>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col2:
                    st.metric("平均成绩", f"{student_traj['score']:.1f}")
                    st.metric("平均绩点", f"{student_traj['gpa']:.2f}")
                    st.metric("挂科数", student_traj['fail_count'])
        
    except Exception as e:
        st.error(f"❌ 轨迹分析模块加载失败: {str(e)}")
        st.info("请确保已安装必要的依赖")

def show_risk_warning(data, risk_students_df):
    """风险预警页面 - 添加筛选功能"""
    st.title("⚠️ 学业风险预警")
    st.markdown("---")
    
    # 风险统计
    data['is_risk'] = ((data['fail_count'] >= 2) | (data['avg_score'] < 60)).astype(int)
    risk_count = data['is_risk'].sum()
    risk_rate = risk_count / len(data) * 100
    
    # 关键指标 - 带悬停动画
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("🔴 风险学生数", int(risk_count), 
                 help="挂科2门以上或平均成绩低于60分的学生")
    with col2:
        st.metric("📊 风险率", f"{risk_rate:.1f}%",
                 delta=f"{risk_rate:.1f}%", delta_color="inverse")
    with col3:
        st.metric("👥 总学生数", len(data))
    
    st.markdown("---")
    
    # ========== 筛选区域 ==========
    st.subheader("🔍 风险学生筛选")
    
    # 获取筛选选项
    risk_data = data[data['is_risk'] == 1].copy()
    
    colleges = ['全部'] + sorted(risk_data['college'].dropna().unique().tolist()) if 'college' in risk_data.columns and len(risk_data) > 0 else ['全部']
    majors = ['全部'] + sorted(risk_data['major'].dropna().unique().tolist()) if 'major' in risk_data.columns and len(risk_data) > 0 else ['全部']
    
    col_f1, col_f2, col_f3 = st.columns(3)
    
    with col_f1:
        college_filter = st.multiselect(
            "🏫 学院筛选",
            options=colleges,
            default=[],
            key="risk_college"
        )
    
    with col_f2:
        major_filter = st.multiselect(
            "📚 专业筛选",
            options=majors,
            default=[],
            key="risk_major"
        )
    
    with col_f3:
        risk_search = st.text_input(
            "🔎 学号搜索",
            placeholder="输入学号...",
            key="risk_search"
        )
    
    # 应用筛选
    filtered_risk = risk_data.copy()
    if college_filter and '全部' not in college_filter:
        filtered_risk = filtered_risk[filtered_risk['college'].isin(college_filter)]
    if major_filter and '全部' not in major_filter:
        filtered_risk = filtered_risk[filtered_risk['major'].isin(major_filter)]
    if risk_search:
        filtered_risk = filtered_risk[filtered_risk['student_id'].astype(str).str.contains(risk_search, case=False)]
    
    st.markdown("---")
    
    # 风险分布
    st.subheader("📊 风险分布")
    
    col_left, col_right = st.columns(2)
    
    with col_left:
        # 风险vs正常分布 - 动态环形图
        risk_dist = data['is_risk'].value_counts()
        labels = ['正常', '风险']
        colors = ['#2ECC71', '#E74C3C']
        
        fig = go.Figure()
        
        # 添加环形图
        fig.add_trace(go.Pie(
            labels=labels,
            values=[risk_dist.get(0, 0), risk_dist.get(1, 0)],
            hole=0.4,
            marker=dict(
                colors=colors,
                line=dict(color='white', width=3)
            ),
            textinfo='label+percent',
            textfont=dict(size=14, color='white'),
            hovertemplate='状态: %{label}<br>人数: %{value}<br>占比: %{percent}<extra></extra>',
            pull=[0.02, 0.08],
            rotation=90
        ))
        
        fig.update_layout(
            title='学业风险分布',
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font_color='white',
            title_font_color='#00d9ff'
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col_right:
        # 各学院风险率 - 静态柱状图
        if 'college' in data.columns:
            college_risk = data.groupby('college')['is_risk'].mean().sort_values(ascending=True)
            
            fig = px.bar(
                x=college_risk.values * 100,
                y=college_risk.index,
                orientation='h',
                title='各学院风险率',
                labels={'x': '风险率 (%)', 'y': '学院'},
                color=college_risk.values,
                color_continuous_scale='Reds'
            )
            fig.update_traces(
                hovertemplate='学院: %{y}<br>风险率: %{x:.1f}%<extra></extra>'
            )
            fig.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font_color='white',
                title_font_color='#ff6692'
            )
            st.plotly_chart(fig, use_container_width=True)
    
    # 高风险学生列表 - 带悬停效果
    st.markdown("---")
    st.subheader(f"📋 高风险学生列表 (共{len(filtered_risk)}人)")
    
    if len(filtered_risk) > 0:
        display_cols = ['student_id', 'avg_score', 'fail_count']
        if 'college' in filtered_risk.columns:
            display_cols.append('college')
        if 'major' in filtered_risk.columns:
            display_cols.append('major')
        
        # 添加风险等级列
        filtered_risk['risk_level'] = filtered_risk.apply(
            lambda x: '🔴 高危' if x['fail_count'] >= 3 or x['avg_score'] < 50 else '🟡 中危',
            axis=1
        )
        
        # 使用样式化的dataframe
        styled_df = filtered_risk[display_cols + ['risk_level']].sort_values('avg_score')
        
        # 显示数据表格（不使用applymap避免兼容性问题）
        st.dataframe(
            styled_df,
            use_container_width=True,
            height=400
        )
        
        # 下载按钮
        csv = filtered_risk[display_cols].to_csv(index=False, encoding='utf-8-sig')
        st.download_button(
            label="📥 下载风险学生列表",
            data=csv,
            file_name='risk_students_filtered.csv',
            mime='text/csv'
        )
    else:
        st.info("暂无高风险学生")

def generate_enhanced_report(student, data, cluster_result=None):
    """生成增强版个性化报告"""
    
    # 基础信息
    student_id = student['student_id']
    college = student.get('college', '未知')
    major = student.get('major', '未知')
    gender = student.get('gender', '未知')
    
    # 学业指标
    avg_score = student['avg_score']
    avg_gpa = student['avg_gpa']
    weighted_gpa = student.get('weighted_gpa', avg_gpa)
    fail_count = int(student['fail_count'])
    
    # 行为指标
    lib_visits = student.get('library_visits', 0)
    lib_days = student.get('library_days', 0)
    tasks = student.get('task_participation', 0)
    attend = student.get('total_attendance', 0)
    online_duration = student.get('total_online_duration', 0)
    
    # 计算排名百分比
    score_rank = (data['avg_score'] < avg_score).mean() * 100
    lib_rank = (data['library_visits'] < lib_visits).mean() * 100 if lib_visits > 0 else 0
    
    # 成绩等级
    if avg_score >= 90:
        grade_level = "A (优秀)"
        grade_desc = "成绩优异，学习能力突出"
        grade_color = "#00ff88"
    elif avg_score >= 80:
        grade_level = "B (良好)"
        grade_desc = "成绩良好，有提升空间"
        grade_color = "#00d9ff"
    elif avg_score >= 70:
        grade_level = "C (中等)"
        grade_desc = "成绩中等，需要加强学习"
        grade_color = "#ffaa00"
    elif avg_score >= 60:
        grade_level = "D (及格)"
        grade_desc = "成绩及格，需要重点关注"
        grade_color = "#ff6692"
    else:
        grade_level = "F (不及格)"
        grade_desc = "成绩不及格，急需干预"
        grade_color = "#ff3333"
    
    # 风险等级
    is_high_risk = (fail_count >= 2) or (avg_score < 60)
    is_medium_risk = (avg_score < 70) and not is_high_risk
    
    if is_high_risk:
        risk_level = "高风险"
        risk_color = "#ff3333"
        risk_desc = "学业状况堪忧，需要立即干预"
    elif is_medium_risk:
        risk_level = "中风险"
        risk_color = "#ffaa00"
        risk_desc = "存在一定风险，建议加强关注"
    else:
        risk_level = "低风险"
        risk_color = "#00ff88"
        risk_desc = "学业状况良好，继续保持"
    
    # 学习画像标签
    tags = []
    if avg_score >= 85:
        tags.append(("🏆 学霸", "成绩优异"))
    elif avg_score >= 75:
        tags.append(("📚 勤奋", "学习认真"))
    elif avg_score >= 60:
        tags.append(("⚠️ 需努力", "成绩一般"))
    else:
        tags.append(("🆘 需帮助", "成绩较差"))
    
    if lib_visits > 30:
        tags.append(("📖 图书馆常客", "自主学习能力强"))
    elif lib_visits < 5:
        tags.append(("🏠 宅", "较少去图书馆"))
    
    if tasks > 40:
        tags.append(("✅ 课堂活跃", "积极参与"))
    elif tasks < 15:
        tags.append(("😴 课堂沉默", "参与度低"))
    
    if attend > 80:
        tags.append(("📍 全勤", "出勤优秀"))
    elif attend < 40:
        tags.append(("🚫 缺勤多", "出勤不佳"))
    
    # 同龄人对比
    same_college = data[data['college'] == college] if college != '未知' else data
    college_avg = same_college['avg_score'].mean()
    college_lib_avg = same_college['library_visits'].mean()
    
    comparison = {
        'score_vs_college': avg_score - college_avg,
        'lib_vs_college': lib_visits - college_lib_avg,
        'score_percentile': score_rank,
        'lib_percentile': lib_rank
    }
    
    # 生成建议
    suggestions = []
    detailed_plans = []
    
    if avg_score < 60:
        suggestions.append({
            'title': '🚨 紧急学业干预',
            'priority': '高',
            'content': '成绩不及格，建议立即制定补考计划，寻求学业辅导。',
            'actions': ['联系任课教师了解补考安排', '参加学业辅导班', '制定每日学习计划（至少4小时）']
        })
    elif avg_score < 70:
        suggestions.append({
            'title': '📚 加强课程学习',
            'priority': '中',
            'content': '成绩偏低，建议加强课堂学习，提高作业质量。',
            'actions': ['课前预习，课后复习', '组建学习小组', '定期向老师请教']
        })
    
    if fail_count > 0:
        suggestions.append({
            'title': '📝 重修科目准备',
            'priority': '高',
            'content': f'有{fail_count}门挂科，需要重点准备补考或重修。',
            'actions': ['分析挂科原因', '制定针对性复习计划', '参加补考辅导班']
        })
    
    if lib_visits < 10:
        suggestions.append({
            'title': '📖 培养自主学习习惯',
            'priority': '中',
            'content': '图书馆使用频率较低，建议增加自主学习时间。',
            'actions': ['每周至少去图书馆3次', '利用图书馆电子资源', '参加图书馆学习讲座']
        })
    
    if tasks < 20:
        suggestions.append({
            'title': '✅ 提高课堂参与度',
            'priority': '中',
            'content': '课堂任务参与度不足，建议积极参与课堂互动。',
            'actions': ['主动回答课堂提问', '认真完成每次作业', '参与课堂讨论']
        })
    
    if attend < 50:
        suggestions.append({
            'title': '📍 改善出勤状况',
            'priority': '高',
            'content': '出勤率较低，严重影响学习效果。',
            'actions': ['设置上课提醒', '调整作息时间', '重视每一节课']
        })
    
    if not suggestions:
        suggestions.append({
            'title': '🎉 保持优秀状态',
            'priority': '低',
            'content': '学习状态良好，请继续保持，争取更大进步！',
            'actions': ['继续保持当前学习节奏', '挑战更高目标', '帮助同学共同进步']
        })
    
    return {
        'basic_info': {
            'student_id': student_id,
            'college': college,
            'major': major,
            'gender': gender
        },
        'academic': {
            'avg_score': avg_score,
            'avg_gpa': avg_gpa,
            'weighted_gpa': weighted_gpa,
            'fail_count': fail_count,
            'grade_level': grade_level,
            'grade_desc': grade_desc,
            'grade_color': grade_color
        },
        'behavior': {
            'lib_visits': lib_visits,
            'lib_days': lib_days,
            'tasks': tasks,
            'attend': attend,
            'online_duration': online_duration
        },
        'risk': {
            'level': risk_level,
            'color': risk_color,
            'desc': risk_desc,
            'is_high': is_high_risk,
            'is_medium': is_medium_risk
        },
        'tags': tags,
        'comparison': comparison,
        'suggestions': suggestions
    }


def show_reports(data):
    """个性化报告页面 - 增强版"""
    st.title("📋 个性化学生分析报告")
    st.markdown("---")
    
    # 介绍
    st.markdown("""
    <div style='background: linear-gradient(135deg, rgba(0,217,255,0.15) 0%, rgba(0,255,136,0.15) 100%); 
                padding: 20px; border-radius: 15px; border: 1px solid rgba(0,217,255,0.4); margin-bottom: 25px;'>
        <h4 style='color: #00d9ff; margin-bottom: 10px;'>🎯 报告说明</h4>
        <p style='color: #ccc; margin: 0;'>
            本报告基于多维度数据分析，为每位学生生成个性化的学习画像、风险等级评估和改进建议。
            报告涵盖学业表现、学习行为、同龄人对比等维度，帮助学生全面了解自身学习状况。
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # ========== 筛选区域 ==========
    st.subheader("🔍 学生查询")
    
    col_f1, col_f2 = st.columns([2, 2])
    
    with col_f1:
        colleges = ['全部'] + sorted(data['college'].dropna().unique().tolist()) if 'college' in data.columns else ['全部']
        selected_college = st.selectbox("🏫 选择学院", colleges)
    
    with col_f2:
        if selected_college != '全部':
            majors = ['全部'] + sorted(data[data['college']==selected_college]['major'].dropna().unique().tolist())
        else:
            majors = ['全部'] + sorted(data['major'].dropna().unique().tolist()) if 'major' in data.columns else ['全部']
        selected_major = st.selectbox("📚 选择专业", majors)
    
    # 筛选数据
    filtered_data = data.copy()
    if selected_college != '全部':
        filtered_data = filtered_data[filtered_data['college'] == selected_college]
    if selected_major != '全部':
        filtered_data = filtered_data[filtered_data['major'] == selected_major]
    
    student_options = filtered_data['student_id'].astype(str).tolist()
    
    col_s1, col_s2 = st.columns([3, 1])
    with col_s1:
        student_id = st.selectbox(
            "👤 选择学生",
            options=[''] + student_options,
            format_func=lambda x: f"学号: {x}" if x else "-- 请选择学生 --"
        )
    
    with col_s2:
        st.write("")
        st.write("")
        if st.button("🔄 随机选择"):
            import random
            if len(student_options) > 0:
                student_id = random.choice(student_options)
                st.rerun()
    
    # 生成报告
    if student_id:
        student = data[data['student_id'].astype(str) == student_id]
        if len(student) > 0:
            student = student.iloc[0]
            
            # 生成增强版报告
            report = generate_enhanced_report(student, data)
            
            # ========== 报告头部 ==========
            st.markdown(f"""
            <div style="background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%); 
                        padding: 35px; border-radius: 20px; color: white; text-align: center;
                        border: 2px solid rgba(0,217,255,0.5); margin: 25px 0;
                        box-shadow: 0 0 30px rgba(0,217,255,0.2);">
                <h1 style="color: #00d9ff; margin: 0; font-size: 2.8em; text-shadow: 0 0 20px rgba(0,217,255,0.5);">
                    📊 学生个性化分析报告
                </h1>
                <p style="font-size: 1.3em; margin: 15px 0; color: #ccc;">
                    学号: <strong style="color: #00ff88;">{report['basic_info']['student_id']}</strong> | 
                    学院: <strong style="color: #00ff88;">{report['basic_info']['college']}</strong> | 
                    专业: <strong style="color: #00ff88;">{report['basic_info']['major']}</strong> |
                    性别: <strong style="color: #00ff88;">{report['basic_info']['gender']}</strong>
                </p>
                <p style="color: #888; font-size: 0.9em;">报告生成时间: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M')}</p>
            </div>
            """, unsafe_allow_html=True)
            
            # ========== 学习画像标签 ==========
            st.markdown("### 🏷️ 学习画像标签")
            
            # 使用columns来显示标签
            tag_cols = st.columns(min(len(report['tags']), 4))
            for idx, (tag_name, tag_desc) in enumerate(report['tags']):
                with tag_cols[idx % 4]:
                    st.info(f"**{tag_name}**\n\n*{tag_desc}*")
            
            # ========== 学业表现 ==========
            st.markdown("---")
            st.markdown("### 📚 学业表现分析")
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.markdown(f"""
                <div style="background: rgba(0,217,255,0.1); padding: 20px; border-radius: 15px; 
                            text-align: center; border: 1px solid rgba(0,217,255,0.3);">
                    <p style="color: #888; margin: 0; font-size: 0.9em;">平均成绩</p>
                    <p style="font-size: 2.5em; font-weight: bold; margin: 10px 0; color: {report['academic']['grade_color']};">
                        {report['academic']['avg_score']:.1f}
                    </p>
                    <p style="color: #666; margin: 0; font-size: 0.8em;">满分100分</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                st.markdown(f"""
                <div style="background: rgba(0,255,136,0.1); padding: 20px; border-radius: 15px; 
                            text-align: center; border: 1px solid rgba(0,255,136,0.3);">
                    <p style="color: #888; margin: 0; font-size: 0.9em;">平均绩点</p>
                    <p style="font-size: 2.5em; font-weight: bold; margin: 10px 0; color: #00ff88;">
                        {report['academic']['avg_gpa']:.2f}
                    </p>
                    <p style="color: #666; margin: 0; font-size: 0.8em;">GPA</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col3:
                st.markdown(f"""
                <div style="background: rgba(255,170,0,0.1); padding: 20px; border-radius: 15px; 
                            text-align: center; border: 1px solid rgba(255,170,0,0.3);">
                    <p style="color: #888; margin: 0; font-size: 0.9em;">加权绩点</p>
                    <p style="font-size: 2.5em; font-weight: bold; margin: 10px 0; color: #ffaa00;">
                        {report['academic']['weighted_gpa']:.2f}
                    </p>
                    <p style="color: #666; margin: 0; font-size: 0.8em;">Weighted</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col4:
                fail_color = "#ff3333" if report['academic']['fail_count'] > 0 else "#00ff88"
                st.markdown(f"""
                <div style="background: rgba(255,51,51,0.1); padding: 20px; border-radius: 15px; 
                            text-align: center; border: 1px solid rgba(255,51,51,0.3);">
                    <p style="color: #888; margin: 0; font-size: 0.9em;">挂科数量</p>
                    <p style="font-size: 2.5em; font-weight: bold; margin: 10px 0; color: {fail_color};">
                        {report['academic']['fail_count']}
                    </p>
                    <p style="color: #666; margin: 0; font-size: 0.8em;">门</p>
                </div>
                """, unsafe_allow_html=True)
            
            # 成绩等级和风险等级
            col_grade, col_risk = st.columns(2)
            
            with col_grade:
                st.markdown(f"""
                <div style="background: rgba(0,0,0,0.2); padding: 20px; border-radius: 15px; 
                            margin-top: 20px; border-left: 5px solid {report['academic']['grade_color']};">
                    <h4 style="color: #fff; margin-bottom: 10px;">📊 成绩等级</h4>
                    <p style="font-size: 1.8em; color: {report['academic']['grade_color']}; font-weight: bold; margin: 0;">
                        {report['academic']['grade_level']}
                    </p>
                    <p style="color: #aaa; margin-top: 10px;">{report['academic']['grade_desc']}</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col_risk:
                st.markdown(f"""
                <div style="background: rgba(0,0,0,0.2); padding: 20px; border-radius: 15px; 
                            margin-top: 20px; border-left: 5px solid {report['risk']['color']};">
                    <h4 style="color: #fff; margin-bottom: 10px;">⚠️ 风险等级</h4>
                    <p style="font-size: 1.8em; color: {report['risk']['color']}; font-weight: bold; margin: 0;">
                        {report['risk']['level']}
                    </p>
                    <p style="color: #aaa; margin-top: 10px;">{report['risk']['desc']}</p>
                </div>
                """, unsafe_allow_html=True)
            
            # ========== 同龄人对比 ==========
            st.markdown("---")
            st.markdown("### 📈 同龄人对比分析")
            
            col_comp1, col_comp2 = st.columns(2)
            
            with col_comp1:
                score_diff = report['comparison']['score_vs_college']
                score_diff_color = "#00ff88" if score_diff > 0 else "#ff6692"
                score_diff_icon = "▲" if score_diff > 0 else "▼"
                
                fig_score = go.Figure()
                fig_score.add_trace(go.Bar(
                    x=['该学生', '学院平均'],
                    y=[report['academic']['avg_score'], report['academic']['avg_score'] - score_diff],
                    marker_color=['#00d9ff', 'rgba(255,255,255,0.3)'],
                    text=[f"{report['academic']['avg_score']:.1f}", 
                          f"{report['academic']['avg_score'] - score_diff:.1f}"],
                    textposition='outside',
                    textfont=dict(color='white')
                ))
                fig_score.update_layout(
                    title='成绩对比',
                    title_font_color='#00d9ff',
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    font_color='white',
                    height=300,
                    yaxis=dict(gridcolor='rgba(255,255,255,0.1)', title='平均成绩'),
                    showlegend=False
                )
                st.plotly_chart(fig_score, use_container_width=True)
                
                st.markdown(f"""
                <div style="text-align: center; margin-top: -10px;">
                    <span style="color: {score_diff_color}; font-size: 1.2em; font-weight: bold;">
                        {score_diff_icon} {abs(score_diff):.1f}分
                    </span>
                    <span style="color: #888;"> vs 学院平均</span>
                </div>
                """, unsafe_allow_html=True)
            
            with col_comp2:
                lib_diff = report['comparison']['lib_vs_college']
                lib_diff_color = "#00ff88" if lib_diff > 0 else "#ff6692"
                lib_diff_icon = "▲" if lib_diff > 0 else "▼"
                
                fig_lib = go.Figure()
                fig_lib.add_trace(go.Bar(
                    x=['该学生', '学院平均'],
                    y=[report['behavior']['lib_visits'], 
                       max(0, report['behavior']['lib_visits'] - lib_diff)],
                    marker_color=['#00ff88', 'rgba(255,255,255,0.3)'],
                    text=[f"{report['behavior']['lib_visits']:.0f}", 
                          f"{max(0, report['behavior']['lib_visits'] - lib_diff):.0f}"],
                    textposition='outside',
                    textfont=dict(color='white')
                ))
                fig_lib.update_layout(
                    title='图书馆访问对比',
                    title_font_color='#00ff88',
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    font_color='white',
                    height=300,
                    yaxis=dict(gridcolor='rgba(255,255,255,0.1)', title='访问次数'),
                    showlegend=False
                )
                st.plotly_chart(fig_lib, use_container_width=True)
                
                st.markdown(f"""
                <div style="text-align: center; margin-top: -10px;">
                    <span style="color: {lib_diff_color}; font-size: 1.2em; font-weight: bold;">
                        {lib_diff_icon} {abs(lib_diff):.0f}次
                    </span>
                    <span style="color: #888;"> vs 学院平均</span>
                </div>
                """, unsafe_allow_html=True)
            
            # 排名百分比
            col_rank1, col_rank2 = st.columns(2)
            with col_rank1:
                st.progress(report['comparison']['score_percentile']/100, 
                           text=f"成绩排名: 超过 {report['comparison']['score_percentile']:.1f}% 的同学")
            with col_rank2:
                st.progress(report['comparison']['lib_percentile']/100, 
                           text=f"图书馆排名: 超过 {report['comparison']['lib_percentile']:.1f}% 的同学")
            
            # ========== 学习行为详情 ==========
            st.markdown("---")
            st.markdown("### 📊 学习行为详情")
            
            col_b1, col_b2, col_b3, col_b4 = st.columns(4)
            
            behavior_metrics = [
                ("📖 图书馆访问", f"{report['behavior']['lib_visits']:.0f}次", 
                 f"{report['behavior']['lib_days']:.0f}天"),
                ("✅ 任务参与", f"{report['behavior']['tasks']:.0f}次", "课堂互动"),
                ("📍 出勤记录", f"{report['behavior']['attend']:.0f}次", "考勤打卡"),
                ("💻 在线时长", f"{report['behavior']['online_duration']/60:.1f}小时", "学习平台")
            ]
            
            for col, (label, value, sub) in zip([col_b1, col_b2, col_b3, col_b4], behavior_metrics):
                with col:
                    st.markdown(f"""
                    <div style="background: rgba(255,255,255,0.05); padding: 15px; border-radius: 10px; 
                                text-align: center; border: 1px solid rgba(255,255,255,0.1);">
                        <p style="color: #888; margin: 0; font-size: 0.85em;">{label}</p>
                        <p style="font-size: 1.8em; font-weight: bold; margin: 5px 0; color: #fff;">{value}</p>
                        <p style="color: #666; margin: 0; font-size: 0.75em;">{sub}</p>
                    </div>
                    """, unsafe_allow_html=True)
            
            # ========== 个性化建议 ==========
            st.markdown("---")
            st.markdown("### 💡 个性化改进建议")
            
            for i, suggestion in enumerate(report['suggestions']):
                priority_colors = {
                    '高': '#ff3333',
                    '中': '#ffaa00',
                    '低': '#00ff88'
                }
                priority_color = priority_colors.get(suggestion['priority'], '#00d9ff')
                
                with st.container():
                    st.markdown(f"""
                    <div style="background: linear-gradient(90deg, rgba(0,0,0,0.3) 0%, rgba(0,0,0,0.1) 100%); 
                                padding: 20px; border-radius: 12px; margin: 15px 0;
                                border-left: 5px solid {priority_color};
                                box-shadow: 0 4px 15px rgba(0,0,0,0.2);">
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
                            <h4 style="color: #fff; margin: 0;">{suggestion['title']}</h4>
                            <span style="background: {priority_color}; color: white; padding: 3px 10px; 
                                        border-radius: 10px; font-size: 0.8em;">
                                优先级: {suggestion['priority']}
                            </span>
                        </div>
                        <p style="color: #ccc; margin: 10px 0;">{suggestion['content']}</p>
                        <div style="margin-top: 15px;">
                            <p style="color: #888; font-size: 0.9em; margin-bottom: 8px;">📝 具体行动:</p>
                            <ul style="color: #aaa; margin: 0; padding-left: 20px;">
                    """, unsafe_allow_html=True)
                    
                    for action in suggestion['actions']:
                        st.markdown(f"<li style='margin: 5px 0;'>{action}</li>", unsafe_allow_html=True)
                    
                    st.markdown("</ul></div></div>", unsafe_allow_html=True)
            
            # ========== 导出报告 ==========
            st.markdown("---")
            st.markdown("### 📥 报告导出")
            
            # 生成Markdown报告内容
            report_md = f"""# 📊 学生个性化分析报告

## 基本信息
- **学号:** {report['basic_info']['student_id']}
- **学院:** {report['basic_info']['college']}
- **专业:** {report['basic_info']['major']}
- **性别:** {report['basic_info']['gender']}
- **报告生成时间:** {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M')}

## 🏷️ 学习画像标签
{chr(10).join([f"- **{tag[0]}**: {tag[1]}" for tag in report['tags']])}

## 📚 学业表现
| 指标 | 数值 | 等级 |
|------|------|------|
| 平均成绩 | {report['academic']['avg_score']:.1f} | {report['academic']['grade_level']} |
| 平均绩点 | {report['academic']['avg_gpa']:.2f} | - |
| 加权绩点 | {report['academic']['weighted_gpa']:.2f} | - |
| 挂科数量 | {report['academic']['fail_count']} | - |

**成绩评价:** {report['academic']['grade_desc']}

## ⚠️ 风险评估
**风险等级:** {report['risk']['level']}

**风险描述:** {report['risk']['desc']}

## 📈 同龄人对比
- **成绩对比:** 该学生成绩 {'高于' if report['comparison']['score_vs_college'] > 0 else '低于'}学院平均 {abs(report['comparison']['score_vs_college']):.1f}分
- **成绩排名:** 超过 {report['comparison']['score_percentile']:.1f}% 的同学
- **图书馆对比:** {'高于' if report['comparison']['lib_vs_college'] > 0 else '低于'}学院平均 {abs(report['comparison']['lib_vs_college']):.0f}次
- **图书馆排名:** 超过 {report['comparison']['lib_percentile']:.1f}% 的同学

## 📊 学习行为详情
- **图书馆访问:** {report['behavior']['lib_visits']:.0f}次 ({report['behavior']['lib_days']:.0f}天)
- **任务参与:** {report['behavior']['tasks']:.0f}次
- **出勤记录:** {report['behavior']['attend']:.0f}次
- **在线时长:** {report['behavior']['online_duration']/60:.1f}小时

## 💡 个性化改进建议

"""
            
            for i, suggestion in enumerate(report['suggestions'], 1):
                report_md += f"""### {i}. {suggestion['title']} (优先级: {suggestion['priority']})

{suggestion['content']}

**具体行动:**
"""
                for action in suggestion['actions']:
                    report_md += f"- {action}\n"
                report_md += "\n"
            
            report_md += """
---
*本报告由大学生行为分析与干预系统自动生成*
"""
            
            col_dl1, col_dl2, col_dl3 = st.columns([1, 2, 1])
            with col_dl2:
                st.download_button(
                    label="📥 下载完整报告 (Markdown)",
                    data=report_md,
                    file_name=f"report_{report['basic_info']['student_id']}_{pd.Timestamp.now().strftime('%Y%m%d')}.md",
                    mime="text/markdown",
                    use_container_width=True
                )
            
            # 打印报告预览
            with st.expander("📄 查看报告预览"):
                st.markdown(report_md)
                
        else:
            st.error("❌ 未找到该学生")


def show_advanced_models(data):
    """高级模型分析页面 - KMeans聚类 + 逻辑回归风险预测 + 可解释性分析"""
    st.title("🔬 高级模型分析")
    
    # 介绍
    st.markdown("""
    <div style='background: linear-gradient(135deg, rgba(0,217,255,0.15) 0%, rgba(255,102,146,0.15) 100%); 
                padding: 25px; border-radius: 15px; border: 1px solid rgba(0,217,255,0.4); margin-bottom: 30px;'>
        <h3 style='color: #00d9ff; margin-bottom: 15px;'>🎯 核心模型架构</h3>
        <div style='display: grid; grid-template-columns: repeat(3, 1fr); gap: 20px;'>
            <div style='text-align: center;'>
                <div style='font-size: 2em; margin-bottom: 10px;'>🧩</div>
                <strong style='color: #00ff88;'>KMeans聚类</strong>
                <p style='color: #ccc; font-size: 0.9em;'>学生分群：4类学生群体</p>
            </div>
            <div style='text-align: center;'>
                <div style='font-size: 2em; margin-bottom: 10px;'>📊</div>
                <strong style='color: #00d9ff;'>逻辑回归预测</strong>
                <p style='color: #ccc; font-size: 0.9em;'>学业风险预测 (AUC≥0.8)</p>
            </div>
            <div style='text-align: center;'>
                <div style='font-size: 2em; margin-bottom: 10px;'>🔍</div>
                <strong style='color: #ffaa00;'>归因分析</strong>
                <p style='color: #ccc; font-size: 0.9em;'>三维度特征解释</p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # 导入高级模型
    try:
        from advanced_models import StudentClustering, LogisticRiskModel
        
        # ========== 模型1: KMeans聚类 ==========
        st.markdown("---")
        st.subheader("🧩 核心模型1: 学生分群 (KMeans聚类)")
        
        # 执行聚类
        clustering = StudentClustering(data)
        cluster_result = clustering.fit(n_clusters=4)
        
        # 显示聚类结果表格
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown("**📊 聚类结果统计**")
            cluster_df = pd.DataFrame({
                '类别': [f"{info['name']}" for info in cluster_result['cluster_names'].values()],
                '特征': [f"{info['desc']}" for info in cluster_result['cluster_names'].values()],
                '学生数量': list(cluster_result['cluster_counts'].values()),
                '占比(%)': [f"{v/len(data)*100:.1f}%" for v in cluster_result['cluster_counts'].values()],
                '平均成绩': cluster_result['cluster_features']['score_avg'].values,
                '日均学习(小时)': cluster_result['cluster_features']['study_time'].values.round(1),
                '图书馆访问': cluster_result['cluster_features']['library_count'].values.round(0)
            })
            
            # 使用样式美化表格
            st.dataframe(
                cluster_df.style.background_gradient(
                    subset=['平均成绩'], cmap='RdYlGn', vmin=60, vmax=100
                ),
                use_container_width=True,
                hide_index=True
            )
        
        with col2:
            st.markdown("**🎯 分群特征解读**")
            for cluster_id, info in cluster_result['cluster_names'].items():
                count = cluster_result['cluster_counts'][cluster_id]
                pct = count / len(data) * 100
                
                # 根据类型选择颜色
                if '学霸' in info['name'] or 'High' in info['name']:
                    color = '#00ff88'
                    icon = '🏆'
                elif '内卷' in info['name'] or 'Over' in info['name']:
                    color = '#ffaa00'
                    icon = '📚'
                elif '摸鱼' in info['name'] or 'Slack' in info['name']:
                    color = '#00d9ff'
                    icon = '😎'
                else:
                    color = '#ff6692'
                    icon = '⚠️'
                
                st.markdown(f"""
                <div style='background: rgba({int(color[1:3], 16)}, {int(color[3:5], 16)}, {int(color[5:7], 16)}, 0.2); 
                            padding: 10px; border-radius: 8px; margin: 8px 0; border-left: 4px solid {color};'>
                    <strong style='color: {color};'>{icon} {info['name']}</strong><br>
                    <span style='color: #ccc; font-size: 0.85em;'>{info['desc']}</span><br>
                    <span style='color: #fff; font-size: 0.8em;'>{count}人 ({pct:.1f}%)</span>
                </div>
                """, unsafe_allow_html=True)
        
        # 聚类散点图
        st.markdown("**📈 聚类可视化**")
        
        # 创建Plotly聚类图
        fig = make_subplots(rows=1, cols=2, 
                           subplot_titles=('学习行为 vs 成绩', '图书馆行为 vs 成绩'),
                           horizontal_spacing=0.1)
        
        colors = ['#00d9ff', '#ff6692', '#00ff88', '#ffaa00']
        
        # 使用聚类后的数据（clustering.data已经包含cluster列）
        clustered_data = clustering.data
        
        for i, cluster_id in enumerate(sorted(clustered_data['cluster'].unique())):
            mask = clustered_data['cluster'] == cluster_id
            name = cluster_result['cluster_names'][cluster_id]['name']
            
            # 图1: 学习时间 vs 成绩
            fig.add_trace(
                go.Scatter(
                    x=clustered_data.loc[mask, 'study_time'],
                    y=clustered_data.loc[mask, 'score_avg'],
                    mode='markers',
                    name=f'{name}',
                    marker=dict(color=colors[i % len(colors)], size=6, opacity=0.7),
                    legendgroup=f'group{i}',
                    showlegend=True
                ),
                row=1, col=1
            )
            
            # 图2: 图书馆访问 vs 成绩
            fig.add_trace(
                go.Scatter(
                    x=clustered_data.loc[mask, 'library_count'],
                    y=clustered_data.loc[mask, 'score_avg'],
                    mode='markers',
                    name=f'{name}',
                    marker=dict(color=colors[i % len(colors)], size=6, opacity=0.7),
                    legendgroup=f'group{i}',
                    showlegend=False
                ),
                row=1, col=2
            )
        
        fig.update_layout(
            height=450,
            title_text="KMeans聚类散点图 (k=4)",
            title_font_color='#00d9ff',
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font_color='white',
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=-0.2,
                xanchor="center",
                x=0.5,
                font=dict(color='white')
            )
        )
        
        fig.update_xaxes(title_text="日均学习时间(小时)", row=1, col=1, gridcolor='rgba(255,255,255,0.1)')
        fig.update_yaxes(title_text="平均成绩", row=1, col=1, gridcolor='rgba(255,255,255,0.1)')
        fig.update_xaxes(title_text="图书馆访问次数", row=1, col=2, gridcolor='rgba(255,255,255,0.1)')
        fig.update_yaxes(title_text="平均成绩", row=1, col=2, gridcolor='rgba(255,255,255,0.1)')
        
        st.plotly_chart(fig, use_container_width=True)
        
        # ========== 模型2: 逻辑回归风险预测 ==========
        st.markdown("---")
        st.subheader("📊 核心模型2: 学业风险预测 (逻辑回归)")
        
        # 显示模型公式
        st.markdown("""
        <div style='background: rgba(0,217,255,0.1); padding: 15px; border-radius: 10px; margin-bottom: 20px;'>
            <strong style='color: #00d9ff;'>模型公式：</strong>
            <code style='color: #00ff88; font-size: 1.1em;'>P(y=1|x) = 1 / (1 + e<sup>-(β₀ + β₁x₁ + ... + βₙxₙ)</sup>)</code>
        </div>
        """, unsafe_allow_html=True)
        
        # 训练模型
        risk_model = LogisticRiskModel(data)
        risk_result = risk_model.train()
        
        # 显示模型性能指标
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                label="AUC Score",
                value=f"{risk_result['auc']:.4f}",
                delta=f"{risk_result['auc']-0.8:.4f} (目标>0.8)" if risk_result['auc'] > 0.8 else f"{risk_result['auc']-0.8:.4f}",
                delta_color="normal" if risk_result['auc'] > 0.8 else "inverse"
            )
        
        with col2:
            st.metric(
                label="模型准确率",
                value=f"{(risk_model.model.predict(risk_model.scaler.transform(risk_result['X_test'])) == risk_result['y_test']).mean():.2%}"
            )
        
        with col3:
            st.metric(
                label="测试样本数",
                value=f"{len(risk_result['X_test'])}"
            )
        
        with col4:
            st.metric(
                label="特征数量",
                value=f"{len(risk_model.feature_cols)}"
            )
        
        # 显示回归系数
        st.markdown("**📈 逻辑回归系数 (β values)**")
        coef_df = pd.DataFrame({
            '特征': list(risk_result['coefficients'].keys()),
            '系数(β)': list(risk_result['coefficients'].values())
        }).sort_values('系数(β)', key=abs, ascending=False)
        
        st.dataframe(coef_df, use_container_width=True, hide_index=True)
        
        # ROC曲线
        st.markdown("**📈 ROC曲线与AUC分析**")
        
        from sklearn.metrics import roc_curve
        fpr, tpr, _ = roc_curve(risk_result['y_test'], risk_result['y_pred_proba'])
        
        fig_roc = go.Figure()
        
        fig_roc.add_trace(go.Scatter(
            x=fpr, y=tpr,
            mode='lines',
            name=f'ROC曲线 (AUC = {risk_result["auc"]:.4f})',
            line=dict(color='#00d9ff', width=3)
        ))
        
        fig_roc.add_trace(go.Scatter(
            x=[0, 1], y=[0, 1],
            mode='lines',
            name='随机猜测 (AUC = 0.5)',
            line=dict(color='rgba(255,255,255,0.5)', width=2, dash='dash')
        ))
        
        fig_roc.update_layout(
            title='逻辑回归风险预测模型 - ROC曲线',
            title_font_color='#00d9ff',
            xaxis_title='假阳性率 (False Positive Rate)',
            yaxis_title='真阳性率 (True Positive Rate)',
            xaxis=dict(range=[0, 1], gridcolor='rgba(255,255,255,0.1)', tickfont=dict(color='white')),
            yaxis=dict(range=[0, 1.05], gridcolor='rgba(255,255,255,0.1)', tickfont=dict(color='white')),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font_color='white',
            legend=dict(font=dict(color='white')),
            height=500
        )
        
        st.plotly_chart(fig_roc, use_container_width=True)
        
        # ========== 模型3: 三维度行为归因分析 ==========
        st.markdown("---")
        st.subheader("🔍 核心模型3: 行为归因分析 (三维度解释)")
        
        # 按Word文档要求，将特征分为三个维度
        dimension_mapping = {
            '学习投入': ['online_time', 'assignment_count', 'library_count'],
            '学习习惯': ['attendance', 'score_avg', 'avg_gpa'],
            '学习参与': ['total_attendance', 'task_participation']
        }
        
        # 获取特征重要性（使用逻辑回归系数的绝对值）
        importance = np.abs(list(risk_result['coefficients'].values()))
        feature_importance = pd.DataFrame({
            'feature': risk_model.feature_cols,
            'importance': importance
        }).sort_values('importance', ascending=True)
        
        col1, col2 = st.columns([3, 2])
        
        with col1:
            st.markdown("**📊 特征重要性排序**")
            
            # 创建水平条形图
            fig_imp = go.Figure()
            
            colors_imp = [f'rgba(0, 217, 255, {0.4 + 0.6 * (i / len(feature_importance))})' 
                         for i in range(len(feature_importance))]
            
            fig_imp.add_trace(go.Bar(
                x=feature_importance['importance'],
                y=feature_importance['feature'],
                orientation='h',
                marker_color=colors_imp,
                text=feature_importance['importance'].apply(lambda x: f'{x:.3f}'),
                textposition='outside',
                textfont=dict(color='white')
            ))
            
            fig_imp.update_layout(
                title='特征重要性分析 (XGBoost)',
                title_font_color='#00d9ff',
                xaxis_title='重要性得分',
                yaxis_title='特征',
                xaxis=dict(gridcolor='rgba(255,255,255,0.1)', tickfont=dict(color='white')),
                yaxis=dict(gridcolor='rgba(255,255,255,0.1)', tickfont=dict(color='white')),
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font_color='white',
                height=500,
                margin=dict(l=150)
            )
            
            st.plotly_chart(fig_imp, use_container_width=True)
        
        with col2:
            st.markdown("**🎯 关键影响因素解读**")
            
            top5 = feature_importance.tail(5)
            
            for idx, (_, row) in enumerate(top5.iterrows()):
                rank = 5 - idx
                feature_name = row['feature']
                importance_val = row['importance']
                
                # 特征解释
                explanations = {
                    'avg_score': '平均成绩 - 当前学业表现',
                    'fail_count': '挂科数量 - 历史失败记录',
                    'avg_gpa': '平均绩点 - 综合学业水平',
                    'weighted_gpa': '加权绩点 - 学分加权表现',
                    'library_visits': '图书馆访问 - 自主学习行为',
                    'total_attendance': '总出勤次数 - 课堂参与度',
                    'task_participation': '任务参与 - 课堂互动情况',
                    'total_online_duration': '在线时长 - 学习投入时间',
                    'lib_attend_ratio': '图书馆/出勤比 - 自主学习倾向'
                }
                
                explanation = explanations.get(feature_name, feature_name)
                
                st.markdown(f"""
                <div style='background: rgba(0, 217, 255, {0.1 + 0.15 * rank}); 
                            padding: 12px; border-radius: 8px; margin: 8px 0; 
                            border-left: 4px solid rgba(0, 217, 255, {0.3 + 0.14 * rank});'>
                    <strong style='color: #00d9ff;'>#{rank} {feature_name}</strong><br>
                    <span style='color: #ccc; font-size: 0.85em;'>{explanation}</span><br>
                    <span style='color: #00ff88; font-size: 0.9em;'>重要性: {importance_val:.4f}</span>
                </div>
                """, unsafe_allow_html=True)
        
        # ========== 模型公式展示 ==========
        st.markdown("---")
        st.subheader("📐 模型公式与算法原理")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            **KMeans聚类目标函数：**
            ```
            min Σᵢ₌₁ᵏ Σₓ∈Cᵢ ||x - μᵢ||²
            
            其中:
            - k = 4 (聚类数)
            - Cᵢ = 第i个簇
            - μᵢ = 第i个簇的中心
            ```
            """)
            
            st.markdown("**特征选择：**")
            st.markdown("""
            - 学习时间 (online_time)
            - 作业提交次数 (assignment_count)
            - 图书馆访问 (library_count)
            - 成绩均值 (score_avg)
            - 出勤率 (attendance)
            """)
        
        with col2:
            st.markdown("""
            **XGBoost损失函数：**
            ```
            L(φ) = Σᵢ l(yᵢ, ŷᵢ) + Σₖ Ω(fₖ)
            
            其中:
            - l = 对数损失函数
            - Ω = 正则化项
            - fₖ = 第k棵树
            ```
            """)
            
            st.info(f"""
            **模型性能指标：**
            - AUC Score: {risk_result['auc']:.4f}
            - 准确率: {(risk_model.model.predict(risk_model.scaler.transform(risk_result['X_test'])) == risk_result['y_test']).mean():.2%}
            - 特征数: {len(risk_model.feature_cols)}
            """)
        
        # ========== 结论与建议 ==========
        st.markdown("---")
        st.subheader("📝 模型分析结论")
        
        st.markdown("""
        <div style='background: linear-gradient(135deg, rgba(0,255,136,0.1) 0%, rgba(0,217,255,0.1) 100%); 
                    padding: 20px; border-radius: 15px; border: 1px solid rgba(0,255,136,0.3);'>
            <h4 style='color: #00ff88; margin-bottom: 15px;'>📊 核心发现</h4>
            <ul style='color: #ccc; line-height: 2;'>
                <li><strong>学生分群：</strong>通过KMeans聚类识别出4类学生群体，其中"学霸型"占比最高，"摆烂型"需要重点关注</li>
                <li><strong>风险预测：</strong>XGBoost模型AUC达到 {:.4f}，能够有效识别学业风险学生</li>
                <li><strong>关键因子：</strong>{} 是影响学业风险的最重要因素</li>
                <li><strong>干预建议：</strong>针对高风险学生，建议加强{}方面的指导和监督</li>
            </ul>
        </div>
        """.format(
            risk_result['auc'],
            feature_importance.iloc[-1]['feature'],
            feature_importance.iloc[-1]['feature'].replace('_', ' ')
        ), unsafe_allow_html=True)
        
    except Exception as e:
        st.error(f"❌ 高级模型加载失败: {str(e)}")
        st.info("请确保已安装必要的依赖: scikit-learn, xgboost (可选), shap (可选)")


if __name__ == "__main__":
    main()
