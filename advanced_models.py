# -*- coding: utf-8 -*-
"""
Advanced Analysis Models Module
Features:
1. KMeans Student Clustering (4 types: High Performer, Overworker, Slacker, Underperformer)
2. XGBoost Academic Risk Prediction (AUC>0.8)
3. SHAP Explainability Analysis
4. Generate 5 Required Charts for Competition
"""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import roc_auc_score, roc_curve
from sklearn.ensemble import GradientBoostingClassifier
import warnings
warnings.filterwarnings('ignore')

plt.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

# Try importing XGBoost and SHAP
try:
    import xgboost as xgb
    XGBOOST_AVAILABLE = True
except ImportError:
    XGBOOST_AVAILABLE = False
    print("[!] XGBoost not installed, using GradientBoosting instead")

try:
    import shap
    SHAP_AVAILABLE = True
except ImportError:
    SHAP_AVAILABLE = False
    print("[!] SHAP not installed, using feature importance instead")


class StudentClustering:
    """Student Clustering Model - KMeans"""
    
    def __init__(self, data):
        self.data = data.copy()
        self.kmeans = None
        self.scaler = StandardScaler()
        self.cluster_labels = None
        print("[OK] Student clustering model initialized")
    
    def prepare_features(self):
        """Prepare clustering features"""
        print("\n[DATA] Preparing clustering features...")
        
        features = []
        
        # Study time
        if 'total_online_duration' in self.data.columns:
            self.data['study_time'] = self.data['total_online_duration'] / 60
            features.append('study_time')
        
        # Assignment count
        if 'task_participation' in self.data.columns:
            self.data['assignment_count'] = self.data['task_participation']
            features.append('assignment_count')
        
        # Library visits
        if 'library_visits' in self.data.columns:
            self.data['library_count'] = self.data['library_visits']
            features.append('library_count')
        
        # Average score
        if 'avg_score' in self.data.columns:
            self.data['score_avg'] = self.data['avg_score']
            features.append('score_avg')
        
        # Attendance
        if 'total_attendance' in self.data.columns:
            self.data['attendance'] = self.data['total_attendance']
            features.append('attendance')
        
        X = self.data[features].fillna(0)
        
        print(f"   Clustering features: {features}")
        print(f"   Sample count: {len(X)}")
        
        return X, features
    
    def fit(self, n_clusters=4):
        """Execute KMeans clustering"""
        print(f"\n[TARGET] Executing KMeans clustering (k={n_clusters})...")
        
        X, features = self.prepare_features()
        
        # Standardize features
        X_scaled = self.scaler.fit_transform(X)
        
        # KMeans clustering
        self.kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
        self.cluster_labels = self.kmeans.fit_predict(X_scaled)
        
        # Add cluster labels to data
        self.data['cluster'] = self.cluster_labels
        
        # Analyze clusters
        cluster_analysis = self.analyze_clusters()
        
        print(f"\n[OK] Clustering completed!")
        return cluster_analysis
    
    def analyze_clusters(self):
        """Analyze clustering results and name clusters"""
        print("\n[CHART] Analyzing cluster characteristics...")
        
        # Calculate average features for each cluster
        cluster_features = self.data.groupby('cluster').agg({
            'study_time': 'mean',
            'assignment_count': 'mean',
            'library_count': 'mean',
            'score_avg': 'mean',
            'attendance': 'mean'
        }).round(2)
        
        # Count students in each cluster
        cluster_counts = self.data['cluster'].value_counts().sort_index()
        cluster_features['student_count'] = cluster_counts
        
        # Name clusters based on characteristics
        cluster_names = {}
        for cluster_id in range(len(cluster_features)):
            row = cluster_features.loc[cluster_id]
            
            # Determine behavior activity
            high_behavior = row['study_time'] > cluster_features['study_time'].median() and \
                          row['library_count'] > cluster_features['library_count'].median()
            
            # Determine score level
            high_score = row['score_avg'] > cluster_features['score_avg'].median()
            
            if high_behavior and high_score:
                name = "High Performer"
                desc = "High behavior + High score"
            elif high_behavior and not high_score:
                name = "Overworker"
                desc = "High behavior + Low score"
            elif not high_behavior and high_score:
                name = "Slacker"
                desc = "Low behavior + High score"
            else:
                name = "Underperformer"
                desc = "Low behavior + Low score"
            
            cluster_names[cluster_id] = {'name': name, 'desc': desc}
        
        self.cluster_names = cluster_names
        
        # Print clustering results
        print("\n" + "=" * 60)
        print("Clustering Results Analysis")
        print("=" * 60)
        for cluster_id, info in cluster_names.items():
            count = cluster_counts[cluster_id]
            pct = count / len(self.data) * 100
            print(f"\n[{info['name']}] - {info['desc']}")
            print(f"   Student count: {count} ({pct:.1f}%)")
            print(f"   Avg score: {cluster_features.loc[cluster_id, 'score_avg']:.1f}")
            print(f"   Daily study: {cluster_features.loc[cluster_id, 'study_time']:.1f} hours")
            print(f"   Library visits: {cluster_features.loc[cluster_id, 'library_count']:.0f}")
        
        return {
            'cluster_features': cluster_features,
            'cluster_names': cluster_names,
            'cluster_counts': cluster_counts.to_dict()
        }
    
    def plot_clusters(self, save_path='cluster_plot.png'):
        """Generate clustering scatter plot"""
        print("\n[DATA] Generating clustering scatter plot...")
        
        fig, axes = plt.subplots(1, 2, figsize=(16, 6))
        
        # Plot 1: Study behavior vs Score
        colors = ['#00d9ff', '#ff6692', '#00ff88', '#ffaa00']
        for i, cluster_id in enumerate(sorted(self.data['cluster'].unique())):
            mask = self.data['cluster'] == cluster_id
            name = self.cluster_names[cluster_id]['name']
            axes[0].scatter(
                self.data.loc[mask, 'study_time'],
                self.data.loc[mask, 'score_avg'],
                c=colors[i % len(colors)],
                label=f'{name} (Cluster {cluster_id})',
                alpha=0.6,
                s=50
            )
        
        axes[0].set_xlabel('Daily Study Time (hours)', fontsize=12)
        axes[0].set_ylabel('Average Score', fontsize=12)
        axes[0].set_title('Student Clustering: Study Behavior vs Score', fontsize=14, fontweight='bold')
        axes[0].legend()
        axes[0].grid(True, alpha=0.3)
        
        # Plot 2: Library visits vs Score
        for i, cluster_id in enumerate(sorted(self.data['cluster'].unique())):
            mask = self.data['cluster'] == cluster_id
            name = self.cluster_names[cluster_id]['name']
            axes[1].scatter(
                self.data.loc[mask, 'library_count'],
                self.data.loc[mask, 'score_avg'],
                c=colors[i % len(colors)],
                label=f'{name} (Cluster {cluster_id})',
                alpha=0.6,
                s=50
            )
        
        axes[1].set_xlabel('Library Visits', fontsize=12)
        axes[1].set_ylabel('Average Score', fontsize=12)
        axes[1].set_title('Student Clustering: Library Behavior vs Score', fontsize=14, fontweight='bold')
        axes[1].legend()
        axes[1].grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"[OK] Clustering plot saved: {save_path}")
        plt.close()


