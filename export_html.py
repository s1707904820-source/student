import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import json

# 加载数据
data = pd.read_csv('cleaned_data.csv')

# 生成静态HTML页面
html_content = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>大学生行为分析与干预模型</title>
    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: 'Microsoft YaHei', Arial, sans-serif; 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        .container { max-width: 1400px; margin: 0 auto; }
        .header {
            background: white;
            padding: 30px;
            border-radius: 15px;
            text-align: center;
            margin-bottom: 30px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        }
        .header h1 { color: #333; font-size: 2.5em; margin-bottom: 10px; }
        .header p { color: #666; font-size: 1.2em; }
        .nav {
            display: flex;
            justify-content: center;
            gap: 10px;
            margin-bottom: 30px;
            flex-wrap: wrap;
        }
        .nav a {
            padding: 12px 25px;
            background: white;
            color: #333;
            text-decoration: none;
            border-radius: 25px;
            font-weight: bold;
            transition: all 0.3s;
        }
        .nav a:hover { background: #667eea; color: white; }
        .card {
            background: white;
            padding: 25px;
            border-radius: 15px;
            margin-bottom: 30px;
            box-shadow: 0 5px 20px rgba(0,0,0,0.1);
        }
        .card h2 { color: #333; margin-bottom: 20px; padding-bottom: 10px; border-bottom: 2px solid #667eea; }
        .stats { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin-bottom: 30px; }
        .stat-box {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 25px;
            border-radius: 15px;
            text-align: center;
        }
        .stat-box .number { font-size: 2.5em; font-weight: bold; }
        .stat-box .label { font-size: 1.1em; opacity: 0.9; }
        .chart-container { margin: 20px 0; }
        .grid-2 { display: grid; grid-template-columns: repeat(auto-fit, minmax(500px, 1fr)); gap: 30px; }
        table { width: 100%; border-collapse: collapse; margin-top: 20px; }
        th, td { padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }
        th { background: #667eea; color: white; }
        tr:hover { background: #f5f5f5; }
        .footer { text-align: center; color: white; margin-top: 30px; padding: 20px; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🎓 基于多源数据的大学生行为分析与干预模型设计</h1>
            <p>数据驱动的学业风险预警与个性化干预系统</p>
        </div>
        
        <div class="nav">
            <a href="#overview">📊 数据概览</a>
            <a href="#profiles">👥 学生画像</a>
            <a href="#analysis">📈 行为分析</a>
            <a href="#risk">⚠️ 风险预警</a>
            <a href="#reports">📋 个性化报告</a>
        </div>
"""

# 数据概览
total_students = len(data)
avg_score = data['avg_score'].mean()
risk_count = ((data['fail_count'] >= 2) | (data['avg_score'] < 60)).sum()
risk_rate = risk_count / total_students * 100

html_content += f"""
        <div class="card" id="overview">
            <h2>📊 数据概览</h2>
            <div class="stats">
                <div class="stat-box">
                    <div class="number">{total_students}</div>
                    <div class="label">学生总数</div>
                </div>
                <div class="stat-box">
                    <div class="number">{avg_score:.1f}</div>
                    <div class="label">平均成绩</div>
                </div>
                <div class="stat-box">
                    <div class="number">{risk_count}</div>
                    <div class="label">风险学生</div>
                </div>
                <div class="stat-box">
                    <div class="number">{risk_rate:.1f}%</div>
                    <div class="label">风险率</div>
                </div>
            </div>
            
            <div class="grid-2">
                <div class="chart-container">
                    <div id="chart-score-dist"></div>
                </div>
                <div class="chart-container">
                    <div id="chart-gender"></div>
                </div>
            </div>
        </div>
"""

# 成绩分布图
fig_score = px.histogram(data, x='avg_score', nbins=20, title='成绩分布',
                         labels={'avg_score': '平均成绩', 'count': '学生人数'},
                         color_discrete_sequence=['#3366CC'])
fig_score.add_vline(x=avg_score, line_dash="dash", line_color="red", 
                   annotation_text=f"均值: {avg_score:.1f}")

# 性别分布
gender_dist = data['gender'].value_counts() if 'gender' in data.columns else pd.Series({'未知': len(data)})
fig_gender = px.pie(values=gender_dist.values, names=gender_dist.index, title='性别分布',
                   color_discrete_sequence=['#3366CC', '#FF6692'])

html_content += f"""
        <div class="card" id="profiles">
            <h2>👥 学生画像</h2>
"""

# 学院分布
if 'college' in data.columns:
    college_stats = data.groupby('college').agg({
        'student_id': 'count',
        'avg_score': 'mean',
        'avg_gpa': 'mean'
    }).reset_index()
    college_stats.columns = ['学院', '学生数', '平均成绩', '平均绩点']
    college_stats = college_stats.sort_values('学生数', ascending=True)
    
    fig_college = px.bar(college_stats, x='学生数', y='学院', color='平均成绩',
                        title='各学院学生分布与成绩', color_continuous_scale='Blues', orientation='h')
    
    html_content += f"""
            <div class="chart-container">
                <div id="chart-college"></div>
            </div>
            
            <h3>学院统计数据</h3>
            <table>
                <tr><th>学院</th><th>学生数</th><th>平均成绩</th><th>平均绩点</th></tr>
"""
    for _, row in college_stats.head(15).iterrows():
        html_content += f"""<tr><td>{row['学院']}</td><td>{int(row['学生数'])}</td><td>{row['平均成绩']:.1f}</td><td>{row['平均绩点']:.2f}</td></tr>
"""
    html_content += """            </table>
"""

html_content += """
        </div>
"""

# 风险预警
html_content += f"""
        <div class="card" id="risk">
            <h2>⚠️ 学业风险预警</h2>
            <div class="stats">
                <div class="stat-box">
                    <div class="number">{risk_count}</div>
                    <div class="label">风险学生数</div>
                </div>
                <div class="stat-box">
                    <div class="number">{risk_rate:.1f}%</div>
                    <div class="label">风险率</div>
                </div>
            </div>
"""

if 'college' in data.columns:
    data['is_risk'] = ((data['fail_count'] >= 2) | (data['avg_score'] < 60)).astype(int)
    college_risk = data.groupby('college')['is_risk'].mean().sort_values(ascending=True)
    fig_risk = px.bar(x=college_risk.values * 100, y=college_risk.index, orientation='h',
                     title='各学院风险率', labels={'x': '风险率 (%)', 'y': '学院'},
                     color=college_risk.values, color_continuous_scale='Reds')
    
    html_content += f"""
            <div class="chart-container">
                <div id="chart-risk"></div>
            </div>
"""

# 高风险学生列表
high_risk = data[(data['fail_count'] >= 3) | (data['avg_score'] < 50)].copy()
if len(high_risk) > 0:
    high_risk['风险等级'] = high_risk.apply(
        lambda x: '高危' if x['fail_count'] >= 3 or x['avg_score'] < 50 else '中危', axis=1
    )
    
    display_cols = ['student_id', 'avg_score', 'fail_count']
    if 'college' in high_risk.columns:
        display_cols.append('college')
    if 'major' in high_risk.columns:
        display_cols.append('major')
    
    display_df = high_risk[display_cols + ['风险等级']].sort_values('avg_score').head(30)
    
    html_content += f"""
            <h3>高风险学生列表 (前30名)</h3>
            <table>
                <tr><th>学号</th><th>平均成绩</th><th>挂科数</th><th>学院</th><th>专业</th><th>风险等级</th></tr>
"""
    for _, row in display_df.iterrows():
        html_content += f"""<tr>
            <td>{row['student_id']}</td>
            <td>{row['avg_score']:.1f}</td>
            <td>{int(row['fail_count'])}</td>
            <td>{row.get('college', 'N/A')}</td>
            <td>{row.get('major', 'N/A')}</td>
            <td>{row['风险等级']}</td>
        </tr>
"""
    html_content += """            </table>
"""

html_content += """
        </div>
        
        <div class="footer">
            <p>基于多源数据的大学生行为分析与干预模型设计 | Generated by Streamlit</p>
        </div>
    </div>
    
    <script>
"""

# 添加图表数据 - 使用正确的方法
score_json = json.loads(fig_score.to_json())
gender_json = json.loads(fig_gender.to_json())

html_content += f"""
        // 成绩分布图
        var trace1 = {json.dumps(score_json['data'][0])};
        var layout1 = {{
            title: '成绩分布',
            xaxis: {{title: '平均成绩'}},
            yaxis: {{title: '学生人数'}},
            height: 400
        }};
        Plotly.newPlot('chart-score-dist', [trace1], layout1);
        
        // 性别分布图
        var trace2 = {json.dumps(gender_json['data'][0])};
        var layout2 = {{
            title: '性别分布',
            height: 400
        }};
        Plotly.newPlot('chart-gender', [trace2], layout2);
"""

if 'college' in data.columns:
    college_json = json.loads(fig_college.to_json())
    risk_json = json.loads(fig_risk.to_json())
    
    html_content += f"""
        // 学院分布图
        var trace3 = {json.dumps(college_json['data'][0])};
        var layout3 = {{
            title: '各学院学生分布与成绩',
            xaxis: {{title: '学生人数'}},
            yaxis: {{title: '学院'}},
            height: 500
        }};
        Plotly.newPlot('chart-college', [trace3], layout3);
        
        // 风险率图
        var trace4 = {json.dumps(risk_json['data'][0])};
        var layout4 = {{
            title: '各学院风险率',
            xaxis: {{title: '风险率 (%)'}},
            yaxis: {{title: '学院'}},
            height: 400
        }};
        Plotly.newPlot('chart-risk', [trace4], layout4);
"""

html_content += """
    </script>
</body>
</html>
"""

# 保存HTML文件
with open('dashboard_static.html', 'w', encoding='utf-8') as f:
    f.write(html_content)

print("[OK] Static HTML page generated: dashboard_static.html")
print(f"[INFO] Contains data for {len(data)} students")
