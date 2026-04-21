"""
大学生行为分析与干预系统 - 主程序
基于多源数据的大学生行为分析与干预模型设计
"""
import os
import sys

# 设置数据路径
DATA_DIR = "数据集及类型"

def print_banner():
    """打印系统横幅"""
    print("=" * 60)
    print("📊 大学生行为分析与干预系统")
    print("=" * 60)
    print("基于多源数据的大学生行为分析与干预模型设计")
    print("=" * 60)

def check_dependencies():
    """检查依赖是否安装"""
    try:
        import pandas
        import numpy
        import sklearn
        import matplotlib
        import seaborn
        import streamlit
        print("✅ 所有依赖已安装")
        return True
    except ImportError as e:
        print(f"❌ 缺少依赖: {e}")
        print("请运行: .venv\\Scripts\\pip.exe install pandas numpy scikit-learn matplotlib seaborn streamlit openpyxl jinja2")
        return False

def run_full_analysis():
    """运行完整分析流程"""
    print_banner()
    
    # 检查依赖
    if not check_dependencies():
        return
    
    # 步骤1: 数据清洗
    print("\n" + "=" * 60)
    print("步骤 1/5: 数据清洗与标准化")
    print("=" * 60)
    
    from data_cleaner import run_data_cleaning
    data = run_data_cleaning()
    
    if data is None:
        print("❌ 数据清洗失败，程序退出")
        return
    
    # 步骤2: 行为分析
    print("\n" + "=" * 60)
    print("步骤 2/5: 行为数据分析")
    print("=" * 60)
    
    from behavior_analysis import BehaviorAnalyzer
    analyzer = BehaviorAnalyzer(data)
    analysis_results = analyzer.analyze_all()
    analyzer.save_results()
    
    # 步骤3: 风险预警模型
    print("\n" + "=" * 60)
    print("步骤 3/5: 学业风险预警模型")
    print("=" * 60)
    
    from risk_model import run_risk_model
    risk_model = run_risk_model(data)
    
    # 步骤4: 生成综合分析报告
    print("\n" + "=" * 60)
    print("步骤 4/5: 生成综合分析报告")
    print("=" * 60)
    
    generate_summary_report(data, analysis_results, risk_model)
    
    # 步骤5: 启动可视化看板
    print("\n" + "=" * 60)
    print("步骤 5/5: 启动可视化看板")
    print("=" * 60)
    
    print("\n✅ 分析流程已完成！")
    print("\n📊 启动可视化看板...")
    print("在浏览器中访问: http://localhost:8501")
    print("\n按 Ctrl+C 停止看板服务")
    print("=" * 60)
    
    # 启动Streamlit
    os.system(".venv\\Scripts\\streamlit.exe run dashboard.py")