class LogisticRiskModel:
    """Logistic Regression Academic Risk Prediction Model
    
    与Word文档一致，使用逻辑回归模型：
    P(y=1|x) = 1 / (1 + e^-(β₀ + β₁x₁ + ... + βₙxₙ))
    """
    
    def __init__(self, data):
        self.data = data.copy()
        self.model = None
        self.scaler = StandardScaler()
        self.auc_score = 0
        self.feature_importance = None
        self.coefficients = None  # 逻辑回归系数
        print("[OK] Logistic Regression risk model initialized")
    
    def prepare_features(self):
        """Prepare feature data - 与Word文档特征命名一致"""
        print("\n[DATA] Preparing risk prediction features...")
        
        # Define risk labels - 与文档一致：以成绩为参考标准
        self.data['is_risk'] = ((self.data['fail_count'] >= 2) | (self.data['avg_score'] < 60)).astype(int)
        
        # Select features - 使用Word文档中的标准特征名
        feature_cols = []
        
        # 学习时长 (online_time) - 对应 total_online_duration
        if 'total_online_duration' in self.data.columns:
            self.data['online_time'] = self.data['total_online_duration'] / 60  # 转换为小时
            feature_cols.append('online_time')
        
        # 作业提交次数 (assignment_count) - 对应 task_participation
        if 'task_participation' in self.data.columns:
            self.data['assignment_count'] = self.data['task_participation']
            feature_cols.append('assignment_count')
        
        # 出勤率 (attendance) - 对应 total_attendance
        if 'total_attendance' in self.data.columns:
            self.data['attendance'] = self.data['total_attendance']
            feature_cols.append('attendance')
        
        # 图书馆使用情况 (library_count) - 对应 library_visits
        if 'library_visits' in self.data.columns:
            self.data['library_count'] = self.data['library_visits']
            feature_cols.append('library_count')
        
        # 平均成绩 (score_avg)
        if 'avg_score' in self.data.columns:
            self.data['score_avg'] = self.data['avg_score']
            feature_cols.append('score_avg')
        
        # 额外特征（如果有）
        if 'avg_gpa' in self.data.columns:
            feature_cols.append('avg_gpa')
        if 'fail_count' in self.data.columns:
            feature_cols.append('fail_count')
        
        self.feature_cols = feature_cols
        
        # Prepare X and y
        X = self.data[self.feature_cols].fillna(0)
        y = self.data['is_risk']
        
        print(f"   Feature count: {len(self.feature_cols)}")
        print(f"   Sample count: {len(X)}")
        print(f"   Risk student ratio: {y.mean()*100:.1f}%")
        
        return X, y
    
    def train(self):
        """Train Logistic Regression model"""
        from sklearn.linear_model import LogisticRegression
        
        print("\n[MODEL] Training Logistic Regression risk prediction model...")
        print("   Model formula: P(y=1|x) = 1 / (1 + e^-(β₀ + β₁x₁ + ... + βₙxₙ))")
        
        X, y = self.prepare_features()
        
        # Split train/test
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.3, random_state=42, stratify=y
        )
        
        # Standardize features (important for logistic regression)
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        # Train Logistic Regression model - 与Word文档一致
        self.model = LogisticRegression(
            random_state=42,
            max_iter=1000,
            C=1.0,  # 正则化强度
            solver='lbfgs'
        )
        
        self.model.fit(X_train_scaled, y_train)
        
        # Get coefficients (β values)
        self.coefficients = dict(zip(self.feature_cols, self.model.coef_[0]))
        self.intercept = self.model.intercept_[0]
        
        # Predict probabilities
        y_pred_proba = self.model.predict_proba(X_test_scaled)[:, 1]
        y_pred = self.model.predict(X_test_scaled)
        
        # Calculate AUC
        self.auc_score = roc_auc_score(y_test, y_pred_proba)
        
        print(f"\n[OK] Model training completed!")
        print(f"   AUC Score: {self.auc_score:.4f}")
        print(f"   Accuracy: {(y_pred == y_test).mean():.4f}")
        print(f"\n   Model Coefficients (β values):")
        print(f"   Intercept (β₀): {self.intercept:.4f}")
        for feature, coef in self.coefficients.items():
            print(f"   {feature} (β): {coef:.4f}")
        
        # Save test data for later analysis
        self.X_test = X_test
        self.y_test = y_test
        self.y_pred_proba = y_pred_proba
        
        return {
            'auc': self.auc_score,
            'X_test': X_test,
            'y_test': y_test,
            'y_pred_proba': y_pred_proba,
            'coefficients': self.coefficients,
            'intercept': self.intercept
        }
    
    def plot_roc_curve(self, save_path='roc_curve.png'):
        """Plot ROC curve"""
        print("\n[DATA] Generating ROC curve...")
        
        fpr, tpr, _ = roc_curve(self.y_test, self.y_pred_proba)
        
        plt.figure(figsize=(8, 6))
        plt.plot(fpr, tpr, color='#00d9ff', lw=2, 
                label=f'ROC Curve (AUC = {self.auc_score:.4f})')
        plt.plot([0, 1], [0, 1], color='gray', lw=1, linestyle='--', label='Random Guess')
        
        plt.xlim([0.0, 1.0])
        plt.ylim([0.0, 1.05])
        plt.xlabel('False Positive Rate', fontsize=12)
        plt.ylabel('True Positive Rate', fontsize=12)
        plt.title('XGBoost Risk Prediction Model - ROC Curve', fontsize=14, fontweight='bold')
        plt.legend(loc='lower right')
        plt.grid(True, alpha=0.3)
        
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"[OK] ROC curve saved: {save_path}")
        plt.close()
    
    def plot_feature_importance(self, save_path='feature_importance.png'):
        """Plot feature importance"""
        print("\n[DATA] Generating feature importance plot...")
        
        # Get feature importance
        importance = self.model.feature_importances_
        feature_importance = pd.DataFrame({
            'feature': self.feature_cols,
            'importance': importance
        }).sort_values('importance', ascending=True)
        
        # Plot horizontal bar chart
        plt.figure(figsize=(10, 8))
        colors = plt.cm.viridis(np.linspace(0, 1, len(feature_importance)))
        plt.barh(feature_importance['feature'], feature_importance['importance'], color=colors)
        
        plt.xlabel('Importance Score', fontsize=12)
        plt.ylabel('Feature', fontsize=12)
        plt.title('XGBoost Model - Feature Importance Analysis', fontsize=14, fontweight='bold')
        plt.grid(True, alpha=0.3, axis='x')
        
        plt.tight_layout()
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"[OK] Feature importance plot saved: {save_path}")
        plt.close()
        
        # Print Top5 features
        print("\n[SEARCH] Top 5 Important Features:")
        top5 = feature_importance.tail(5)
        for idx, row in top5.iterrows():
            print(f"   {row['feature']}: {row['importance']:.4f}")
    
    def shap_analysis(self, save_path='shap_plot.png'):
        """SHAP explainability analysis"""
        if not SHAP_AVAILABLE:
            print("[WARN] SHAP not installed, skipping SHAP analysis")
            return None
        
        print("\n[DATA] Executing SHAP explainability analysis...")
        
        # Prepare data
        X_sample = self.X_test.sample(min(100, len(self.X_test)), random_state=42)
        X_sample_scaled = self.scaler.transform(X_sample)
        
        # Create SHAP explainer
        explainer = shap.TreeExplainer(self.model)
        shap_values = explainer.shap_values(X_sample_scaled)
        
        # Plot SHAP summary
        plt.figure(figsize=(10, 8))
        shap.summary_plot(shap_values, X_sample_scaled, feature_names=self.feature_cols, 
                         show=False, plot_size=(10, 8))
        plt.title('SHAP Feature Impact Analysis', fontsize=14, fontweight='bold')
        plt.tight_layout()
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"[OK] SHAP plot saved: {save_path}")
        plt.close()


