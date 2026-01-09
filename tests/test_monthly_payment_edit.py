"""
测试月缴费额(flex_monthly_payments)字段的编辑功能
"""
import requests
import json
import sys
import io

# 设置标准输出编码为UTF-8
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

BASE_URL = "http://localhost:5000"

def test_monthly_payment_edit():
    """测试可以编辑月缴费额字段"""

    print("=" * 60)
    print("测试月缴费额字段编辑功能")
    print("=" * 60)

    # 创建session以保持cookies
    session = requests.Session()

    # 步骤1: 设置用户名称
    print("\n步骤1: 设置用户名称...")
    response = session.post(f"{BASE_URL}/api/set-name", json={"name": "test_user"})
    print(f"状态码: {response.status_code}")
    if response.status_code == 200:
        print("✓ 用户名称设置成功")
    else:
        print("✗ 用户名称设置失败")
        return False

    # 步骤2: 获取当前用户数据
    print("\n步骤2: 获取当前用户数据...")
    response = session.get(f"{BASE_URL}/api/user-data")
    print(f"状态码: {response.status_code}")

    if response.status_code != 200:
        print("✗ 获取用户数据失败")
        return False

    data = response.json()
    print(f"用户数据: {json.dumps(data, ensure_ascii=False, indent=2)}")

    # 步骤3: 更新月缴费额字段
    print("\n步骤3: 更新月缴费额字段...")
    new_monthly_payment = "低档60%:1400元/月,中档100%:2300元/月,高档300%:6800元/月"

    update_data = {
        "flex_monthly_payments": new_monthly_payment
    }

    response = session.post(f"{BASE_URL}/api/update-user-data", json=update_data)
    print(f"状态码: {response.status_code}")

    if response.status_code != 200:
        print("✗ 更新月缴费额失败")
        print(f"响应内容: {response.text}")
        return False

    result = response.json()
    print(f"更新结果: {json.dumps(result, ensure_ascii=False, indent=2)}")

    if not result.get('success'):
        print("✗ 更新失败")
        return False

    print("✓ 月缴费额更新成功")

    # 步骤4: 验证更新后的数据
    print("\n步骤4: 验证更新后的数据...")
    response = session.get(f"{BASE_URL}/api/user-data")
    print(f"状态码: {response.status_code}")

    if response.status_code != 200:
        print("✗ 获取更新后的用户数据失败")
        return False

    data = response.json()
    updated_value = data.get('data', {}).get('flex_monthly_payments') or data.get('flex_monthly_payments')

    print(f"更新后的月缴费额: {updated_value}")

    if updated_value == new_monthly_payment:
        print("✓ 月缴费额字段验证成功")
        return True
    else:
        print("✗ 月缴费额字段值不匹配")
        print(f"期望值: {new_monthly_payment}")
        print(f"实际值: {updated_value}")
        return False

def test_multiple_fields_edit():
    """测试同时编辑多个字段包括月缴费额"""

    print("\n" + "=" * 60)
    print("测试多字段编辑(包括月缴费额)")
    print("=" * 60)

    # 创建session以保持cookies
    session = requests.Session()

    # 设置用户名称
    print("\n设置用户名称...")
    response = session.post(f"{BASE_URL}/api/set-name", json={"name": "test_user2"})
    if response.status_code != 200:
        print("✗ 用户名称设置失败")
        return False

    # 准备多个字段的更新数据
    update_data = {
        "social_avg_wage": "16000",
        "flex_payment_bases": "下限60%:7200元,上限300%:36000元",
        "flex_monthly_payments": "低档60%:1368元/月,中档100%:2280元/月,高档300%:6840元/月"
    }

    print("\n更新数据:")
    print(json.dumps(update_data, ensure_ascii=False, indent=2))

    response = session.post(f"{BASE_URL}/api/update-user-data", json=update_data)
    print(f"\n状态码: {response.status_code}")

    if response.status_code != 200:
        print("✗ 多字段更新失败")
        return False

    result = response.json()
    if not result.get('success'):
        print("✗ 更新失败")
        return False

    print("✓ 多字段更新成功")

    # 验证所有字段
    response = session.get(f"{BASE_URL}/api/user-data")
    if response.status_code != 200:
        print("✗ 获取验证数据失败")
        return False

    data = response.json()
    data_content = data.get('data', data)

    # 检查月缴费额
    if data_content.get('flex_monthly_payments') == update_data['flex_monthly_payments']:
        print("✓ 月缴费额验证成功")
    else:
        print("✗ 月缴费额验证失败")
        return False

    # 检查社平工资
    if data_content.get('social_avg_wage') == update_data['social_avg_wage']:
        print("✓ 社平工资验证成功")
    else:
        print("✗ 社平工资验证失败")
        return False

    # 检查缴费基数
    if data_content.get('flex_payment_bases') == update_data['flex_payment_bases']:
        print("✓ 缴费基数验证成功")
    else:
        print("✗ 缴费基数验证失败")
        return False

    return True

if __name__ == "__main__":
    try:
        # 测试1: 单独编辑月缴费额字段
        success1 = test_monthly_payment_edit()

        # 测试2: 同时编辑多个字段(包括月缴费额)
        success2 = test_multiple_fields_edit()

        print("\n" + "=" * 60)
        print("测试总结")
        print("=" * 60)
        print(f"测试1 (单独编辑月缴费额): {'✓ 通过' if success1 else '✗ 失败'}")
        print(f"测试2 (多字段编辑): {'✓ 通过' if success2 else '✗ 失败'}")
        print("=" * 60)

        if success1 and success2:
            print("\n所有测试通过! ✓")
        else:
            print("\n部分测试失败! ✗")

    except requests.exceptions.ConnectionError:
        print("\n✗ 错误: 无法连接到服务器")
        print("请确保Flask服务器正在运行: python app.py")
    except Exception as e:
        print(f"\n✗ 测试过程中发生错误: {str(e)}")
        import traceback
        traceback.print_exc()
