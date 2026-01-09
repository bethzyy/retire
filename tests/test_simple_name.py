#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
简化的名字识别测试
"""

import requests
import json

base_url = "http://localhost:5000"
session = requests.Session()

print("="*70)
print("简化的名字识别测试")
print("="*70)

# 步骤1：发送消息
print("\n步骤1：发送消息")
response = session.post(f"{base_url}/api/chat", json={"message": "你好"}, timeout=30)
data = response.json()
print(f"用户名字: {data.get('user_name')}")
print(f"有历史数据: {data.get('has_history')}")
print(f"AI回复前100字: {data.get('reply', '')[:100]}")

# 步骤2：回答名字
print("\n步骤2：回答名字 '张三'")
response = session.post(f"{base_url}/api/chat", json={"message": "张三"}, timeout=30)
data = response.json()
print(f"用户名字: {data.get('user_name')}")
print(f"有历史数据: {data.get('has_history')}")
print(f"AI回复前100字: {data.get('reply', '')[:100]}")

# 步骤3：重置
print("\n步骤3：重置对话")
response = session.post(f"{base_url}/api/reset", json={}, timeout=10)
print(f"重置成功: {response.json().get('success')}")

# 步骤4：再次访问
print("\n步骤4：再次访问，发送 '你好'")
response = session.post(f"{base_url}/api/chat", json={"message": "你好"}, timeout=30)
data = response.json()
print(f"用户名字: {data.get('user_name')}")
print(f"有历史数据: {data.get('has_history')}")
print(f"AI回复前100字: {data.get('reply', '')[:100]}")

# 步骤5：再次回答名字
print("\n步骤5：再次回答名字 '张三'")
response = session.post(f"{base_url}/api/chat", json={"message": "张三"}, timeout=30)
data = response.json()
print(f"用户名字: {data.get('user_name')}")
print(f"有历史数据: {data.get('has_history')}")
print(f"AI回复前200字: {data.get('reply', '')[:200]}")

# 步骤6：检查文件
print("\n步骤6：检查用户数据文件")
import os
if os.path.exists('user_data/张三.json'):
    with open('user_data/张三.json', 'r', encoding='utf-8') as f:
        user_data = json.load(f)
    print(f"文件内容:")
    print(json.dumps(user_data, indent=2, ensure_ascii=False))
else:
    print("文件不存在")

print("\n"+"="*70)
