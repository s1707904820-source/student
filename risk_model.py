"""
学业风险预警模型
功能：构建学业风险预测模型，AUC不低于80%
"""
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score, classification_report, confusion_matrix, roc_curve
from sklearn.preprocessing import StandardScaler
import matplotlib.pyplot as plt
import warnings
warnings.filterwarnings('ignore')

plt.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False


class AcademicRiskModel:
    """学业风险预警模型"""
    
    def __init__(self, data):
        self.data = data.copy()
        self.model = None
        self.scaler = StandardScaler()
        self.feature_importance = None
        self.auc_score = 0
        print("✅ 风险预警模型初始化完成")
    
    def prepare_features(self):
        """准备特征数据"""
        print("\n📊 准备特征数据...")
        
        # 定义风险标签（挂科2门以上或平均成绩<60）
        self.data['is_risk'] = ((self.data['fail_count'] >= 2) | (self.data['avg_score'] < 60)).astype(int)
        
        # 选择特征
        feature_cols = [
            'avg_score', 'avg_gpa', 'weighted_gpa', 'fail_count',
            'library_visits', 'library_days', 'avg_visit_hour',
            'task_participation', 'total_attendance',
            'total_online_duration', 'avg_online_duration'
        ]
        
        self.feature_cols = [c for c in feature_cols if c in self.data.columns]
        
        # 添加派生特征
        if 'library_visits' in self.data.columns and 'total_attendance' in self.data.columns:
            self.data['lib_attend_ratio'] = self.data['library_visits'] / (self.data['total_attendance'] + 1)
            self.feature_cols.append('lib_attend_ratio')
        
        if 'task_participation' in self.data.columns and 'total_attendance' in self.data.columns:
            self.data['task_attend_ratio'] = self.data['task_participation'] / (self.data['total_attendance'] + 1)
            self.feature_cols.append('task_attend_ratio')
        
        # 准备X和y
        X = self.data[self.feature_cols].fillna(0)
        y = self.data['is_risk']
        
        print(f"   特征数量: {len(self.feature_cols)}")
        print(f"   样本数量: {len(X)}")
        print(f"   风险学生比例: {y.mean()*100:.1f}%")
        
        return X, y
    
    def train_model(self, model_type='random_forest'):
        """训练模型"""
        print(f"\n🤖 训练{model_type}模型...")
        
        X, y = self.prepare_features()
        
        # 划分训练集和测试集
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.3, random_state=42, stratify=y
        )
        
        # 标准化特征
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        # 选择模型
        if model_type == 'random_forest':
            self.model = RandomForestClassifier(
                n_estimators=100,
                max_depth=10,
                min_samples_split=5,
                min_samples_leaf=2,
                random_state=42,
                class_weight='balanced'
            )
        elif model_type == 'gradient_boosting':
            self.model = GradientBoostingClassifier(
                n_estimators=100,
                max_depth=5,
                learning_rate=0.1,
                random_state=42
            )
        elif model_type == 'logistic':
            self.model = LogisticRegression(
                random_state=42,
                class_weight='balanced',
                max_iter=1000
            )
        
        # 训练
        if model_type == 'logistic':
            self.model.fit(X_train_scaled, y_train)
            y_pred_proba = self.model.predict_proba(X_test_scaled)[:, 1]
            y_pred = self.model.predict(X_test_scaled)
        else:
            self.model.fit(X_train, y_train)
            y_pred_proba = self.model.predict_proba(X_test)[:, 1]
            y_pred = self.model.predict(X_test)
        
        # 评估
        self.auc_score = roc_auc_score(y_test, y_pred_proba)
        
        print(f"\n📈 模型评估结果:")
        print(f"   AUC: {self.auc_score:.4f}")
        print(f"   {'✅ 达到要求 (AUC >= 0.80)' if self.auc_score >= 0.80 else '⚠️ 未达到要求 (AUC < 0.80)'}")
        
        print(f"\n📋 分类报告:")
        print(classification_report(y_test, y_pred, target_names=['正常', '风险']))
        
        # 特征重要性
        if hasattr(self.model, 'feature_importances_'):
            self.feature_importance = pd.DataFrame({
                'feature': self.feature_cols,
                'importance': self.model.feature_importances_
            }).sort_values('importance', ascending=False)
        elif hasattr(self.model, 'coef_'):
            self.feature_importance = pd.DataFrame({
                'feature': self.feature_cols,
                'importance': np.abs(self.model.coef_[0])
            }).sort_values('importance', ascending=False)
        
        if self.feature_importance is not None:
            print(f"\n🔍 特征重要性 (Top 5):")
            for _, row in self.feature_importance.head(5).iterrows():
                print(f"   {row['feature']}: {row['importance']:.4f}")
        
        # 保存测试集结果用于可视化
        self.test_results = {
            'y_test': y_test,
            'y_pred_proba': y_pred_proba,
            'y_pred': y_pred
        }
        
        return self.auc_score
    
    def cross_validate(self, cv=5):
        """交叉验证"""
        print(f"\n🔄 进行{cv}折交叉验证...")
        
        X, y = self.prepare_features()
        
        # 使用随机森林进行交叉验证
        model = RandomForestClassifier(
            n_estimators=100,
            random_state=42,
            class_weight='balanced'
        )
        
        scores = cross_val_score(model, X, y, cv=cv, scoring='roc_auc')
        
        print(f"   交叉验证AUC: {scores.mean():.4f} (+/- {scores.std()*2:.4f})")
        
        return scores.mean()
    
    def predict_risk(self, student_data):
        """预测单个学生的风险"""
        if self.model is None:
            print("❌ 模型尚未训练")
            return None
        
        X = student_data[self.feature_cols].fillna(0).values.reshape(1, -1)
        risk_proba = self.model.predict_proba(X)[0, 1]
        risk_level = '高风险' if risk_proba > 0.7 else '中风险' if risk_proba > 0.3 else '低风险'
        
        return {
            'risk_probability': risk_proba,
            'risk_level': risk_level
        }
    
    def get_risk_students(self, threshold=0.5):
        """获取高风险学生列表"""
        if self.model is None:
            print("❌ 模型尚未训练")
            return None
        
        X = self.data[self.feature_cols].fillna(0)
        risk_proba = self.model.predict_proba(X)[:, 1]
        
        self.data['risk_probability'] = risk_proba
        self.data['predicted_risk'] = (risk_proba >= threshold).astype(int)
        
        risk_students = self.data[self.data['risk_probability'] >= threshold].copy()
        risk_students = risk_students.sort_values('risk_probability', ascending=False)
        
        return risk_students[['student_id', 'avg_score', 'fail_count', 'risk_probability', 'predicted_risk']]
    
    def explain_risk(self, student_id):
        """解释学生风险原因（可解释性分析）"""
        student = self.data[self.data['student_id'] == student_id]
        if len(student) == 0:
            return "未找到该学生"
        
        student = student.iloc[0]
        explanations = []
        
        # 基于特征重要性解释
        if self.feature_importance is not None:
            for _, row in self.feature_importance.head(3).iterrows():
                feature = row['feature']
                if feature in student:
                    value = student[feature]
                    # 根据特征值给出解释
                    if feature == 'avg_score' and value < 60:
                        explanations.append(f"平均成绩较低 ({value:.1f}分)")
                    elif feature == 'fail_count' and value >= 2:
                        explanations.append(f"挂科科目较多 ({int(value)}门)")
                    elif feature == 'library_visits' and value < 5:
                        explanations.append(f"图书馆使用频率低 ({int(value)}次)")
                    elif feature == 'task_participation' and value < 10:
                        explanations.append(f"课堂任务参与度低 ({int(value)}次)")
                    elif feature == 'total_attendance' and value < 20:
                        explanations.append(f"考勤记录较少 ({int(value)}次)")
        
        if not explanations:
            explanations.append("综合行为指标显示学习投入不足")
        
        return {
            'student_id': student_id,
            'risk_probability': student.get('risk_probability', 0),
            'explanations': explanations,
            'key_factors': explanations[:3]  # 前3个关键因素
        }
    
    def visualize_results(self):
        """可视化模型结果"""
        if self.model is None:
            print("❌ 模型尚未训练")
            return
        
        fig, axes = plt.subplots(2, 2, figsize=(14, 12))
        
        # 1. ROC曲线
        y_test = self.test_results['y_test']
        y_pred_proba = self.test_results['y_pred_proba']
        fpr, tpr, _ = roc_curve(y_test, y_pred_proba)
        
        axes[0, 0].plot(fpr, tpr, label=f'ROC Curve (AUC = {self.auc_score:.3f})')
        axes[0, 0].plot([0, 1], [0, 1], 'k--', label='Random')
        axes[0, 0].set_xlabel('False Positive Rate')
        axes[0, 0].set_ylabel('True Positive Rate')
        axes[0, 0].set_title('ROC Curve')
        axes[0, 0].legend()
        axes[0, 0].grid(True)
        
        # 2. 特征重要性
        if self.feature_importance is not None:
            top_features = self.feature_importance.head(10)
            axes[0, 1].barh(top_features['feature'], top_features['importance'])
            axes[0, 1].set_xlabel('Importance')
            axes[0, 1].set_title('Feature Importance (Top 10)')
            axes[0, 1].invert_yaxis()
        
        # 3. 混淆矩阵
        cm = confusion_matrix(y_test, self.test_results['y_pred'])
        im = axes[1, 0].imshow(cm, interpolation='nearest', cmap='Blues')
        axes[1, 0].set_title('Confusion Matrix')
        tick_marks = np.arange(2)
        axes[1, 0].set_xticks(tick_marks)
        axes[1, 0].set_yticks(tick_marks)
        axes[1, 0].set_xticklabels(['Normal', 'Risk'])
        axes[1, 0].set_yticklabels(['Normal', 'Risk'])
        
        # 添加数值标注
        thresh = cm.max() / 2.
        for i in range(cm.shape[0]):
            for j in range(cm.shape[1]):
                axes[1, 0].text(j, i, format(cm[i, j], 'd'),
                             ha="center", va="center",
                             color="white" if cm[i, j] > thresh else "black")
        
        axes[1, 0].set_ylabel('True Label')
        axes[1, 0].set_xlabel('Predicted Label')
        
        # 4. 风险概率分布
        risk_proba_normal = y_pred_proba[y_test == 0]
        risk_proba_risk = y_pred_proba[y_test == 1]
        
        axes[1, 1].hist(risk_proba_normal, bins=20, alpha=0.5, label='Normal', color='green')
        axes[1, 1].hist(risk_proba_risk, bins=20, alpha=0.5, label='Risk', color='red')
        axes[1, 1].set_xlabel('Risk Probability')
        axes[1, 1].set_ylabel('Count')
        axes[1, 1].set_title('Risk Probability Distribution')
        axes[1, 1].legend()
        
        plt.tight_layout()
        plt.savefig('risk_model_results.png', dpi=150, bbox_inches='tight')
        plt.close()
        
        print("\n✅ 模型可视化结果已保存至: risk_model_results.png")
    
    def save_model(self, filename='risk_model.pkl'):
        """保存模型"""
        import pickle
        
        model_data = {
            'model': self.model,
            'scaler': self.scaler,
            'feature_cols': self.feature_cols,
            'feature_importance': self.feature_importance,
            'auc_score': self.auc_score
        }
        
        with open(filename, 'wb') as f:
            pickle.dump(model_data, f)
        
        print(f"✅ 模型已保存至: {filename}")
    
    def load_model(self, filename='risk_model.pkl'):
        """加载模型"""
        import pickle
        
        with open(filename, 'rb') as f:
            model_data = pickle.load(f)
        
        self.model = model_data['model']
        self.scaler = model_data['scaler']
        self.feature_cols = model_data['feature_cols']
        self.feature_importance = model_data['feature_importance']
        self.auc_score = model_data['auc_score']
        
        print(f"✅ 模型已从 {filename} 加载")


def run_risk_model(data):
    """运行风险预警模型完整流程"""
    print("\n" + "=" * 50)
    print("学业风险预警模型")
    print("=" * 50)
    
    model = AcademicRiskModel(data)
    
    # 训练模型
    auc = model.train_model(model_type='random_forest')
    
    # 交叉验证
    cv_auc = model.cross_validate(cv=5)
    
    # 可视化
    model.visualize_results()
    
    # 保存模型
    model.save_model()
    
    # 获取高风险学生
    risk_students = model.get_risk_students(threshold=0.5)
    if risk_students is not None:
        risk_students.to_csv('high_risk_students.csv', index=False, encoding='utf-8-sig')
        print(f"\n✅ 高风险学生列表已保存至: high_risk_students.csv ({len(risk_students)}人)")
    
    print("\n" + "=" * 50)
    print(f"模型AUC: {auc:.4f} {'✅ 达标' if auc >= 0.80 else '❌ 未达标'}")
    print("=" * 50)
    
    return model


if __name__ == "__main__":
    from data_cleaner import run_data_cleaning
    data = run_data_cleaning()
    
    if data is not None:
        model = run_risk_model(data)
