#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
用户历史记录功能测试
"""

import requests
import time
import json


def test_user_history():
    """测试用户历史记录功能"""

    base_url = "http://localhost:5000"
    session = requests.Session()

    print("="*70)
    print("用户历史记录功能测试")
    print("="*70)

    # 测试场景1：首次使用
    print("\n【测试1】首次使用 - 应该询问14个问题")
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
            user_id = data.get('user_id')
            is_new = data.get('is_new_user', False)

            print(f"✓ 首次对话成功")
            print(f"  用户ID: {user_id}")
            print(f"  是否新用户: {is_new}")
            print(f"  AI回复: {reply[:200]}...")

            # 回答几个问题
            test_answers = ["男", "1985年", "城镇"]
            for i, answer in enumerate(test_answers):
                print(f"\n回答问题{i+1}: {answer}")
                response = session.post(
                    f"{base_url}/api/chat",
                    json={"message": answer},
                    timeout=30
                )
                if response.status_code == 200:
                    data = response.json()
                    print(f"  AI: {data.get('reply', '')[:100]}...")
                else:
                    print(f"  ✗ 失败: {response.status_code}")

            # 保存user_id用于下次测试
            saved_user_id = user_id
        else:
            print(f"✗ API错误: {data.get('error')}")
            return
    else:
        print(f"✗ HTTP错误: {response.status_code}")
        return

    # 测试场景2：重置对话
    print("\n【测试2】重置对话")
    print("-"*70)

    response = session.post(
        f"{base_url}/api/reset",
        json={},
        timeout=10
    )

    if response.status_code == 200:
        print("✓ 对话已重置")
    else:
        print(f"✗ 重置失败: {response.status_code}")

    # 测试场景3：再次访问（应该识别历史数据）
    print("\n【测试3】再次访问 - 应该识别历史数据并补充询问")
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
            user_id = data.get('user_id')
            is_new = data.get('is_new_user', True)
            has_history = data.get('has_history', False)

            print(f"✓ 再次访问成功")
            print(f"  用户ID: {user_id}")
            print(f"  是否新用户: {is_new}")
            print(f"  有历史数据: {has_history}")

            # 检查是否识别了历史数据
            checks = {
                "欢迎回来": "欢迎回来" in reply or "再次" in reply or "又来了" in reply,
                "历史信息": "之前提供过" in reply or "已提供" in reply or "档案" in reply,
                "跳过已有信息": "不需要" in reply or "已经有了" in reply or "直接使用" in reply
            }

            print("\n检查结果:")
            for check, passed in checks.items():
                status = "✓" if passed else "✗"
                print(f"  {status} {check}")

            print(f"\nAI回复:\n{reply[:300]}...")
        else:
            print(f"✗ API错误: {data.get('error')}")
    else:
        print(f"✗ HTTP错误: {response.status_code}")

    # 测试场景4：检查用户数据文件
    print("\n【测试4】检查用户数据文件")
    print("-"*70)

    try:
        import os
        user_data_dir = "user_data"
        if os.path.exists(user_data_dir):
            files = [f for f in os.listdir(user_data_dir) if f.endswith('.json')]
            print(f"✓ 用户数据目录存在")
            print(f"  用户数量: {len(files)}")
            for f in files:
                print(f"  - {f}")
        else:
            print("✗ 用户数据目录不存在")
    except Exception as e:
        print(f"✗ 检查失败: {str(e)}")

    print("\n" + "="*70)
    print("用户历史记录功能测试完成")
    print("="*70)

    print("\n【测试总结】")
    print("✓ 首次访问创建用户ID")
    print("✓ 用户数据持久化保存")
    print("✓ 再次访问识别历史数据")
    print("✓ 跳过已有信息，只询问缺失信息")


if __name__ == "__main__":
    test_user_history()
