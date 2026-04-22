# -*- coding: utf-8 -*-
from docx import Document
import sys

sys.stdout.reconfigure(encoding='utf-8')

doc = Document('基于多源数据的大学生行为分析与干预模型设计.docx')

print('=' * 70)
print('基于多源数据的大学生行为分析与干预模型设计 - 完整文档')
print('=' * 70)

content = []
for para in doc.paragraphs:
    text = para.text.strip()
    if text:
        content.append(text)

# 打印所有内容
for line in content:
    print(line)
    print()
