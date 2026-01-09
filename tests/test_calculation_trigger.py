#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试计算触发机制
验证AI在收到用户确认("A")后是否会实际调用WebSearch工具
而不是反复说"正在搜索"但不采取行动
"""

import requests
import json
import sys
import io
import time

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

base_url = "http://localhost:5000"

def test_calculation_trigger():
    """测试计算触发机制"""
    print("\n" + "="*70)
    print("测试计算触发机制 - 验证AI是否实际调用WebSearch")
    print("="*70)

    session = requests.Session()

    # 步骤1: 设置用户名
    print("\n[步骤1] 设置用户名...")
    response = session.post(
        f"{base_url}/api/set-name",
        json={"name": "测试用户计算触发"},
        timeout=10
    )

    if response.status_code != 200 or not response.json().get('success'):
        print("[FAIL] 设置用户名失败")
        return False

    print("[OK] 用户名设置成功")

    # 步骤2: 快速完成所有问题
    print("\n[步骤2] 快速完成所有问题收集...")

    # 模拟用户快速回答所有问题
    answers = [
        "你好",  # 触发第一个问题
        "A",     # 性别-男
        "A",     # 户口-城镇
        "1990-06-15",  # 出生日期
        "A",     # 就业状态-在职
        "2020",  # 参加工作年份
        "15",    # 实际缴费年限
        "0",     # 视同缴费年限
        "500000",  # 个人账户余额
        "B",     # 有外地经历
        "5",     # 外地年限
        "上海",  # 外地地点
        "A",     # 已转入
        "B",     # 无高级职称
    ]

    for i, answer in enumerate(answers, 1):
        print(f"  [回答 {i}/{len(answers)}] 发送: {answer}")
        response = session.post(
            f"{base_url}/api/chat",
            json={"message": answer},
            timeout=30
        )

        if response.status_code != 200:
            print(f"[FAIL] HTTP错误: {response.status_code}")
            return False

        data = response.json()
        if not data.get('success'):
            print(f"[FAIL] AI响应失败: {data.get('error')}")
            return False

        # 短暂延迟避免请求过快
        time.sleep(0.5)

    print("[OK] 所有问题回答完成")

    # 步骤3: 获取最后的回复（应该是确认信息）
    print("\n[步骤3] 查看AI最后的确认消息...")
    response = session.post(
        f"{base_url}/api/chat",
        json={"message": "请确认"},
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
    print(f"\nAI回复预览:\n{reply[:300]}...\n")

    # 检查是否包含确认选项
    has_confirmation = "确认" in reply and ("A." in reply or "A、" in reply or "A)" in reply)
    if not has_confirmation:
        print("[WARN] AI可能还没有提供确认选项，继续测试...")

    # 步骤4: 发送"A"确认 - 关键测试！
    print("\n[步骤4] 发送'A'确认 - 测试AI是否实际调用WebSearch...")
    response = session.post(
        f"{base_url}/api/chat",
        json={"message": "A"},
        timeout=60  # 给AI更多时间进行搜索
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

    # 关键检查：AI是否真的在搜索，而不是反复说"正在搜索"
    checks = {
        "包含搜索关键词": "搜索" in reply or "查询" in reply,
        "包含具体年份": "2026" in reply or "2025" in reply or "2024" in reply,
        "包含社保关键词": "社保" in reply or "社平工资" in reply or "缴费基数" in reply,
        "包含计算结果": "档位" in reply or "元" in reply or "月" in reply,
        "包含工具调用迹象": any(keyword in reply for keyword in [
            "【开始搜索】", "正在搜索", "搜索结果", "根据搜索", "数据显示"
        ]),
        "避免反复说要搜索": reply.count("正在为您搜索") <= 1,  # 最多出现1次
    }

    all_passed = True
    for check_name, passed in checks.items():
        status = "[OK]" if passed else "[FAIL]"
        print(f"{status} {check_name}: {'通过' if passed else '未通过'}")
        if not passed:
            all_passed = False

    # 特别检查：是否有"说搜索但不搜索"的迹象
    if "正在为您搜索" in reply and "搜索" in reply and "计算" not in reply and "档位" not in reply:
        print("\n[WARN] AI可能只是说搜索但没有实际行动!")
        print("       建议检查system_prompt.txt中的计算触发机制说明")
        all_passed = False

    if all_passed:
        print("\n[SUCCESS] 计算触发机制工作正常!AI实际进行了搜索")
        return True
    else:
        print("\n[FAIL] 计算触发机制可能有问题，需要调整提示词")
        return False

if __name__ == "__main__":
    print("\n" + "="*70)
    print("计算触发机制测试")
    print("验证AI在收到确认后是否实际调用WebSearch工具")
    print("="*70)

    success = test_calculation_trigger()

    print("\n" + "="*70)
    if success:
        print("✓ 测试通过!计算触发机制正常")
    else:
        print("✗ 测试失败!可能需要调整system_prompt.txt")
    print("="*70 + "\n")

    sys.exit(0 if success else 1)
