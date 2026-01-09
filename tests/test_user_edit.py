#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试用户信息编辑功能
"""

import requests
import json
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

base_url = "http://localhost:5000"

def test_user_edit():
    """测试用户信息编辑功能"""
    print("\n" + "="*70)
    print("测试用户信息编辑功能")
    print("="*70)

    session = requests.Session()

    # 步骤1: 设置用户名
    print("\n[步骤1] 设置用户名...")
    response = session.post(
        f"{base_url}/api/set-name",
        json={"name": "测试用户编辑"}
    )

    if response.status_code != 200 or not response.json().get('success'):
        print("[FAIL] 设置用户名失败")
        return False

    print("[OK] 用户名设置成功")

    # 步骤2: 添加一些基础数据
    print("\n[步骤2] 添加基础数据...")
    test_data = {
        "gender": "男",
        "birth_year": "1990",
        "birth_month": "06",
        "hukou_type": "城镇",
        "employment_status": "在职"
    }

    # 通过模拟DATA_UPDATE来保存数据
    response = session.post(
        f"{base_url}/api/chat",
        json={"message": "我是男性,1990年6月出生,城镇户口,在职"},
        timeout=120
    )

    if response.status_code != 200:
        print(f"[FAIL] 添加数据失败: HTTP {response.status_code}")
        return False

    print("[OK] 基础数据已添加")

    # 步骤3: 获取用户数据
    print("\n[步骤3] 获取用户数据...")
    response = session.get(f"{base_url}/api/user-data")

    if response.status_code != 200:
        print(f"[FAIL] 获取用户数据失败: HTTP {response.status_code}")
        return False

    data = response.json()
    if not data.get('success'):
        print(f"[FAIL] 获取用户数据失败: {data.get('error')}")
        return False

    print(f"[OK] 获取用户数据成功")
    print(f"  用户名: {data.get('user_name')}")
    print(f"  数据: {json.dumps(data.get('data'), ensure_ascii=False, indent=2)}")

    # 步骤4: 更新用户数据
    print("\n[步骤4] 更新用户数据...")
    updated_data = {
        "gender": "女",  # 修改性别
        "birth_year": "1992",  # 修改出生年份
        "account_balance": "100000",  # 添加账户余额
        "retirement_age": "60"  # 添加退休年龄
    }

    response = session.post(
        f"{base_url}/api/update-user-data",
        json=updated_data
    )

    if response.status_code != 200:
        print(f"[FAIL] 更新用户数据失败: HTTP {response.status_code}")
        return False

    result = response.json()
    if not result.get('success'):
        print(f"[FAIL] 更新用户数据失败: {result.get('error')}")
        return False

    print("[OK] 用户数据更新成功")
    print(f"  更新后的数据: {json.dumps(result.get('data'), ensure_ascii=False, indent=2)}")

    # 步骤5: 验证更新
    print("\n[步骤5] 验证更新...")
    response = session.get(f"{base_url}/api/user-data")

    if response.status_code != 200:
        print(f"[FAIL] 获取更新后的数据失败: HTTP {response.status_code}")
        return False

    data = response.json()
    updated_user_data = data.get('data', {})

    # 检查关键字段
    checks = [
        ("性别已更新为女", updated_user_data.get('gender') == "女"),
        ("出生年份已更新为1992", updated_user_data.get('birth_year') == "1992"),
        ("账户余额已添加", updated_user_data.get('account_balance') == "100000"),
        ("退休年龄已添加", updated_user_data.get('retirement_age') == "60"),
        ("户口性质保持不变", updated_user_data.get('hukou_type') == "城镇"),
    ]

    all_passed = True
    for check_name, passed in checks:
        status = "[OK]" if passed else "[FAIL]"
        print(f"  {status} {check_name}")
        if not passed:
            all_passed = False

    if all_passed:
        print("\n[SUCCESS] 用户信息编辑功能测试通过!")
        print("功能验证:")
        print("  ✓ 可以获取用户数据")
        print("  ✓ 可以更新用户数据")
        print("  ✓ 支持按条修改字段")
        print("  ✓ 未修改的字段保持不变")
        print("  ✓ 新增字段正确保存")
        return True
    else:
        print("\n[FAIL] 用户信息编辑功能测试失败")
        return False

if __name__ == "__main__":
    print("\n" + "="*70)
    print("用户信息编辑功能测试")
    print("验证前端编辑表单和后端API")
    print("="*70)

    success = test_user_edit()

    print("\n" + "="*70)
    if success:
        print("✓ 测试通过!用户信息编辑功能正常")
    else:
        print("✗ 测试失败!需要检查功能实现")
    print("="*70 + "\n")

    sys.exit(0 if success else 1)
