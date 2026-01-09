#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试WebSearch实时搜索功能
验证AI是否会主动搜索最新数据而不是使用硬编码数据
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
print("测试WebSearch实时搜索功能")
print("="*70)

# 步骤1: 设置用户名
print("\n[步骤1] 设置用户名...")
response = session.post(
    f"{base_url}/api/set-name",
    json={"name": "测试用户WebSearch"},
    timeout=10
)

if response.status_code == 200:
    data = response.json()
    if data.get('success'):
        print(f"[OK] 用户名设置成功: {data['user_name']}")
    else:
        print(f"[FAIL] 失败: {data.get('error')}")
        exit(1)
else:
    print(f"[FAIL] HTTP错误: {response.status_code}")
    exit(1)

# 步骤2: 快速回答完所有问题
print("\n[步骤2] 快速回答问题收集信息...")

questions_and_answers = [
    ("你好", "请问您的性别是？"),  # AI第一次会问性别
    ("女", "请问您的出生年份是？"),
    ("1985年", "请问您的户口性质是？"),
    ("城镇", "请问您目前的失业状态及开始时间？"),
    ("失业，2026年1月开始", "请问您的预计退休年龄？"),
    ("50岁", "请问您的首次工作时间？"),
    ("2005年", "请问您的累计工作年限？"),
    ("20年", "请问您的实际缴费年限？"),
    ("20年", "请问您的近3年平均工资？"),
    ("8000元", "请问您的个人账户余额？"),
    ("100000元", "请问您是否有高级职称等特殊情况？"),
    ("无", "请问您的预期寿命？"),
    ("80岁", "【信息总结】")  # 最后AI会总结信息
)

for i, (question, expected_keyword) in enumerate(questions_and_answers):
    print(f"\n[问题 {i+1}] 用户: {question}")
    response = session.post(
        f"{base_url}/api/chat",
        json={"message": question},
        timeout=30
    )

    if response.status_code == 200:
        data = response.json()
        if data.get('success'):
            reply = data.get('reply', '')
            print(f"AI回复预览: {reply[:150]}...")

            # 检查是否包含预期关键词
            if expected_keyword and expected_keyword not in reply:
                print(f"[WARN] 未找到预期关键词: {expected_keyword}")
    else:
        print(f"[FAIL] HTTP错误: {response.status_code}")
        break

    time.sleep(1)

# 步骤3: 确认信息
print("\n[步骤3] 确认信息...")
response = session.post(
    f"{base_url}/api/chat",
    json={"message": "确认"},
    timeout=60  # 给足够时间让AI搜索和计算
)

if response.status_code == 200:
    data = response.json()
    if data.get('success'):
        reply = data.get('reply', '')
        print(f"\n[OK] AI完整回复:")
        print("-"*70)
        print(reply)
        print("-"*70)

        # 关键检查:是否包含搜索行为
        print("\n[检查] 验证AI是否使用了WebSearch...")

        checks = {
            "搜索提示": any(keyword in reply for keyword in ["搜索", "查询", "正在获取", "最新数据"]),
            "使用最新年份": any(keyword in reply for keyword in ["2026年", "2025年", "最新"]),
            "数据来源说明": any(keyword in reply for keyword in ["数据来源", "官方", "根据", "公布"]),
            "明确标注年份": "2024年" not in reply or "过时" in reply  # 如果提到2024,应该说明已过时
        }

        all_passed = True
        for check_name, passed in checks.items():
            status = "[OK]" if passed else "[FAIL]"
            print(f"{status} {check_name}: {'通过' if passed else '未通过'}")
            if not passed:
                all_passed = False

        if all_passed:
            print("\n[SUCCESS] 所有检查通过!AI正在使用实时搜索!")
        else:
            print("\n[WARNING] 部分检查未通过,可能需要调整提示词")
    else:
        print(f"[FAIL] 失败: {data.get('error')}")
else:
    print(f"[FAIL] HTTP错误: {response.status_code}")

print("\n" + "="*70)
print("测试完成")
print("="*70)
