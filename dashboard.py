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

# 设置页面配置
st.set_page_config(
    page_title="大学生行为分析与干预系统",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 自定义CSS样式 - 添加动画效果
st.markdown("""
<style>
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
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
    }
    
    /* 信息卡片动画 */
    .stInfo, .stSuccess, .stWarning, .stError {
        transition: all 0.3s ease !important;
    }
    .stInfo:hover, .stSuccess:hover, .stWarning:hover, .stError:hover {
        transform: translateX(5px);
    }
    
    /* 侧边栏动画 */
    .sidebar .sidebar-content {
        animation: slideIn 0.5s ease;
    }
    
    @keyframes slideIn {
        from { transform: translateX(-100%); opacity: 0; }
        to { transform: translateX(0); opacity: 1; }
    }
    
    /* 标题渐变动画 */
    h1 {
        background: linear-gradient(90deg, #3366CC, #FF6692);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
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
        ["🏠 首页概览", "👤 学生画像", "📈 行为分析", "⚠️ 风险预警", "📋 个性化报告"]
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
    elif page == "⚠️ 风险预警":
        show_risk_warning(data, risk_students_df)
    elif page == "📋 个性化报告":
        show_reports(data)

def show_home(data, analysis_results):
    """首页概览"""
    st.title("📊 大学生行为分析与干预系统")
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
    
    st.markdown("---")
    
    # 数据概览
    st.subheader("📋 数据概览")
    
    col_left, col_right = st.columns(2)
    
    with col_left:
        # 成绩分布 - 静态柱状图
        fig = px.histogram(
            data, 
            x='avg_score',
            nbins=20,
            title='成绩分布',
            labels={'avg_score': '平均成绩', 'count': '学生人数'},
            color_discrete_sequence=['#3366CC']
        )
        fig.add_vline(x=avg_score, line_dash="dash", line_color="red", 
                     annotation_text=f"均值: {avg_score:.1f}")
        fig.update_traces(
            hovertemplate='成绩: %{x}<br>人数: %{y}<extra></extra>',
            marker_line_width=1,
            marker_line_color='white'
        )
        fig.update_layout(yaxis_range=[0, None])
        st.plotly_chart(fig, use_container_width=True)
    
    with col_right:
        # 性别分布 - 静态饼图
        if 'gender' in data.columns:
            gender_dist = data['gender'].value_counts()
            fig = px.pie(
                values=gender_dist.values,
                names=gender_dist.index,
                title='性别分布',
                color_discrete_sequence=['#3366CC', '#FF6692']
            )
            fig.update_traces(
                hovertemplate='性别: %{label}<br>人数: %{value}<br>占比: %{percent}<extra></extra>',
                pull=[0.02, 0.02]
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
                st.info(f"**{title}**\n\n{desc}")

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
            color_continuous_scale='Blues',
            orientation='h'
        )
        fig.update_traces(
            hovertemplate='学院: %{y}<br>学生数: %{x}<br>平均成绩: %{marker.color:.1f}<extra></extra>',
            marker_line_width=1,
            marker_line_color='white'
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
        fillcolor='rgba(51, 102, 204, 0.3)',
        line=dict(color='rgb(51, 102, 204)', width=2)
    ))
    fig.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
        showlegend=True,
        title='群体行为特征雷达图'
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
    st.markdown("---")
    
    if analysis_results is None:
        st.warning("⚠️ 分析结果未找到，请先运行行为分析模块")
        return
    
    # 展示10个分析成果 - 添加动画效果
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
            with st.expander(title, expanded=(i==0)):
                result = analysis_results[key]
                
                # 使用卡片样式展示
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    st.info(f"**💡 洞察:** {result.get('insight', '无')}")
                    
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
        
        fig.update_layout(title='学业风险分布')
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

def show_reports(data):
    """个性化报告页面 - 添加筛选功能"""
    st.title("📋 个性化学生分析报告")
    st.markdown("---")
    
    # ========== 筛选区域 ==========
    st.subheader("🔍 学生查询")
    
    col_f1, col_f2 = st.columns([2, 2])
    
    with col_f1:
        # 学院筛选
        colleges = ['全部'] + sorted(data['college'].dropna().unique().tolist()) if 'college' in data.columns else ['全部']
        selected_college = st.selectbox("🏫 选择学院", colleges)
    
    with col_f2:
        # 专业筛选（根据学院动态更新）
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
    
    # 学生选择 - 带搜索功能
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
        if st.button("🔄 随机选择一个学生"):
            import random
            if len(student_options) > 0:
                student_id = random.choice(student_options)
                st.rerun()
    
    # 生成报告
    if student_id:
        student = data[data['student_id'].astype(str) == student_id]
        if len(student) > 0:
            student = student.iloc[0]
            
            # 报告标题 - 带渐变背景
            st.markdown(f"""
            <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                        padding: 30px; border-radius: 15px; color: white; text-align: center;
                        box-shadow: 0 10px 30px rgba(0,0,0,0.2); margin: 20px 0;">
                <h1 style="color: white; margin: 0; font-size: 2.5em;">📄 学生个人分析报告</h1>
                <p style="font-size: 1.2em; margin: 10px 0;">
                    学号: <strong>{student['student_id']}</strong> | 
                    学院: <strong>{student.get('college', '未知')}</strong> | 
                    专业: <strong>{student.get('major', '未知')}</strong>
                </p>
            </div>
            """, unsafe_allow_html=True)
            
            # 学业表现 - 卡片式布局
            st.subheader("📚 学业表现")
            
            col1, col2, col3, col4 = st.columns(4)
            metrics = [
                ("平均成绩", f"{student['avg_score']:.1f}", "分"),
                ("平均绩点", f"{student['avg_gpa']:.2f}", ""),
                ("加权绩点", f"{student.get('weighted_gpa', student['avg_gpa']):.2f}", ""),
                ("挂科数", int(student['fail_count']), "门")
            ]
            
            for col, (label, value, unit) in zip([col1, col2, col3, col4], metrics):
                with col:
                    with st.container():
                        st.markdown(f"""
                        <div style="background: #f0f2f6; padding: 20px; border-radius: 10px; text-align: center;
                                    transition: all 0.3s ease; cursor: pointer;"
                             onmouseover="this.style.transform='scale(1.05)';this.style.boxShadow='0 4px 12px rgba(0,0,0,0.15)'"
                             onmouseout="this.style.transform='scale(1)';this.style.boxShadow='none'">
                            <p style="color: #666; margin: 0; font-size: 0.9em;">{label}</p>
                            <p style="font-size: 2em; font-weight: bold; margin: 5px 0; color: #3366CC;">{value}</p>
                            <p style="color: #999; margin: 0; font-size: 0.8em;">{unit}</p>
                        </div>
                        """, unsafe_allow_html=True)
            
            # 成绩等级
            score = student['avg_score']
            if score >= 90:
                level, color, emoji = "优秀", "green", "🌟"
            elif score >= 80:
                level, color, emoji = "良好", "blue", "👍"
            elif score >= 70:
                level, color, emoji = "中等", "orange", "📖"
            elif score >= 60:
                level, color, emoji = "及格", "yellow", "⚠️"
            else:
                level, color, emoji = "不及格", "red", "❌"
            
            st.markdown(f"""
            <div style="text-align: center; margin: 20px 0;">
                <span style="font-size: 1.2em;">成绩等级: </span>
                <span style="background-color: {color}; color: white; padding: 5px 15px; 
                             border-radius: 20px; font-weight: bold;">{emoji} {level}</span>
            </div>
            """, unsafe_allow_html=True)
            
            # 行为分析
            st.markdown("---")
            st.subheader("📊 学习行为分析")
            
            col_left, col_right = st.columns(2)
            
            with col_left:
                with st.container():
                    st.markdown("**📖 图书馆使用**")
                    lib_visits = student.get('library_visits', 0)
                    
                    # 进度条显示
                    progress = min(lib_visits / 50, 1.0)
                    st.progress(progress, text=f"访问次数: {lib_visits:.0f}次")
                    
                    if lib_visits > 30:
                        st.success("📖 图书馆使用频繁，学习习惯良好！")
                    elif lib_visits > 10:
                        st.info("📖 图书馆使用一般，还有提升空间")
                    else:
                        st.warning("📖 建议增加图书馆使用频率，培养自主学习习惯")
            
            with col_right:
                with st.container():
                    st.markdown("**✅ 课堂参与**")
                    tasks = student.get('task_participation', 0)
                    attend = student.get('total_attendance', 0)
                    
                    col_t1, col_t2 = st.columns(2)
                    with col_t1:
                        st.metric("任务参与", f"{tasks:.0f}次")
                    with col_t2:
                        st.metric("考勤记录", f"{attend:.0f}次")
                    
                    if tasks > 30 and attend > 50:
                        st.success("✅ 课堂参与积极，继续保持！")
                    else:
                        st.info("ℹ️ 课堂参与度一般，建议更加积极参与")
            
            # 风险评估
            st.markdown("---")
            st.subheader("⚠️ 学业风险评估")
            
            is_risk = (student['fail_count'] >= 2) or (student['avg_score'] < 60)
            
            if is_risk:
                st.error("""
                ### 🔴 高风险
                该学生需要重点关注和干预
                """)
                
                risk_factors = []
                if student['fail_count'] >= 2:
                    risk_factors.append(f"挂科科目较多 ({int(student['fail_count'])}门)")
                if student['avg_score'] < 60:
                    risk_factors.append(f"平均成绩偏低 ({student['avg_score']:.1f}分)")
                if lib_visits < 5:
                    risk_factors.append("图书馆使用频率低")
                if tasks < 10:
                    risk_factors.append("课堂任务参与度低")
                
                st.write("**风险因素:**")
                for factor in risk_factors:
                    st.write(f"- ⚠️ {factor}")
                    
            elif student['avg_score'] < 70:
                st.warning("""
                ### 🟡 中风险
                建议加强学习管理和监督
                """)
            else:
                st.success("""
                ### 🟢 低风险
                学业状态良好，请继续保持！
                """)
            
            # 改进建议
            st.markdown("---")
            st.subheader("💡 个性化建议")
            
            suggestions = []
            if student['avg_score'] < 70:
                suggestions.append(("📚 加强课程学习", "建议制定详细的学习计划，合理安排学习时间"))
            if lib_visits < 10:
                suggestions.append(("📖 增加图书馆学习", "培养自主学习习惯，利用图书馆资源"))
            if tasks < 20:
                suggestions.append(("✅ 积极参与课堂", "提高课堂参与度，认真完成作业任务"))
            if student['fail_count'] > 0:
                suggestions.append(("📝 重点复习挂科科目", "必要时寻求辅导帮助，参加补考准备"))
            
            if not suggestions:
                suggestions.append(("🎉 学习状态良好", "请继续保持当前的学习状态！"))
            
            for i, (title, desc) in enumerate(suggestions):
                with st.container():
                    st.markdown(f"""
                    <div style="background: linear-gradient(90deg, #f8f9fa 0%, #e9ecef 100%); 
                                padding: 15px; border-radius: 8px; margin: 10px 0;
                                border-left: 4px solid #3366CC;
                                transition: all 0.3s ease;"
                         onmouseover="this.style.transform='translateX(10px)';this.style.boxShadow='0 4px 12px rgba(0,0,0,0.1)'"
                         onmouseout="this.style.transform='translateX(0)';this.style.boxShadow='none'">
                        <strong>{title}</strong><br>
                        <span style="color: #666;">{desc}</span>
                    </div>
                    """, unsafe_allow_html=True)
            
            # 导出报告按钮
            st.markdown("---")
            report_content = f"""# 学生个人分析报告

**学号:** {student['student_id']}
**学院:** {student.get('college', '未知')}
**专业:** {student.get('major', '未知')}

## 学业表现
- 平均成绩: {student['avg_score']:.1f}
- 平均绩点: {student['avg_gpa']:.2f}
- 挂科数: {int(student['fail_count'])}

## 学习行为
- 图书馆访问: {lib_visits:.0f}次
- 任务参与: {tasks:.0f}次
- 考勤记录: {attend:.0f}次

## 风险评估
{'高风险' if is_risk else '中风险' if student['avg_score'] < 70 else '低风险'}

## 建议
{chr(10).join([f'- {t}: {d}' for t, d in suggestions])}
"""
            
            col_dl1, col_dl2, col_dl3 = st.columns([1, 2, 1])
            with col_dl2:
                st.download_button(
                    label="📥 下载完整报告 (Markdown)",
                    data=report_content,
                    file_name=f"report_{student['student_id']}.md",
                    mime="text/markdown",
                    use_container_width=True
                )
        else:
            st.error("❌ 未找到该学生")


if __name__ == "__main__":
    main()
