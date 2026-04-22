# -*- coding: utf-8 -*-
from docx import Document
import sys

# 设置UTF-8输出
sys.stdout.reconfigure(encoding='utf-8')

doc = Document('基于多源数据的大学生行为分析与干预模型设计.docx')

print('=' * 60)
print('基于多源数据的大学生行为分析与干预模型设计 - 文档内容')
print('=' * 60)

for i, para in enumerate(doc.paragraphs):
    text = para.text.strip()
    if text:
        print(f'{text}')
        print()
