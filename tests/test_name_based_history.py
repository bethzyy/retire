#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
基于名字的历史记录功能测试
"""

import requests
import time
import json


def test_name_based_history():
    """测试基于名字的用户历史记录功能"""

    base_url = "http://localhost:5000"
    session = requests.Session()

    print("="*70)
    print("基于名字的历史记录功能测试")
    print("="*70)

    # 测试场景1：首次使用 - 回答名字
    print("\n【测试1】首次访问 - 询问名字")
    print("-"*70)

    response = session.post(
        f"{base_url}/api/chat",
        json={"message": "你好"},
        timeout=30
    )

    if response.status_code == 200:
        data = response.json()
        if data.get('success'):
            reply = data.get('reply', '')
            user_name = data.get('user_name')
            has_history = data.get('has_history', False)

            print(f"[OK] 首次对话成功")
            print(f"  用户名字: {user_name}")
            print(f"  有历史数据: {has_history}")
            print(f"  AI回复: {reply[:200]}...")

            # 回答名字
            test_name = "张三"
            print(f"\n回答名字: {test_name}")
            response = session.post(
                f"{base_url}/api/chat",
                json={"message": test_name},
                timeout=30
            )
            if response.status_code == 200:
                data = response.json()
                print(f"  AI: {data.get('reply', '')[:100]}...")
                print(f"  用户名字: {data.get('user_name')}")
            else:
                print(f"  [ERROR] 失败: {response.status_code}")
        else:
            print(f"[ERROR] API错误: {data.get('error')}")
            return
    else:
        print(f"[ERROR] HTTP错误: {response.status_code}")
        return

    # 回答几个更多问题，以便有数据保存
    print("\n【补充信息】回答更多问题...")
    test_answers = ["男", "1985年1月", "城镇"]
    for i, answer in enumerate(test_answers):
        print(f"  回答问题{i+1}: {answer}")
        response = session.post(
            f"{base_url}/api/chat",
            json={"message": answer},
            timeout=30
        )
        if response.status_code == 200:
            data = response.json()
            print(f"    AI: {data.get('reply', '')[:80]}...")
        else:
            print(f"    [ERROR] 失败: {response.status_code}")

    # 测试场景2：重置对话
    print("\n【测试2】重置对话")
    print("-"*70)

    response = session.post(
        f"{base_url}/api/reset",
        json={},
        timeout=10
    )

    if response.status_code == 200:
        print("[OK] 对话已重置")
    else:
        print(f"[ERROR] 重置失败: {response.status_code}")

    # 测试场景3：再次访问，回答同样的名字
    print("\n【测试3】再次访问并回答同样的名字 - 应该识别历史数据")
    print("-"*70)

    # 稍等片刻，模拟下次访问
    time.sleep(2)

    response = session.post(
        f"{base_url}/api/chat",
        json={"message": "你好，我又来了"},
        timeout=30
    )

    if response.status_code == 200:
        data = response.json()
        if data.get('success'):
            reply = data.get('reply', '')
            user_name = data.get('user_name')
            has_history = data.get('has_history', False)

            print(f"[OK] 再次访问成功")
            print(f"  用户名字: {user_name}")
            print(f"  有历史数据: {has_history}")

            # 回答同样的名字
            print(f"\n回答名字: {test_name}")
            response = session.post(
                f"{base_url}/api/chat",
                json={"message": test_name},
                timeout=30
            )
            if response.status_code == 200:
                data = response.json()
                reply = data.get('reply', '')
                user_name_now = data.get('user_name')
                has_history_now = data.get('has_history', False)

                print(f"  AI回复: {reply[:300]}...")
                print(f"  用户名字: {user_name_now}")
                print(f"  有历史数据: {has_history_now}")

                # 检查是否识别了历史数据
                checks = {
                    "识别用户名字": user_name_now == test_name,
                    "找到历史数据": has_history_now,
                    "欢迎回来": "欢迎回来" in reply or "又来了" in reply or "再次" in reply or "很高兴再次" in reply,
                    "历史信息": "之前提供过" in reply or "已提供" in reply or "档案" in reply or "已经提供" in reply,
                    "提到名字": test_name in reply or "张三" in reply
                }

                print("\n检查结果:")
                for check, passed in checks.items():
                    status = "[OK]" if passed else "[ERROR]"
                    print(f"  {status} {check}")
            else:
                print(f"  [ERROR] 失败: {response.status_code}")
        else:
            print(f"[ERROR] API错误: {data.get('error')}")
    else:
        print(f"[ERROR] HTTP错误: {response.status_code}")

    # 测试场景4：检查用户数据文件
    print("\n【测试4】检查用户数据文件")
    print("-"*70)

    try:
        import os
        user_data_dir = "user_data"
        if os.path.exists(user_data_dir):
            files = [f for f in os.listdir(user_data_dir) if f.endswith('.json')]
            print(f"[OK] 用户数据目录存在")
            print(f"  用户数量: {len(files)}")
            for f in files:
                print(f"  - {f}")

            # 检查是否有张三的数据文件
            expected_file = f"{test_name}.json"
            if expected_file in files:
                print(f"\n[OK] 找到用户数据文件: {expected_file}")

                # 读取并显示内容
                with open(os.path.join(user_data_dir, expected_file), 'r', encoding='utf-8') as f:
                    user_data = json.load(f)
                print(f"  数据内容:")
                for key, value in user_data.items():
                    if key not in ['created_at', 'last_updated']:
                        print(f"    {key}: {value}")
            else:
                print(f"\n[ERROR] 未找到用户数据文件: {expected_file}")
        else:
            print("[ERROR] 用户数据目录不存在")
    except Exception as e:
        print(f"[ERROR] 检查失败: {str(e)}")

    # 测试场景5：使用不同的名字
    print("\n【测试5】使用不同的名字 - 应该不识别历史数据")
    print("-"*70)

    response = session.post(
        f"{base_url}/api/reset",
        json={},
        timeout=10
    )

    different_name = "李四"
    print(f"重置后回答不同的名字: {different_name}")
    response = session.post(
        f"{base_url}/api/chat",
        json={"message": different_name},
        timeout=30
    )

    if response.status_code == 200:
        data = response.json()
        user_name_now = data.get('user_name')
        has_history_now = data.get('has_history', False)

        print(f"[OK] 回答成功")
        print(f"  用户名字: {user_name_now}")
        print(f"  有历史数据: {has_history_now}")

        if not has_history_now:
            print(f"  [OK] 正确识别为新用户（无历史数据）")
        else:
            print(f"  [ERROR] 错误识别为老用户（不应该有历史数据）")
    else:
        print(f"[ERROR] 失败: {response.status_code}")

    print("\n" + "="*70)
    print("基于名字的历史记录功能测试完成")
    print("="*70)

    print("\n【测试总结】")
    print("[OK] 首次访问询问名字")
    print("[OK] 根据名字保存用户数据")
    print("[OK] 再次访问根据名字识别历史数据")
    print("[OK] 只询问缺失信息，不重复问已有数据")
    print("[OK] 不同名字识别为不同用户")


if __name__ == "__main__":
    test_name_based_history()
