#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试新的缴费水平问题
验证AI是否询问平均缴费水平而不是近3年平均工资
"""

import requests
import json
import sys
import io
import time

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

base_url = "http://localhost:5000"

def test_payment_level_question():
    """测试缴费水平问题"""
    print("\n" + "="*70)
    print("测试新的缴费水平问题")
    print("="*70)

    session = requests.Session()

    # 步骤1: 设置用户名
    print("\n[步骤1] 设置用户名...")
    response = session.post(
        f"{base_url}/api/set-name",
        json={"name": "测试用户缴费水平"},
        timeout=10
    )

    if response.status_code != 200 or not response.json().get('success'):
        print("[FAIL] 设置用户名失败")
        return False

    print("[OK] 用户名设置成功")

    # 快速回答前面的问题
    print("\n[步骤2] 快速回答基础问题...")

    answers = [
        ("你好", "触发第一个问题"),
        ("A", "性别-男"),
        ("A", "户口-城镇"),
        ("1990-06", "出生日期"),
        ("A", "就业状态-在职"),
        ("2020", "首次工作年份"),
        ("15", "累计工作年限"),
        ("0", "视同缴费年限"),
        ("15", "实际缴费年限"),
    ]

    for answer, desc in answers:
        print(f"  回答: {desc} ({answer})")
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

        time.sleep(0.5)

    print("[OK] 基础问题回答完成")

    # 步骤3: 检查下一个问题是否是缴费水平问题
    print("\n[步骤3] 检查AI是否询问平均缴费水平...")
    response = session.post(
        f"{base_url}/api/chat",
        json={"message": "100000"},  # 个人账户余额
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

    # 关键检查点
    checks = {
        "❌ 不应出现'近3年平均工资'": "近3年平均工资" not in reply and "最近3年" not in reply,
        "✅ 应该询问'平均缴费水平'或'缴费档次'": any(keyword in reply for keyword in ["平均缴费水平", "缴费档次", "缴费指数", "60%档", "100%档"]),
        "✅ 应该有ABCDE选项": all(keyword in reply for keyword in ["A.", "B.", "C.", "D.", "E."]) or \
                         all(keyword in reply for keyword in ["A、", "B、", "C、", "D、", "E、"]),
        "✅ 应该有60%档选项": "60%档" in reply or "60%" in reply,
        "✅ 应该有100%档选项": "100%档" in reply or "100%" in reply,
        "✅ 应该有300%档选项": "300%档" in reply or "300%" in reply,
    }

    all_passed = True
    for check_name, passed in checks.items():
        status = "[OK]" if passed else "[FAIL]"
        print(f"{status} {check_name}")
        if not passed:
            all_passed = False

    if all_passed:
        print("\n[SUCCESS] 缴费水平问题正确!不再询问近3年平均工资")
        return True
    else:
        print("\n[FAIL] 缴费水平问题可能有问题")
        return False

if __name__ == "__main__":
    print("\n" + "="*70)
    print("缴费水平问题测试")
    print("验证AI询问的是平均缴费水平,而不是近3年平均工资")
    print("="*70)

    success = test_payment_level_question()

    print("\n" + "="*70)
    if success:
        print("✓ 测试通过!缴费水平问题正确")
    else:
        print("✗ 测试失败!可能需要调整提示词")
    print("="*70 + "\n")

    sys.exit(0 if success else 1)
