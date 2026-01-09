#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试ABCD选择题功能
验证AI是否在适当的问题上使用选择题格式
"""

import requests
import json
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

base_url = "http://localhost:5000"

def test_abc_questions():
    """测试ABCD选择题功能"""
    print("\n" + "="*70)
    print("测试ABCD选择题功能")
    print("="*70)

    session = requests.Session()

    # 步骤1: 设置用户名
    print("\n[步骤1] 设置用户名...")
    response = session.post(
        f"{base_url}/api/set-name",
        json={"name": "测试用户ABCD"},
        timeout=10
    )

    if response.status_code != 200 or not response.json().get('success'):
        print("[FAIL] 设置用户名失败")
        return False

    print("[OK] 用户名设置成功")

    # 步骤2: 发送第一条消息
    print("\n[步骤2] 发送'你好'触发第一个问题(性别)...")
    response = session.post(
        f"{base_url}/api/chat",
        json={"message": "你好"},
        timeout=30
    )

    if response.status_code != 200:
        print(f"[FAIL] HTTP错误: {response.status_code}")
        return False

    data = response.json()
    if not data.get('success'):
        print(f"[FAIL] AI响应失败: {data.get('error')}")
        return False

    reply = data.get('reply', '')
    print(f"\nAI回复:\n{reply}\n")

    # 检查是否使用了ABCD选择题格式
    checks = {
        "包含问题": "性别" in reply,
        "包含选项A": "A." in reply or "A、" in reply or "A)" in reply,
        "包含选项B": "B." in reply or "B、" in reply or "B)" in reply,
        "提示回复字母": any(keyword in reply for keyword in ["回复字母", "直接回复", "选择 A/B"]),
    }

    all_passed = True
    for check_name, passed in checks.items():
        status = "[OK]" if passed else "[FAIL]"
        print(f"{status} {check_name}: {'通过' if passed else '未通过'}")
        if not passed:
            all_passed = False

    if all_passed:
        print("\n[SUCCESS] AI正确使用了ABCD选择题格式!")

    # 步骤3: 回复选择题
    print("\n[步骤3] 回复选择题(选择A-男)...")
    response = session.post(
        f"{base_url}/api/chat",
        json={"message": "A"},
        timeout=30
    )

    if response.status_code != 200:
        print(f"[FAIL] HTTP错误: {response.status_code}")
        return False

    data = response.json()
    if not data.get('success'):
        print(f"[FAIL] AI响应失败: {data.get('error')}")
        return False

    reply = data.get('reply', '')
    print(f"\nAI回复:\n{reply[:200]}...\n")

    # 检查是否正确记录了数据
    if "DATA_UPDATE" in reply and "gender" in reply:
        print("[OK] AI正确记录了选择题答案(DATA_UPDATE)")
    else:
        print("[WARN] DATA_UPDATE可能不完整")

    # 检查是否问了下一个问题
    if any(keyword in reply for keyword in ["出生", "户口", "请问"]):
        print("[OK] AI继续问下一个问题")
    else:
        print("[WARN] AI可能没有问下一个问题")

    return all_passed

if __name__ == "__main__":
    print("\n" + "="*70)
    print("ABCD选择题功能测试")
    print("="*70)

    success = test_abc_questions()

    print("\n" + "="*70)
    if success:
        print("✓ 测试通过!ABCD选择题功能正常")
    else:
        print("✗ 测试失败!可能需要调整提示词")
    print("="*70 + "\n")

    sys.exit(0 if success else 1)
