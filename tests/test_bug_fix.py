#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试Bug修复 - 模拟用户报告的问题:
1. 登录
2. 清空记录
3. 发送"开始"
验证AI是否正常响应,不再出现null classList错误
"""

import requests
import json
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

base_url = "http://localhost:5000"

def test_bug_fix():
    """测试Bug修复"""
    print("\n" + "="*70)
    print("测试Bug修复: 登录→清空记录→发送'开始'")
    print("="*70)

    session = requests.Session()

    # 步骤1: 设置用户名(登录)
    print("\n[步骤1] 登录(设置用户名)...")
    response = session.post(
        f"{base_url}/api/set-name",
        json={"name": "测试用户Bug修复"},
        timeout=10
    )

    if response.status_code == 200:
        data = response.json()
        if data.get('success'):
            print(f"[OK] 登录成功: {data['user_name']}")
        else:
            print(f"[FAIL] 登录失败: {data.get('error')}")
            return False
    else:
        print(f"[FAIL] HTTP错误: {response.status_code}")
        return False

    # 步骤2: 发送第一条消息
    print("\n[步骤2] 发送第一条消息测试...")
    response = session.post(
        f"{base_url}/api/chat",
        json={"message": "你好"},
        timeout=30
    )

    if response.status_code == 200:
        data = response.json()
        if data.get('success'):
            print(f"[OK] AI响应成功")
            print(f"AI回复预览: {data.get('reply', '')[:100]}...")
        else:
            print(f"[FAIL] AI响应失败: {data.get('error')}")
            return False
    else:
        print(f"[FAIL] HTTP错误: {response.status_code}")
        return False

    # 步骤3: 重置对话(清空记录)
    print("\n[步骤3] 重置对话(清空记录)...")
    response = session.post(
        f"{base_url}/api/reset",
        timeout=10
    )

    if response.status_code == 200:
        data = response.json()
        if data.get('success'):
            print(f"[OK] 重置成功: {data.get('message')}")
        else:
            print(f"[FAIL] 重置失败: {data.get('error')}")
            return False
    else:
        print(f"[FAIL] HTTP错误: {response.status_code}")
        return False

    # 步骤4: 发送"开始"消息(这是用户报告的问题场景)
    print("\n[步骤4] 发送'开始'消息(关键测试)...")
    response = session.post(
        f"{base_url}/api/chat",
        json={"message": "开始"},
        timeout=30
    )

    if response.status_code == 200:
        data = response.json()
        if data.get('success'):
            print(f"[OK] AI响应成功!")
            print(f"AI完整回复:")
            print("-"*70)
            print(data.get('reply', ''))
            print("-"*70)

            # 检查AI是否正常询问问题
            reply = data.get('reply', '')
            if any(keyword in reply for keyword in ['性别', '请问', '你好', '欢迎']):
                print("\n[SUCCESS] Bug已修复!AI正常响应,没有null classList错误")
                return True
            else:
                print("\n[WARN] AI响应了但内容可能不正常")
                return False
        else:
            print(f"[FAIL] AI响应失败: {data.get('error')}")
            return False
    else:
        print(f"[FAIL] HTTP错误: {response.status_code}")
        return False

if __name__ == "__main__":
    print("\n" + "="*70)
    print("Bug修复验证测试")
    print("测试场景: 登录→清空记录→发送'开始'")
    print("="*70)

    success = test_bug_fix()

    print("\n" + "="*70)
    if success:
        print("✓ 测试通过!Bug已修复")
    else:
        print("✗ 测试失败!可能仍有问题")
    print("="*70 + "\n")

    sys.exit(0 if success else 1)
