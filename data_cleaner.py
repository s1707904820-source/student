# -*- coding: utf-8 -*-
"""
数据清洗与标准化模块
功能：统一学生标识、过滤脏数据、标准化数据格式
"""
import pandas as pd
import numpy as np
import os
import sys

# 设置编码
sys.stdout.reconfigure(encoding='utf-8')

DATA_DIR = "数据集及类型"

def load_data(file_name):
    """加载数据文件"""
    try:
        file_path = os.path.join(DATA_DIR, file_name)
        df = pd.read_excel(file_path)
        print(f"[OK] 成功加载: {file_name} ({len(df)} 条记录)")
        return df
    except Exception as e:
        print(f"[ERROR] 加载失败: {file_name} - {str(e)}")
        return None

def clean_student_info(df):
    """清洗学生基本信息"""
    if df is None:
        return None
    
    # 统一学号字段
    df = df.rename(columns={'XH': 'student_id'})
    df['student_id'] = df['student_id'].astype(str).str.strip()
    
    # 标准化性别字段
    df['XB'] = df['XB'].astype(str).str.strip()
    df['gender'] = df['XB'].map({'男': '男', '女': '女'}).fillna('未知')
    
    # 提取出生年份
    df['birth_year'] = pd.to_numeric(df['CSRQ'].astype(str).str[:4], errors='coerce')
    df['age'] = 2024 - df['birth_year']
    
    # 标准化籍贯（取省份代码前两位）
    df['province_code'] = df['JG'].astype(str).str[:2]
    
    # 保留关键字段
    keep_cols = ['student_id', 'gender', 'age', 'province_code', 'XSM', 'ZYM']
    df = df[keep_cols].copy()
    df.columns = ['student_id', 'gender', 'age', 'province', 'college', 'major']
    
    print(f"[OK] 学生信息清洗完成: {len(df)} 条有效记录")
    return df

def clean_scores(df):
    """清洗学生成绩数据"""
    if df is None:
        return None
    
    # 统一学号字段
    df = df.rename(columns={'XH': 'student_id'})
    df['student_id'] = df['student_id'].astype(str).str.strip()
    
    # 识别成绩列（KCCJ）
    df['score'] = pd.to_numeric(df['KCCJ'], errors='coerce')
    df['credit'] = pd.to_numeric(df['XF'], errors='coerce')
    
    # 计算绩点（标准4.0制）
    def score_to_gpa(score):
        if pd.isna(score):
            return np.nan
        if score >= 90:
            return 4.0
        elif score >= 85:
            return 3.7
        elif score >= 82:
            return 3.3
        elif score >= 78:
            return 3.0
        elif score >= 75:
            return 2.7
        elif score >= 72:
            return 2.3
        elif score >= 68:
            return 2.0
        elif score >= 64:
            return 1.5
        elif score >= 60:
            return 1.0
        else:
            return 0.0
    
    df['gpa'] = df['score'].apply(score_to_gpa)
    df['is_fail'] = df['score'] < 60
    
    # 按学生汇总成绩
    score_summary = df.groupby('student_id').agg(
        total_courses=('score', 'count'),
        avg_score=('score', 'mean'),
        weighted_avg_score=('score', lambda x: np.average(x, weights=df.loc[x.index, 'credit'].fillna(1))),
        avg_gpa=('gpa', 'mean'),
        weighted_gpa=('gpa', lambda x: np.average(x, weights=df.loc[x.index, 'credit'].fillna(1))),
        fail_count=('is_fail', 'sum'),
        total_credits=('credit', 'sum')
    ).reset_index()
    
    print(f"[OK] 成绩数据清洗完成: {len(score_summary)} 名学生")
    return score_summary

def clean_library(df):
    """清洗图书馆打卡记录"""
    if df is None:
        return None
    
    # 统一学号字段 - 图书馆数据使用cardld作为学号
    if 'cardld' in df.columns:
        df = df.rename(columns={'cardld': 'student_id'})
    elif 'XH' in df.columns:
        df = df.rename(columns={'XH': 'student_id'})
    
    df['student_id'] = df['student_id'].astype(str).str.strip()
    
    # 解析时间字段
    if 'visittime' in df.columns:
        df['check_time'] = pd.to_datetime(df['visittime'], errors='coerce')
        df['date'] = df['check_time'].dt.date
        df['hour'] = df['check_time'].dt.hour
    elif 'DZSJ' in df.columns:
        df['check_time'] = pd.to_datetime(df['DZSJ'], errors='coerce')
        df['date'] = df['check_time'].dt.date
        df['hour'] = df['check_time'].dt.hour
    
    # 统计图书馆行为
    lib_summary = df.groupby('student_id').agg(
        library_visits=('student_id', 'count'),
        library_days=('date', 'nunique'),
        avg_visit_hour=('hour', 'mean')
    ).reset_index()
    
    print(f"[OK] 图书馆数据清洗完成: {len(lib_summary)} 名学生")
    return lib_summary

