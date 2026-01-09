#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试数据自动保存功能
"""

import requests
import json
import time
import sys
import io

# 设置stdout编码为UTF-8
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

base_url = "http://localhost:5000"
session = requests.Session()

print("="*70)
print("测试数据自动保存功能")
print("="*70)

# 步骤1: 设置用户名
print("\n[步骤1] 设置用户名...")
response = session.post(
    f"{base_url}/api/set-name",
    json={"name": "测试用户"},
    timeout=10
)

if response.status_code == 200:
    data = response.json()
    if data.get('success'):
        print(f"[OK] 用户名设置成功: {data['user_name']}")
        print(f"     是否有历史数据: {data.get('has_history', False)}")
    else:
        print(f"[FAIL] 失败: {data.get('error')}")
        exit(1)
else:
    print(f"[FAIL] HTTP错误: {response.status_code}")
    exit(1)

# 步骤2: 发送第一条消息，看AI是否问性别
print("\n[步骤2] 发送第一条消息...")
response = session.post(
    f"{base_url}/api/chat",
    json={"message": "你好"},
    timeout=30
)

if response.status_code == 200:
    data = response.json()
    if data.get('success'):
        reply = data.get('reply', '')
        print(f"[OK] AI回复:")
        print("-"*70)
        print(reply[:500])  # 只打印前500字符
        print("-"*70)

        # 检查是否包含DATA_UPDATE
        if "DATA_UPDATE" in reply:
            print("[OK] AI返回了DATA_UPDATE块")

            # 提取DATA_UPDATE内容
            import re
            match = re.search(r'DATA_UPDATE:\s*(\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\})', reply, re.DOTALL)
            if match:
                json_str = match.group(1)
                print(f"     提取的JSON: {json_str}")
                try:
                    parsed = json.loads(json_str)
                    print(f"     解析成功: {parsed}")
                except:
                    print(f"     [FAIL] JSON解析失败")
            else:
                print("     [FAIL] 未找到有效的DATA_UPDATE块")
        else:
            print("[INFO] AI没有返回DATA_UPDATE块（这是正常的，因为用户还没有提供数据）")
    else:
        print(f"[FAIL] 失败: {data.get('error')}")
else:
    print(f"[FAIL] HTTP错误: {response.status_code}")

# 步骤3: 回答性别问题
print("\n[步骤3] 回答性别问题...")
time.sleep(2)  # 等待2秒
response = session.post(
    f"{base_url}/api/chat",
    json={"message": "我是女性"},
    timeout=30
)

if response.status_code == 200:
    data = response.json()
    if data.get('success'):
        reply = data.get('reply', '')
        print(f"[OK] AI回复:")
        print("-"*70)
        print(reply[:500])
        print("-"*70)

        # 检查是否包含DATA_UPDATE
        if "DATA_UPDATE" in reply:
            print("[OK] AI返回了DATA_UPDATE块")

            # 提取DATA_UPDATE内容
            import re
            match = re.search(r'DATA_UPDATE:\s*(\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\})', reply, re.DOTALL)
            if match:
                json_str = match.group(1)
                print(f"     提取的JSON: {json_str}")
                try:
                    parsed = json.loads(json_str)
                    print(f"     [OK] 解析成功: {parsed}")

                    # 检查是否保存到文件
                    print("\n[步骤4] 检查数据是否保存到文件...")
                    import os
                    user_file = "user_data/测试用户.json"
                    if os.path.exists(user_file):
                        print(f"[OK] 用户数据文件存在: {user_file}")
                        with open(user_file, 'r', encoding='utf-8') as f:
                            saved_data = json.load(f)
                        print(f"     保存的数据: {json.dumps(saved_data, ensure_ascii=False, indent=2)}")

                        # 检查gender字段
                        if 'gender' in saved_data:
                            print(f"     [OK] gender字段已保存: {saved_data['gender']}")
                        else:
                            print(f"     [FAIL] gender字段未找到")
                    else:
                        print(f"[FAIL] 用户数据文件不存在: {user_file}")

                except Exception as e:
                    print(f"     [FAIL] JSON解析失败: {e}")
            else:
                print("     [FAIL] 未找到有效的DATA_UPDATE块")
        else:
            print("[FAIL] AI没有返回DATA_UPDATE块")
    else:
        print(f"[FAIL] 失败: {data.get('error')}")
else:
    print(f"[FAIL] HTTP错误: {response.status_code}")

# 步骤5: 再次对话，检查AI是否记住性别
print("\n[步骤5] 再次对话，检查AI是否记住性别...")
time.sleep(2)
response = session.post(
    f"{base_url}/api/chat",
    json={"message": "请继续问下一个问题"},
    timeout=30
)

if response.status_code == 200:
    data = response.json()
    if data.get('success'):
        reply = data.get('reply', '')
        print(f"[OK] AI回复:")
        print("-"*70)
        print(reply[:500])
        print("-"*70)

        # 检查AI是否又问性别（不应该）
        if "性别" in reply and "请问" in reply:
            print("[WARN] AI又问了性别问题（说明数据保存可能有问题）")
        else:
            print("[OK] AI没有重复问性别（数据保存成功）")
    else:
        print(f"[FAIL] 失败: {data.get('error')}")
else:
    print(f"[FAIL] HTTP错误: {response.status_code}")

print("\n" + "="*70)
print("测试完成")
print("="*70)
