#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
API测试模块
"""

import os
import sys

# 添加上级目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ai_client import GLMClient
from logger import AILogger


def test_ai_client():
    """测试AI客户端"""
    print("\n" + "="*60)
    print("测试AI客户端")
    print("="*60)

    try:
        # 创建客户端
        client = GLMClient()
        print("✓ 客户端初始化成功")
        print(f"  模型: {client.model}")
        print(f"  接口: {client.base_url}")

        # 读取系统提示词
        prompt_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "prompts", "system_prompt.txt")
        with open(prompt_path, 'r', encoding='utf-8') as f:
            system_prompt = f.read()
        print(f"✓ 系统提示词加载成功 ({len(system_prompt)} 字符)")

        # 测试简单对话
        print("\n发送测试消息...")
        response = client.chat(
            user_message="你好，我是1985年出生的北京男性，现在想咨询灵活就业交养老保险的事情。",
            system_prompt=system_prompt
        )

        if "error" in response and response["error"]:
            print(f"✗ API调用失败: {response.get('message', 'Unknown')}")
            return False
        else:
            print("✓ API调用成功")
            if "content" in response and len(response["content"]) > 0:
                content = response["content"][0]
                if "text" in content:
                    print(f"\nAI回复预览:")
                    print("-" * 60)
                    print(content["text"][:200] + "...")
                    print("-" * 60)

        return True

    except Exception as e:
        print(f"✗ 测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_logger():
    """测试日志记录器"""
    print("\n" + "="*60)
    print("测试日志记录器")
    print("="*60)

    try:
        # 创建日志记录器
        logger = AILogger(log_dir="logs")
        print("✓ 日志记录器初始化成功")
        print(f"  日志目录: {logger.log_dir}")

        # 模拟记录日志
        test_response = {
            "content": [
                {
                    "text": "这是测试回复内容。根据您的年龄和缴费情况，建议您选择中档缴费..."
                }
            ]
        }

        log_path = logger.log_call(
            model="glm-4.7",
            system_prompt="测试系统提示词",
            user_message="测试用户消息",
            conversation_history=[],
            response=test_response,
            metadata={"test": True}
        )

        print(f"✓ 日志记录成功: {log_path}")

        # 读取并打印摘要
        logger.print_summary(log_path)

        # 获取最新日志
        latest_logs = logger.get_latest_logs(5)
        print(f"✓ 获取到 {len(latest_logs)} 个日志文件")

        return True

    except Exception as e:
        print(f"✗ 测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_prompts():
    """测试提示词文件"""
    print("\n" + "="*60)
    print("测试提示词文件")
    print("="*60)

    try:
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

        # 测试系统提示词
        system_prompt_path = os.path.join(base_dir, "prompts", "system_prompt.txt")
        if os.path.exists(system_prompt_path):
            with open(system_prompt_path, 'r', encoding='utf-8') as f:
                content = f.read()
            print(f"✓ system_prompt.txt 存在 ({len(content)} 字符)")
        else:
            print(f"✗ system_prompt.txt 不存在")
            return False

        # 测试政策背景
        policy_path = os.path.join(base_dir, "prompts", "policy_context.txt")
        if os.path.exists(policy_path):
            with open(policy_path, 'r', encoding='utf-8') as f:
                content = f.read()
            print(f"✓ policy_context.txt 存在 ({len(content)} 字符)")
        else:
            print(f"✗ policy_context.txt 不存在")
            return False

        return True

    except Exception as e:
        print(f"✗ 测试失败: {str(e)}")
        return False


def main():
    """运行所有测试"""
    print("\n" + "="*60)
    print("北京退休金测算系统 - 测试套件")
    print("="*60)

    results = []

    # 测试提示词文件
    results.append(("提示词文件", test_prompts()))

    # 测试日志记录器
    results.append(("日志记录器", test_logger()))

    # 测试AI客户端
    results.append(("AI客户端", test_ai_client()))

    # 打印测试结果汇总
    print("\n" + "="*60)
    print("测试结果汇总")
    print("="*60)

    for name, passed in results:
        status = "✓ 通过" if passed else "✗ 失败"
        print(f"{name}: {status}")

    total = len(results)
    passed = sum(1 for _, p in results if p)

    print(f"\n总计: {passed}/{total} 通过")
    print("="*60 + "\n")

    return passed == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