def generate_all_plots(data):
    """Generate 5 required charts for competition"""
    print("\n" + "=" * 60)
    print("Generating 5 Required Charts")
    print("=" * 60)
    
    # 1. Clustering scatter plot
    print("\n[1/5] Generating clustering scatter plot...")
    clustering = StudentClustering(data)
    clustering.fit(n_clusters=4)
    clustering.plot_clusters('chart_1_clustering.png')
    
    # 2. ROC curve
    print("\n[2/5] Generating ROC curve...")
    risk_model = XGBoostRiskModel(data)
    risk_model.train()
    risk_model.plot_roc_curve('chart_2_roc_curve.png')
    
    # 3. Risk distribution
    print("\n[3/5] Generating risk distribution plot...")
    plot_risk_distribution(data, 'chart_3_risk_distribution.png')
    
    # 4. Feature importance
    print("\n[4/5] Generating feature importance plot...")
    risk_model.plot_feature_importance('chart_4_feature_importance.png')
    
    # 5. SHAP plot (if available)
    print("\n[5/5] Generating SHAP explainability plot...")
    if SHAP_AVAILABLE:
        risk_model.shap_analysis('chart_5_shap.png')
    else:
        print("   SHAP not installed, generating alternative plot...")
        plot_student_profile(data, 'chart_5_student_profile.png')
    
    print("\n[OK] All 5 charts generated!")
    return {
        'clustering': clustering,
        'risk_model': risk_model
    }