def generate_summary_report(data, analysis_results, risk_model):
    """生成综合分析报告"""
    
    report = []
    report.append("# 大学生行为分析与干预系统 - 综合分析报告\n")
    report.append(f"**分析学生数:** {len(data)}\n")
    report.append(f"**生成时间:** {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    report.append("---\n")
    
    # 1. 数据概况
    report.append("## 一、数据概况\n")
    report.append(f"- 学生总数: {len(data)}\n")
    report.append(f"- 平均成绩: {data['avg_score'].mean():.2f}\n")
    report.append(f"- 平均绩点: {data['avg_gpa'].mean():.2f}\n")
    report.append(f"- 挂科率: {(data['fail_count'] > 0).mean() * 100:.1f}%\n")
    
    if 'library_visits' in data.columns:
        report.append(f"- 平均图书馆访问: {data['library_visits'].mean():.1f}次\n")
    
    report.append("\n")
    
    # 2. 行为分析成果
    report.append("## 二、行为数据分析成果\n")
    
    if analysis_results:
        for i, (key, result) in enumerate(analysis_results.items(), 1):
            report.append(f"### {i}. {result.get('title', key)}\n")
            report.append(f"**洞察:** {result.get('insight', 'N/A')}\n")
            
            if 'correlation' in result:
                report.append(f"**相关系数:** {result['correlation']:.3f}\n")
            
            report.append("\n")
    
    # 3. 风险预警结果
    report.append("## 三、学业风险预警结果\n")
    
    risk_count = ((data['fail_count'] >= 2) | (data['avg_score'] < 60)).sum()
    risk_rate = risk_count / len(data) * 100
    
    report.append(f"- 风险学生数: {risk_count}人\n")
    report.append(f"- 风险率: {risk_rate:.1f}%\n")
    report.append(f"- 模型AUC: {risk_model.auc_score:.4f}\n")
    report.append(f"- 模型性能: {'✅ 达标 (AUC >= 0.80)' if risk_model.auc_score >= 0.80 else '❌ 未达标'}\n")
    
    # 特征重要性
    if risk_model.feature_importance is not None:
        report.append("\n**关键风险因素 (Top 5):**\n")
        for _, row in risk_model.feature_importance.head(5).iterrows():
            report.append(f"- {row['feature']}: {row['importance']:.4f}\n")
    
    report.append("\n")
    
    # 4. 建议与干预措施
    report.append("## 四、建议与干预措施\n")
    report.append("### 针对高风险学生:\n")
    report.append("1. 建立一对一学业帮扶机制\n")
    report.append("2. 定期跟踪学习进度和行为变化\n")
    report.append("3. 提供心理咨询和学习方法指导\n")
    report.append("4. 加强课堂考勤和作业监督\n")
    
    report.append("\n### 针对中风险学生:\n")
    report.append("1. 发送学业预警提醒\n")
    report.append("2. 推荐学习资源和辅导课程\n")
    report.append("3. 鼓励参与学习小组和讨论\n")
    
    report.append("\n### 系统优化建议:\n")
    report.append("1. 持续收集更多行为数据维度\n")
    report.append("2. 定期更新风险预测模型\n")
    report.append("3. 完善个性化干预策略库\n")
    
    # 保存报告
    report_text = "".join(report)
    
    with open("综合分析报告.md", "w", encoding="utf-8") as f:
        f.write(report_text)
    
    print("\n✅ 综合分析报告已生成: 综合分析报告.md")
    
    # 同时保存为Excel
    try:
        summary_df = pd.DataFrame({
            '指标': ['学生总数', '平均成绩', '平均绩点', '挂科率', '风险学生数', '风险率', '模型AUC'],
            '数值': [
                len(data),
                f"{data['avg_score'].mean():.2f}",
                f"{data['avg_gpa'].mean():.2f}",
                f"{(data['fail_count'] > 0).mean() * 100:.1f}%",
                risk_count,
                f"{risk_rate:.1f}%",
                f"{risk_model.auc_score:.4f}"
            ]
        })
        summary_df.to_excel("综合分析报告.xlsx", index=False)
        print("✅ Excel报告已生成: 综合分析报告.xlsx")
    except Exception as e:
        print(f"⚠️ Excel报告生成失败: {e}")

def quick_run():
    """快速运行（仅基础分析）"""
    print_banner()
    
    if not check_dependencies():
        return
    
    print("\n运行快速分析模式...\n")
    
    # 仅运行数据清洗和基础分析
    from data_cleaner import run_data_cleaning
    data = run_data_cleaning()
    
    if data is not None:
        # 保存基础结果
        data.to_excel("学生综合分析结果.xlsx", index=False)
        print("\n✅ 基础分析完成！")
        print("📄 结果文件: 学生综合分析结果.xlsx")

def show_menu():
    """显示菜单"""
    print("\n" + "=" * 60)
    print("请选择运行模式:")
    print("=" * 60)
    print("1. 完整分析流程 (数据清洗 + 行为分析 + 风险模型 + 看板)")
    print("2. 快速分析 (仅数据清洗和基础分析)")
    print("3. 仅启动可视化看板")
    print("4. 退出")
    print("=" * 60)
    
    choice = input("请输入选项 (1-4): ").strip()
    
    if choice == "1":
        run_full_analysis()
    elif choice == "2":
        quick_run()
    elif choice == "3":
        print("\n启动可视化看板...")
        os.system(".venv\\Scripts\\streamlit.exe run dashboard.py")
    elif choice == "4":
        print("再见！")
        sys.exit(0)
    else:
        print("无效选项，请重新选择")
        show_menu()

if __name__ == "__main__":
    import pandas as pd
    
    # 如果有命令行参数，直接运行完整分析
    if len(sys.argv) > 1:
        if sys.argv[1] == "--full":
            run_full_analysis()
        elif sys.argv[1] == "--quick":
            quick_run()
        elif sys.argv[1] == "--dashboard":
            os.system(".venv\\Scripts\\streamlit.exe run dashboard.py")
    else:
        # 交互式菜单
        show_menu()
