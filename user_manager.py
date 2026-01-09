#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
用户数据管理模块
保存和读取用户的历史信息
"""

import os
import json
from datetime import datetime
from typing import Dict, Optional


class UserDataManager:
    """用户数据管理器"""

    def __init__(self, data_dir: str = "user_data"):
        """
        初始化用户数据管理器

        Args:
            data_dir: 用户数据存储目录
        """
        self.data_dir = data_dir

        # 确保目录存在
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)

    def _get_user_file(self, user_name: str) -> str:
        """
        获取用户数据文件路径

        Args:
            user_name: 用户名字（作为唯一标识）

        Returns:
            用户数据文件路径
        """
        # 将名字作为文件名，移除特殊字符
        safe_name = "".join(c for c in user_name if c.isalnum() or c in (' ', '-', '_'))
        filepath = os.path.join(self.data_dir, f"{safe_name}.json")
        # 使用绝对路径
        filepath = os.path.abspath(filepath)
        print(f"[DEBUG] _get_user_file: user_name={user_name}, safe_name={safe_name}, filepath={filepath}")
        print(f"[DEBUG] _get_user_file: current working directory={os.getcwd()}")
        print(f"[DEBUG] _get_user_file: data_dir={self.data_dir}, absolute={os.path.abspath(self.data_dir)}")
        return filepath

    def save_user_data(self, user_name: str, user_data: Dict) -> str:
        """
        保存用户数据

        Args:
            user_name: 用户名字
            user_data: 用户数据字典

        Returns:
            保存的文件路径
        """
        filepath = self._get_user_file(user_name)

        # 添加更新时间和用户名
        user_data['user_name'] = user_name
        user_data['last_updated'] = datetime.now().isoformat()

        # 如果文件存在，保留创建时间
        if os.path.exists(filepath):
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    old_data = json.load(f)
                    user_data['created_at'] = old_data.get('created_at', datetime.now().isoformat())
            except:
                user_data['created_at'] = datetime.now().isoformat()
        else:
            user_data['created_at'] = datetime.now().isoformat()

        # 保存数据
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(user_data, f, ensure_ascii=False, indent=2)

        return filepath

    def load_user_data(self, user_name: str) -> Optional[Dict]:
        """
        加载用户数据

        Args:
            user_name: 用户名字

        Returns:
            用户数据字典，如果不存在返回None
        """
        filepath = self._get_user_file(user_name)
        print(f"[DEBUG] UserDataManager.load_user_data: user_name = {user_name}")
        print(f"[DEBUG] UserDataManager.load_user_data: filepath = {filepath}")
        print(f"[DEBUG] UserDataManager.load_user_data: file exists = {os.path.exists(filepath)}")

        if not os.path.exists(filepath):
            return None

        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
                print(f"[DEBUG] UserDataManager.load_user_data: loaded keys = {list(data.keys())}")
                return data
        except Exception as e:
            print(f"加载用户数据失败: {str(e)}")
            return None

    def get_missing_fields(self, user_data: Dict) -> list:
        """
        获取缺失的字段

        Args:
            user_data: 用户数据字典

        Returns:
            缺失字段名称列表
        """
        required_fields = {
            # 基础信息
            'gender': '性别',
            'birth_year': '出生年份',
            'birth_month': '出生月份',
            'hukou_type': '户口性质（城镇/农村）',
            'unemployment_status': '当前失业状态',
            'unemployment_start': '失业开始时间',
            'retirement_age': '预计退休年龄',

            # 工作经历
            'first_work_year': '首次工作时间',
            'total_work_years': '累计工作年限',
            'actual_years': '实际缴费年限',

            # 其他信息
            'account_balance': '个人账户余额',
            'special_title': '高级职称'
        }

        # 以下字段不属于用户必填信息,而是AI搜索或用户提供的数据
        # 不在required_fields中,避免AI重复询问:
        # - 'social_avg_wage': 社平工资(元/月)
        # - 'flex_payment_bases': 灵活就业养老保险缴费基数上下限
        # - 'flex_monthly_payments': 灵活就业养老保险月缴费额(低/中/高档)

        missing = []
        for field, name in required_fields.items():
            if field not in user_data or user_data[field] is None or user_data[field] == '':
                missing.append((field, name))

        return missing

    def merge_user_data(self, old_data: Dict, new_data: Dict) -> Dict:
        """
        合并用户数据

        Args:
            old_data: 旧的用户数据
            new_data: 新的用户数据

        Returns:
            合并后的用户数据
        """
        merged = old_data.copy()

        # 只更新有值的字段
        for key, value in new_data.items():
            if value is not None and value != '':
                merged[key] = value

        # 更新时间戳
        merged['last_updated'] = datetime.now().isoformat()

        return merged

    def list_all_users(self) -> list:
        """
        列出所有用户

        Returns:
            用户信息列表
        """
        users = []

        for filename in os.listdir(self.data_dir):
            if filename.endswith('.json'):
                try:
                    filepath = os.path.join(self.data_dir, filename)
                    with open(filepath, 'r', encoding='utf-8') as f:
                        data = json.load(f)

                    user_id = filename[:-5]  # 去掉.json后缀
                    users.append({
                        'user_id': user_id,
                        'created_at': data.get('created_at', ''),
                        'last_updated': data.get('last_updated', ''),
                        'gender': data.get('gender', ''),
                        'birth_year': data.get('birth_year', ''),
                        'has_data': len([k for k in data.keys() if k not in ['created_at', 'last_updated']]) > 0
                    })
                except Exception as e:
                    print(f"读取用户文件失败 {filename}: {str(e)}")

        # 按更新时间排序
        users.sort(key=lambda x: x['last_updated'], reverse=True)

        return users

    def delete_user_data(self, user_name: str) -> bool:
        """
        删除用户数据

        Args:
            user_name: 用户名字

        Returns:
            是否删除成功
        """
        filepath = self._get_user_file(user_name)

        if os.path.exists(filepath):
            try:
                os.remove(filepath)
                return True
            except Exception as e:
                print(f"删除用户数据失败: {str(e)}")
                return False

        return False


if __name__ == "__main__":
    # 测试代码
    manager = UserDataManager()

    # 测试保存
    test_user_name = "张三"
    test_data = {
        'gender': '男',
        'birth_year': '1985',
        'birth_month': '1',
        'hukou_type': '城镇',
        'unemployment_status': '失业',
        'unemployment_start': '2026-01',
        'retirement_age': '60'
    }

    filepath = manager.save_user_data(test_user_name, test_data)
    print(f"[OK] 用户数据已保存: {filepath}")

    # 测试加载
    loaded_data = manager.load_user_data(test_user_name)
    print(f"[OK] 用户数据已加载: {loaded_data}")

    # 测试缺失字段
    missing = manager.get_missing_fields(loaded_data)
    print(f"[OK] 缺失字段: {missing}")

    # 测试列表所有用户
    users = manager.list_all_users()
    print(f"[OK] 所有用户 ({len(users)} 个):")
    for user in users:
        print(f"  - {user['user_id']}: {user['gender']}, {user['birth_year']}")