def plot_risk_distribution(data, save_path='risk_distribution.png'):
    """Plot risk distribution"""
    data['is_risk'] = ((data['fail_count'] >= 2) | (data['avg_score'] < 60)).astype(int)
    
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    
    # Left: Risk student distribution (pie chart)
    risk_counts = data['is_risk'].value_counts()
    labels = ['Normal', 'At Risk']
    colors = ['#00ff88', '#ff6692']
    axes[0].pie(risk_counts.values, labels=labels, autopct='%1.1f%%', 
               colors=colors, startangle=90, textprops={'fontsize': 12})
    axes[0].set_title('Academic Risk Student Distribution', fontsize=14, fontweight='bold')
    
    # Right: Risk rate by college (bar chart)
    if 'college' in data.columns:
        college_risk = data.groupby('college')['is_risk'].mean().sort_values(ascending=True)
        colors_bar = ['#ff6692' if x > 0.5 else '#ffaa00' if x > 0.3 else '#00ff88' for x in college_risk.values]
        axes[1].barh(college_risk.index, college_risk.values * 100, color=colors_bar)
        axes[1].set_xlabel('Risk Rate (%)', fontsize=12)
        axes[1].set_title('Academic Risk Rate by College', fontsize=14, fontweight='bold')
        axes[1].grid(True, alpha=0.3, axis='x')
    
    plt.tight_layout()
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    print(f"[OK] Risk distribution plot saved: {save_path}")
    plt.close()


