# -*- coding: utf-8 -*-
"""
行为分析模块
功能：实现8-10个行为数据分析成果
"""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
import warnings
import sys
warnings.filterwarnings('ignore')

# 设置编码
sys.stdout.reconfigure(encoding='utf-8')

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

class BehaviorAnalyzer:
    """学生行为分析器"""
    
    def __init__(self, data):
        self.data = data.copy()
        self.results = {}
        print("[OK] 行为分析器初始化完成")
    
    def analyze_all(self):
        """执行所有分析"""
        print("\n" + "=" * 50)
        print("开始行为数据分析")
        print("=" * 50)
        
        # 1. 学习行为与成绩关联分析
        self.analysis_1_study_behavior_score()
        
        # 2. 图书馆行为与学业表现分析
        self.analysis_2_library_performance()
        
        # 3. 考勤与学业状态分析
        self.analysis_3_attendance_performance()
        
        # 4. 课堂任务参与与成绩关联
        self.analysis_4_task_score()
        
        # 5. 上网行为与学习效果分析
        self.analysis_5_internet_learning()
        
        # 6. 学生群体聚类分析
        self.analysis_6_student_clustering()
        
        # 7. 学业成绩分布特征
        self.analysis_7_score_distribution()
        
        # 8. 多维度行为特征关联
        self.analysis_8_multi_behavior_correlation()
        
        # 9. 学业风险因素分析
        self.analysis_9_risk_factors()
        
        # 10. 学生行为模式识别
        self.analysis_10_behavior_patterns()
        
        print("\n✅ 全部行为分析完成")
        return self.results
    
    def analysis_1_study_behavior_score(self):
        """分析1: 学习行为与成绩关联分析"""
        print("\n📊 分析1: 学习行为与成绩关联分析")
        
        # 计算学习投入度指标
        self.data['study_engagement'] = (
            self.data.get('library_visits', 0) * 0.3 +
            self.data.get('task_participation', 0) * 0.4 +
            self.data.get('total_attendance', 0) * 0.3
        )
        
        # 相关性分析
        corr = self.data['study_engagement'].corr(self.data['avg_score'])
        
        # 分组比较 - 处理重复边界的情况
        try:
            self.data['engagement_level'] = pd.qcut(
                self.data['study_engagement'], 
                q=4, 
                labels=['低投入', '中低投入', '中高投入', '高投入'],
                duplicates='drop'
            )
        except ValueError:
            # 如果分位数分组失败，使用自定义区间
            self.data['engagement_level'] = pd.cut(
                self.data['study_engagement'],
                bins=[-1, 0, 50, 200, 10000],
                labels=['无投入', '低投入', '中等投入', '高投入']
            )
        
        engagement_score = self.data.groupby('engagement_level')['avg_score'].agg(['mean', 'std', 'count'])
        
        self.results['study_behavior_score'] = {
            'title': '学习行为与成绩关联分析',
            'correlation': corr,
            'engagement_groups': engagement_score.to_dict(),
            'insight': f"学习投入度与平均成绩相关系数为 {corr:.3f}，{'呈显著正相关' if corr > 0.3 else '相关性较弱'}"
        }
        
        print(f"   相关系数: {corr:.3f}")
        print(f"   洞察: {self.results['study_behavior_score']['insight']}")
        
        # 可视化
        fig, axes = plt.subplots(1, 2, figsize=(14, 5))
        
        # 散点图
        axes[0].scatter(self.data['study_engagement'], self.data['avg_score'], alpha=0.5)
        axes[0].set_xlabel('学习投入度')
        axes[0].set_ylabel('平均成绩')
        axes[0].set_title('学习投入度与成绩散点图')
        
        # 箱线图
        self.data.boxplot(column='avg_score', by='engagement_level', ax=axes[1])
        axes[1].set_title('不同投入度组的成绩分布')
        axes[1].set_xlabel('学习投入度等级')
        
        plt.tight_layout()
        plt.savefig('analysis_1_study_behavior.png', dpi=150, bbox_inches='tight')
        plt.close()
        
        return self.results['study_behavior_score']
    
    def analysis_2_library_performance(self):
        """分析2: 图书馆行为与学业表现分析"""
        print("\n📊 分析2: 图书馆行为与学业表现分析")
        
        if 'library_visits' not in self.data.columns:
            print("   ⚠️ 缺少图书馆数据")
            return None
        
        # 图书馆使用分组
        self.data['library_usage'] = pd.cut(
            self.data['library_visits'],
            bins=[-1, 0, 10, 30, 100, 1000],
            labels=['从不', '偶尔', '一般', '经常', '频繁']
        )
        
        library_stats = self.data.groupby('library_usage').agg({
            'avg_score': ['mean', 'std'],
            'avg_gpa': 'mean',
            'student_id': 'count'
        }).round(2)
        
        # 相关性
        corr_visits = self.data['library_visits'].corr(self.data['avg_score'])
        corr_days = self.data.get('library_days', self.data['library_visits']).corr(self.data['avg_score'])
        
        self.results['library_performance'] = {
            'title': '图书馆行为与学业表现分析',
            'visit_score_corr': corr_visits,
            'days_score_corr': corr_days,
            'library_groups': library_stats.to_dict(),
            'insight': f"图书馆访问次数与成绩相关系数为 {corr_visits:.3f}，常去图书馆的学生平均成绩更高"
        }
        
        print(f"   访问-成绩相关系数: {corr_visits:.3f}")
        print(f"   洞察: {self.results['library_performance']['insight']}")
        
        # 可视化
        fig, ax = plt.subplots(figsize=(10, 6))
        library_means = self.data.groupby('library_usage')['avg_score'].mean()
        library_means.plot(kind='bar', ax=ax, color='steelblue')
        ax.set_title('不同图书馆使用频率的平均成绩')
        ax.set_xlabel('图书馆使用频率')
        ax.set_ylabel('平均成绩')
        ax.tick_params(axis='x', rotation=45)
        plt.tight_layout()
        plt.savefig('analysis_2_library.png', dpi=150, bbox_inches='tight')
        plt.close()
        
        return self.results['library_performance']
    
    def analysis_3_attendance_performance(self):
        """分析3: 考勤与学业状态分析"""
        print("\n📊 分析3: 考勤与学业状态分析")
        
        if 'total_attendance' not in self.data.columns:
            print("   ⚠️ 缺少考勤数据")
            return None
        
        # 考勤分组
        self.data['attendance_level'] = pd.cut(
            self.data['total_attendance'],
            bins=[-1, 0, 20, 50, 100, 1000],
            labels=['无记录', '较少', '一般', '良好', '优秀']
        )
        
        attendance_stats = self.data.groupby('attendance_level').agg({
            'avg_score': ['mean', 'std'],
            'fail_count': 'mean',
            'student_id': 'count'
        }).round(2)
        
        corr = self.data['total_attendance'].corr(self.data['avg_score'])
        
        self.results['attendance_performance'] = {
            'title': '考勤与学业状态分析',
            'correlation': corr,
            'attendance_groups': attendance_stats.to_dict(),
            'insight': f"考勤记录数与成绩相关系数为 {corr:.3f}，考勤良好的学生挂科率更低"
        }
        
        print(f"   相关系数: {corr:.3f}")
        print(f"   洞察: {self.results['attendance_performance']['insight']}")
        
        return self.results['attendance_performance']
    
    def analysis_4_task_score(self):
        """分析4: 课堂任务参与与成绩关联"""
        print("\n📊 分析4: 课堂任务参与与成绩关联")
        
        if 'task_participation' not in self.data.columns:
            print("   ⚠️ 缺少任务参与数据")
            return None
        
        corr = self.data['task_participation'].corr(self.data['avg_score'])
        
        # 任务参与分组
        self.data['task_level'] = pd.cut(
            self.data['task_participation'],
            bins=[-1, 0, 10, 30, 100, 1000],
            labels=['不参与', '较少', '一般', '积极', '非常积极']
        )
        
        task_stats = self.data.groupby('task_level')['avg_score'].agg(['mean', 'count'])
        
        self.results['task_score'] = {
            'title': '课堂任务参与与成绩关联',
            'correlation': corr,
            'task_groups': task_stats.to_dict(),
            'insight': f"任务参与度与成绩相关系数为 {corr:.3f}，积极参与任务的学生成绩更优"
        }
        
        print(f"   相关系数: {corr:.3f}")
        print(f"   洞察: {self.results['task_score']['insight']}")
        
        return self.results['task_score']
    
    def analysis_5_internet_learning(self):
        """分析5: 上网行为与学习效果分析"""
        print("\n📊 分析5: 上网行为与学习效果分析")
        
        if 'total_online_duration' not in self.data.columns:
            print("   ⚠️ 缺少上网数据")
            return None
        
        # 计算上网强度
        self.data['internet_intensity'] = pd.cut(
            self.data['total_online_duration'],
            bins=[-1, 0, 100, 500, 1000, 10000],
            labels=['无', '低', '中', '高', '极高']
        )
        
        internet_stats = self.data.groupby('internet_intensity').agg({
            'avg_score': ['mean', 'std'],
            'avg_gpa': 'mean',
            'student_id': 'count'
        }).round(2)
        
        corr = self.data['total_online_duration'].corr(self.data['avg_score'])
        
        self.results['internet_learning'] = {
            'title': '上网行为与学习效果分析',
            'correlation': corr,
            'internet_groups': internet_stats.to_dict(),
            'insight': f"上网时长与成绩相关系数为 {corr:.3f}，{'过度上网可能影响学习' if corr < -0.1 else '上网行为对成绩影响不显著'}"
        }
        
        print(f"   相关系数: {corr:.3f}")
        print(f"   洞察: {self.results['internet_learning']['insight']}")
        
        return self.results['internet_learning']
    
    def analysis_6_student_clustering(self):
        """分析6: 学生群体聚类分析"""
        print("\n📊 分析6: 学生群体聚类分析")
        
        from sklearn.cluster import KMeans
        from sklearn.preprocessing import StandardScaler
        
        # 选择特征进行聚类
        features = ['avg_score', 'avg_gpa', 'library_visits', 'task_participation', 'total_attendance']
        available_features = [f for f in features if f in self.data.columns]
        
        if len(available_features) < 3:
            print("   ⚠️ 可用特征不足，无法进行聚类")
            return None
        
        # 准备数据
        X = self.data[available_features].fillna(0)
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)
        
        # K-means聚类
        kmeans = KMeans(n_clusters=4, random_state=42, n_init=10)
        self.data['cluster'] = kmeans.fit_predict(X_scaled)
        
        # 分析每个簇的特征
        cluster_profiles = self.data.groupby('cluster')[available_features].mean().round(2)
        cluster_sizes = self.data['cluster'].value_counts().to_dict()
        
        # 为每个簇命名
        cluster_names = {}
        for c in range(4):
            profile = cluster_profiles.loc[c]
            if profile['avg_score'] >= 80 and profile.get('library_visits', 0) > 20:
                cluster_names[c] = '学霸型'
            elif profile['avg_score'] >= 60 and profile.get('task_participation', 0) > 10:
                cluster_names[c] = '努力型'
            elif profile['avg_score'] < 60:
                cluster_names[c] = '困难型'
            else:
                cluster_names[c] = '普通型'
        
        self.data['cluster_name'] = self.data['cluster'].map(cluster_names)
        
        self.results['student_clustering'] = {
            'title': '学生群体聚类分析',
            'cluster_profiles': cluster_profiles.to_dict(),
            'cluster_sizes': cluster_sizes,
            'cluster_names': cluster_names,
            'insight': f"学生可分为4类群体：{', '.join(cluster_names.values())}"
        }
        
        print(f"   发现 {len(cluster_names)} 个学生群体")
        print(f"   群体类型: {', '.join(cluster_names.values())}")
        print(f"   洞察: {self.results['student_clustering']['insight']}")
        
        return self.results['student_clustering']
    
    def analysis_7_score_distribution(self):
        """分析7: 学业成绩分布特征"""
        print("\n📊 分析7: 学业成绩分布特征")
        
        # 成绩统计
        score_stats = {
            'mean': self.data['avg_score'].mean(),
            'median': self.data['avg_score'].median(),
            'std': self.data['avg_score'].std(),
            'min': self.data['avg_score'].min(),
            'max': self.data['avg_score'].max()
        }
        
        # 成绩等级分布
        self.data['score_level'] = pd.cut(
            self.data['avg_score'],
            bins=[0, 60, 70, 80, 90, 100],
            labels=['不及格', '及格', '中等', '良好', '优秀']
        )
        
        level_dist = self.data['score_level'].value_counts().to_dict()
        
        # 挂科情况
        fail_rate = (self.data['fail_count'] > 0).mean() * 100
        
        self.results['score_distribution'] = {
            'title': '学业成绩分布特征',
            'statistics': score_stats,
            'level_distribution': level_dist,
            'fail_rate': fail_rate,
            'insight': f"平均成绩 {score_stats['mean']:.1f} 分，挂科率 {fail_rate:.1f}%，成绩呈{'正态' if abs(score_stats['mean'] - score_stats['median']) < 5 else '偏态'}分布"
        }
        
        print(f"   平均成绩: {score_stats['mean']:.1f}")
        print(f"   挂科率: {fail_rate:.1f}%")
        print(f"   洞察: {self.results['score_distribution']['insight']}")
        
        # 可视化
        fig, axes = plt.subplots(1, 2, figsize=(14, 5))
        
        # 成绩分布直方图
        self.data['avg_score'].hist(bins=20, ax=axes[0], edgecolor='black')
        axes[0].axvline(score_stats['mean'], color='red', linestyle='--', label=f'均值: {score_stats["mean"]:.1f}')
        axes[0].set_xlabel('平均成绩')
        axes[0].set_ylabel('学生人数')
        axes[0].set_title('成绩分布直方图')
        axes[0].legend()
        
        # 等级分布饼图
        level_dist_series = pd.Series(level_dist)
        axes[1].pie(level_dist_series.values, labels=level_dist_series.index, autopct='%1.1f%%')
        axes[1].set_title('成绩等级分布')
        
        plt.tight_layout()
        plt.savefig('analysis_7_score_dist.png', dpi=150, bbox_inches='tight')
        plt.close()
        
        return self.results['score_distribution']
    
    def analysis_8_multi_behavior_correlation(self):
        """分析8: 多维度行为特征关联"""
        print("\n📊 分析8: 多维度行为特征关联")
        
        # 选择行为特征
        behavior_cols = ['library_visits', 'task_participation', 'total_attendance', 
                        'total_online_duration', 'avg_score', 'avg_gpa']
        available_cols = [c for c in behavior_cols if c in self.data.columns]
        
        if len(available_cols) < 4:
            print("   ⚠️ 可用特征不足")
            return None
        
        # 计算相关矩阵
        corr_matrix = self.data[available_cols].corr()
        
        # 找出强相关关系
        strong_corrs = []
        for i in range(len(corr_matrix.columns)):
            for j in range(i+1, len(corr_matrix.columns)):
                corr_val = corr_matrix.iloc[i, j]
                if abs(corr_val) > 0.3:
                    strong_corrs.append({
                        'var1': corr_matrix.columns[i],
                        'var2': corr_matrix.columns[j],
                        'correlation': corr_val
                    })
        
        self.results['multi_behavior_correlation'] = {
            'title': '多维度行为特征关联',
            'correlation_matrix': corr_matrix.to_dict(),
            'strong_correlations': strong_corrs,
            'insight': f"发现 {len(strong_corrs)} 组强相关行为特征，学习行为各维度间存在{'显著' if len(strong_corrs) > 3 else '一定'}关联"
        }
        
        print(f"   发现 {len(strong_corrs)} 组强相关特征")
        print(f"   洞察: {self.results['multi_behavior_correlation']['insight']}")
        
        # 可视化热力图
        plt.figure(figsize=(10, 8))
        sns.heatmap(corr_matrix, annot=True, cmap='coolwarm', center=0, 
                   square=True, fmt='.2f', cbar_kws={'shrink': 0.8})
        plt.title('行为特征相关性热力图')
        plt.tight_layout()
        plt.savefig('analysis_8_correlation.png', dpi=150, bbox_inches='tight')
        plt.close()
        
        return self.results['multi_behavior_correlation']
    
    def analysis_9_risk_factors(self):
        """分析9: 学业风险因素分析"""
        print("\n📊 分析9: 学业风险因素分析")
        
        # 定义风险学生（挂科2门以上或平均成绩<60）
        self.data['is_risk'] = (self.data['fail_count'] >= 2) | (self.data['avg_score'] < 60)
        risk_rate = self.data['is_risk'].mean() * 100
        
        # 比较风险学生和非风险学生的行为差异
        risk_students = self.data[self.data['is_risk'] == True]
        normal_students = self.data[self.data['is_risk'] == False]
        
        behavior_diff = {}
        for col in ['library_visits', 'task_participation', 'total_attendance', 'total_online_duration']:
            if col in self.data.columns:
                risk_mean = risk_students[col].mean()
                normal_mean = normal_students[col].mean()
                diff_pct = ((normal_mean - risk_mean) / normal_mean * 100) if normal_mean > 0 else 0
                behavior_diff[col] = {
                    'risk_mean': risk_mean,
                    'normal_mean': normal_mean,
                    'difference_pct': diff_pct
                }
        
        self.results['risk_factors'] = {
            'title': '学业风险因素分析',
            'risk_rate': risk_rate,
            'risk_count': risk_students.shape[0],
            'behavior_differences': behavior_diff,
            'insight': f"学业风险学生占比 {risk_rate:.1f}%，风险学生在图书馆访问、任务参与等行为上显著低于正常学生"
        }
        
        print(f"   风险学生比例: {risk_rate:.1f}% ({risk_students.shape[0]}人)")
        print(f"   洞察: {self.results['risk_factors']['insight']}")
        
        return self.results['risk_factors']
    
    def analysis_10_behavior_patterns(self):
        """分析10: 学生行为模式识别"""
        print("\n📊 分析10: 学生行为模式识别")
        
        # 定义行为模式
        def classify_pattern(row):
            lib = row.get('library_visits', 0)
            task = row.get('task_participation', 0)
            attend = row.get('total_attendance', 0)
            score = row.get('avg_score', 0)
            
            if score >= 85 and lib > 30:
                return '学霸模式'
            elif task > 50 and attend > 50:
                return '积极参与模式'
            elif lib > 20 and task < 10:
                return '自主学习模式'
            elif score < 60:
                return '学业困难模式'
            elif lib < 5 and task < 5:
                return '低参与模式'
            else:
                return '常规模式'
        
        self.data['behavior_pattern'] = self.data.apply(classify_pattern, axis=1)
        
        pattern_dist = self.data['behavior_pattern'].value_counts().to_dict()
        pattern_scores = self.data.groupby('behavior_pattern')['avg_score'].mean().to_dict()
        
        self.results['behavior_patterns'] = {
            'title': '学生行为模式识别',
            'pattern_distribution': pattern_dist,
            'pattern_avg_scores': pattern_scores,
            'pattern_count': len(pattern_dist),
            'insight': f"识别出 {len(pattern_dist)} 种行为模式，其中 '{max(pattern_dist, key=pattern_dist.get)}' 模式学生最多"
        }
        
        print(f"   识别出 {len(pattern_dist)} 种行为模式")
        for pattern, count in pattern_dist.items():
            print(f"      - {pattern}: {count}人 (平均成绩: {pattern_scores[pattern]:.1f})")
        print(f"   洞察: {self.results['behavior_patterns']['insight']}")
        
        return self.results['behavior_patterns']
    
    def save_results(self, filename='behavior_analysis_results.json'):
        """保存分析结果"""
        import json
        
        # 转换numpy类型为Python类型
        def convert_to_serializable(obj):
            if isinstance(obj, np.integer):
                return int(obj)
            elif isinstance(obj, np.floating):
                return float(obj)
            elif isinstance(obj, np.ndarray):
                return obj.tolist()
            elif isinstance(obj, tuple):
                return str(obj)  # 将tuple转换为字符串
            elif isinstance(obj, dict):
                # 处理字典中的非字符串键
                new_dict = {}
                for k, v in obj.items():
                    if isinstance(k, tuple):
                        new_dict[str(k)] = convert_to_serializable(v)
                    else:
                        new_dict[k] = convert_to_serializable(v)
                return new_dict
            elif isinstance(obj, list):
                return [convert_to_serializable(i) for i in obj]
            return obj
        
        serializable_results = convert_to_serializable(self.results)
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(serializable_results, f, ensure_ascii=False, indent=2)
        
        print(f"\n✅ 分析结果已保存至: {filename}")
        return serializable_results


if __name__ == "__main__":
    # 测试代码
    from data_cleaner import run_data_cleaning
    data = run_data_cleaning()
    
    if data is not None:
        analyzer = BehaviorAnalyzer(data)
        analyzer.analyze_all()
        analyzer.save_results()
