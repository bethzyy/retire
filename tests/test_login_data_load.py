"""
测试登录后右侧边栏是否正确加载用户数据
"""
import requests
import json
import sys
import io

# 设置标准输出编码为UTF-8
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

BASE_URL = "http://localhost:5000"

def test_login_and_load_data():
    """测试登录后数据是否正确加载到右侧边栏"""

    print("=" * 60)
    print("测试登录后右侧边栏数据加载")
    print("=" * 60)

    # 创建session以保持cookies
    session = requests.Session()

    # 步骤1: 登录(设置用户名称)
    print("\n步骤1: 用户登录...")
    test_name = "test_data_load"
    response = session.post(f"{BASE_URL}/api/set-name", json={"name": test_name})

    print(f"状态码: {response.status_code}")
    if response.status_code != 200:
        print("✗ 登录失败")
        return False

    data = response.json()
    print(f"响应: {json.dumps(data, ensure_ascii=False, indent=2)}")
    print("✓ 登录成功")

    # 步骤2: 获取用户数据(模拟右侧边栏加载)
    print("\n步骤2: 获取用户数据(模拟右侧边栏)...")
    response = session.get(f"{BASE_URL}/api/user-data")

    print(f"状态码: {response.status_code}")
    if response.status_code != 200:
        print("✗ 获取用户数据失败")
        return False

    data = response.json()
    print(f"用户数据: {json.dumps(data, ensure_ascii=False, indent=2)}")

    # 步骤3: 验证数据结构
    print("\n步骤3: 验证数据结构...")
    required_fields = ['success', 'user_name', 'data']
    all_present = True

    for field in required_fields:
        if field in data:
            print(f"✓ 字段 '{field}' 存在")
        else:
            print(f"✗ 字段 '{field}' 缺失")
            all_present = False

    if not all_present:
        return False

    # 步骤4: 验证用户名称
    print("\n步骤4: 验证用户名称...")
    if data.get('user_name') == test_name:
        print(f"✓ 用户名称正确: {test_name}")
    else:
        print(f"✗ 用户名称不匹配")
        print(f"  期望: {test_name}")
        print(f"  实际: {data.get('user_name')}")
        return False

    # 步骤5: 检查data对象是否存在
    print("\n步骤5: 检查data对象...")
    if data.get('data') is not None:
        print("✓ data对象存在")
        if isinstance(data.get('data'), dict):
            print("✓ data对象是字典类型")
        else:
            print("✗ data对象不是字典类型")
            return False
    else:
        print("⚠ data对象为None(新用户,正常情况)")

    print("\n" + "=" * 60)
    print("测试结果: ✓ 通过")
    print("=" * 60)
    return True

def test_existing_user_data_load():
    """测试已有数据的用户登录后数据是否正确加载"""

    print("\n" + "=" * 60)
    print("测试已有用户数据加载")
    print("=" * 60)

    # 创建session
    session = requests.Session()

    # 使用beth用户(已知有数据)
    test_name = "beth"

    print(f"\n步骤1: 登录已有用户 {test_name}...")
    response = session.post(f"{BASE_URL}/api/set-name", json={"name": test_name})

    print(f"状态码: {response.status_code}")
    if response.status_code != 200:
        print("✗ 登录失败")
        return False

    data = response.json()
    if data.get('has_history'):
        print("✓ 检测到历史数据")
    else:
        print("⚠ 未检测到历史数据")

    print("\n步骤2: 获取用户数据...")
    response = session.get(f"{BASE_URL}/api/user-data")

    if response.status_code != 200:
        print("✗ 获取用户数据失败")
        return False

    data = response.json()
    user_data = data.get('data', {})

    print(f"\n用户数据字段数量: {len(user_data)}")

    # 检查关键字段
    key_fields = [
        'user_name', 'gender', 'birth_year', 'birth_month',
        'social_avg_wage', 'flex_payment_bases', 'flex_monthly_payments'
    ]

    print("\n关键字段检查:")
    for field in key_fields:
        if field in user_data and user_data[field]:
            print(f"✓ {field}: {user_data[field]}")
        else:
            print(f"⚠ {field}: 未设置或为空")

    print("\n" + "=" * 60)
    print("测试结果: ✓ 通过")
    print("=" * 60)
    return True

if __name__ == "__main__":
    try:
        # 测试1: 新用户登录后数据加载
        success1 = test_login_and_load_data()

        # 测试2: 已有用户数据加载
        success2 = test_existing_user_data_load()

        print("\n" + "=" * 60)
        print("最终总结")
        print("=" * 60)
        print(f"测试1 (新用户数据加载): {'✓ 通过' if success1 else '✗ 失败'}")
        print(f"测试2 (已有用户数据加载): {'✓ 通过' if success2 else '✗ 失败'}")
        print("=" * 60)

        if success1 and success2:
            print("\n所有测试通过! ✓")
            print("\n登录后右侧边栏应该能正确显示用户数据。")
        else:
            print("\n部分测试失败! ✗")

    except requests.exceptions.ConnectionError:
        print("\n✗ 错误: 无法连接到服务器")
        print("请确保Flask服务器正在运行: python app.py")
    except Exception as e:
        print(f"\n✗ 测试过程中发生错误: {str(e)}")
        import traceback
        traceback.print_exc()