def plot_student_profile(data, save_path='student_profile.png'):
    """Plot student profile"""
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    
    # Plot 1: Score distribution
    axes[0, 0].hist(data['avg_score'], bins=20, color='#00d9ff', alpha=0.7, edgecolor='white')
    axes[0, 0].axvline(data['avg_score'].mean(), color='#ff6692', linestyle='--', 
                      linewidth=2, label=f'Mean: {data["avg_score"].mean():.1f}')
    axes[0, 0].set_xlabel('Average Score', fontsize=11)
    axes[0, 0].set_ylabel('Student Count', fontsize=11)
    axes[0, 0].set_title('Score Distribution Histogram', fontsize=12, fontweight='bold')
    axes[0, 0].legend()
    axes[0, 0].grid(True, alpha=0.3)
    
    # Plot 2: Library visit distribution
    if 'library_visits' in data.columns:
        axes[0, 1].hist(data['library_visits'], bins=20, color='#00ff88', alpha=0.7, edgecolor='white')
        axes[0, 1].axvline(data['library_visits'].mean(), color='#ff6692', linestyle='--',
                          linewidth=2, label=f'Mean: {data["library_visits"].mean():.0f}')
        axes[0, 1].set_xlabel('Library Visits', fontsize=11)
        axes[0, 1].set_ylabel('Student Count', fontsize=11)
        axes[0, 1].set_title('Library Visit Distribution', fontsize=12, fontweight='bold')
        axes[0, 1].legend()
        axes[0, 1].grid(True, alpha=0.3)
    
    # Plot 3: Gender vs Score
    if 'gender' in data.columns:
        gender_score = data.groupby('gender')['avg_score'].mean()
        colors = ['#00d9ff', '#ff6692']
        axes[1, 0].bar(gender_score.index, gender_score.values, color=colors, alpha=0.8)
        axes[1, 0].set_ylabel('Average Score', fontsize=11)
        axes[1, 0].set_title('Gender vs Average Score', fontsize=12, fontweight='bold')
        axes[1, 0].grid(True, alpha=0.3, axis='y')
    
    # Plot 4: Study duration vs Score scatter
    if 'total_online_duration' in data.columns:
        study_hours = data['total_online_duration'] / 60
        axes[1, 1].scatter(study_hours, data['avg_score'], alpha=0.5, c='#00d9ff', s=20)
        axes[1, 1].set_xlabel('Daily Study Duration (hours)', fontsize=11)
        axes[1, 1].set_ylabel('Average Score', fontsize=11)
        axes[1, 1].set_title('Study Duration vs Score', fontsize=12, fontweight='bold')
        axes[1, 1].grid(True, alpha=0.3)
    
    plt.suptitle('Student Profile Comprehensive Analysis', fontsize=16, fontweight='bold', y=1.02)
    plt.tight_layout()
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    print(f"[OK] Student profile plot saved: {save_path}")
    plt.close()


if __name__ == "__main__":
    # Load data
    print("Loading data...")
    data = pd.read_csv('cleaned_data.csv', encoding='utf-8-sig')
    
    # Generate all charts
    results = generate_all_plots(data)
    
    print("\n" + "=" * 60)
    print("Analysis Complete! Generated files:")
    print("=" * 60)
    print("1. chart_1_clustering.png - Clustering scatter plot")
    print("2. chart_2_roc_curve.png - ROC curve")
    print("3. chart_3_risk_distribution.png - Risk distribution")
    print("4. chart_4_feature_importance.png - Feature importance")
    print("5. chart_5_shap.png / chart_5_student_profile.png - SHAP/Profile")