def clean_internet(df):
    """清洗上网统计数据"""
    if df is None:
        return None
    
    # 统一学号字段
    if 'XSBH' in df.columns:
        df = df.rename(columns={'XSBH': 'student_id'})
    df['student_id'] = df['student_id'].astype(str).str.strip()
    
    # 查找上网时长列
    duration_col = None
    for col in df.columns:
        if '时长' in str(col) or 'SC' in str(col):
            duration_col = col
            break
    
    if duration_col:
        df['online_duration'] = pd.to_numeric(df[duration_col], errors='coerce')
        
        # 统计上网行为
        net_summary = df.groupby('student_id').agg(
            total_online_duration=('online_duration', 'sum'),
            avg_online_duration=('online_duration', 'mean'),
            online_records=('student_id', 'count')
        ).reset_index()
        
        print(f"[OK] 上网数据清洗完成: {len(net_summary)} 名学生")
        return net_summary
    
    return None

def clean_attendance(df):
    """清洗考勤数据"""
    if df is None:
        return None
    
    # 统一学号字段
    if 'XH' in df.columns:
        df = df.rename(columns={'XH': 'student_id'})
    df['student_id'] = df['student_id'].astype(str).str.strip()
    
    # 统计考勤
    attend_summary = df.groupby('student_id').agg(
        total_attendance=('student_id', 'count')
    ).reset_index()
    
    print(f"[OK] 考勤数据清洗完成: {len(attend_summary)} 名学生")
    return attend_summary

def clean_tasks(df):
    """清洗课堂任务参与数据"""
    if df is None:
        return None
    
    # 统一学号字段
    if 'USER_ID' in df.columns:
        df = df.rename(columns={'USER_ID': 'student_id'})
    df['student_id'] = df['student_id'].astype(str).str.strip()
    
    # 统计任务参与
    task_summary = df.groupby('student_id').agg(
        task_participation=('student_id', 'count')
    ).reset_index()
    
    print(f"[OK] 任务参与数据清洗完成: {len(task_summary)} 名学生")
    return task_summary

def merge_all_data(datasets):
    """合并所有清洗后的数据"""
    # 以学生信息为基础
    base = datasets.get('info')
    if base is None:
        print("[ERROR] 缺少学生基本信息，无法合并")
        return None
    
    result = base.copy()
    
    # 依次合并其他数据
    merge_order = ['scores', 'library', 'internet', 'attendance', 'tasks']
    for key in merge_order:
        if key in datasets and datasets[key] is not None:
            result = result.merge(datasets[key], on='student_id', how='left')
            print(f"[OK] 已合并 {key} 数据")
    
    # 填充缺失值
    numeric_cols = result.select_dtypes(include=[np.number]).columns
    result[numeric_cols] = result[numeric_cols].fillna(0)
    
    print(f"\n[OK] 数据合并完成: 共 {len(result)} 名学生，{len(result.columns)} 个特征")
    return result

def run_data_cleaning():
    """执行完整的数据清洗流程"""
    print("=" * 50)
    print("开始数据清洗与标准化")
    print("=" * 50)
    
    # 加载原始数据
    raw_data = {
        'info': load_data("学生基本信息.xlsx"),
        'scores': load_data("学生成绩.xlsx"),
        'library': load_data("图书馆打卡记录.xlsx"),
        'internet': load_data("上网统计.xlsx"),
        'attendance': load_data("考勤汇总.xlsx"),
        'tasks': load_data("课堂任务参与.xlsx")
    }
    
    # 清洗数据
    cleaned_data = {
        'info': clean_student_info(raw_data['info']),
        'scores': clean_scores(raw_data['scores']),
        'library': clean_library(raw_data['library']),
        'internet': clean_internet(raw_data['internet']),
        'attendance': clean_attendance(raw_data['attendance']),
        'tasks': clean_tasks(raw_data['tasks'])
    }
    
    # 合并数据
    final_data = merge_all_data(cleaned_data)
    
    # 保存清洗后的数据
    if final_data is not None:
        final_data.to_csv("cleaned_data.csv", index=False, encoding='utf-8-sig')
        print("\n[OK] 清洗后的数据已保存至: cleaned_data.csv")
    
    return final_data

if __name__ == "__main__":
    run_data_cleaning()
