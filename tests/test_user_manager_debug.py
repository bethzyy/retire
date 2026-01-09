#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试UserDataManager的load_user_data函数
"""
import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from user_manager import UserDataManager
import json

def test_load_user_data():
    """测试加载beth用户数据"""

    print("=" * 60)
    print("测试 UserDataManager.load_user_data()")
    print("=" * 60)

    # 创建用户管理器
    manager = UserDataManager(data_dir="user_data")

    # 打印当前工作目录
    print(f"\n当前工作目录: {os.getcwd()}")
    print(f"user_data目录绝对路径: {os.path.abspath('user_data')}")
    print(f"user_data目录是否存在: {os.path.exists('user_data')}")

    # 列出user_data目录中的所有文件
    print(f"\nuser_data目录中的文件:")
    if os.path.exists('user_data'):
        files = os.listdir('user_data')
        for f in files:
            filepath = os.path.join('user_data', f)
            print(f"  - {f} (大小: {os.path.getsize(filepath)} bytes)")

    # 测试加载beth用户数据
    print(f"\n测试加载 beth 用户数据...")
    print(f"- 调用: manager.load_user_data('beth')")

    # 手动调用_get_user_file查看路径
    filepath = manager._get_user_file("beth")
    print(f"_get_user_file返回的路径: {filepath}")
    print(f"文件是否存在: {os.path.exists(filepath)}")

    # 加载用户数据
    user_data = manager.load_user_data("beth")

    print(f"\n返回结果:")
    if user_data:
        print(f"  类型: {type(user_data)}")
        print(f"  键数量: {len(user_data)}")
        print(f"  所有键: {list(user_data.keys())}")
        print(f"\n完整数据:")
        print(json.dumps(user_data, ensure_ascii=False, indent=2))
    else:
        print("  返回None!")

    # 直接使用json.load读取文件进行对比
    print(f"\n直接读取文件进行对比:")
    direct_filepath = os.path.join("user_data", "beth.json")
    print(f"文件路径: {direct_filepath}")
    print(f"文件是否存在: {os.path.exists(direct_filepath)}")

    if os.path.exists(direct_filepath):
        with open(direct_filepath, 'r', encoding='utf-8') as f:
            direct_data = json.load(f)
        print(f"直接读取的键数量: {len(direct_data)}")
        print(f"直接读取的所有键: {list(direct_data.keys())}")

    print("\n" + "=" * 60)
    if user_data and len(user_data) > 3:
        print("测试结果: ✓ 成功 - 数据加载正确")
    else:
        print("测试结果: ✗ 失败 - 数据不完整")
    print("=" * 60)

if __name__ == "__main__":
    test_load_user_data()
