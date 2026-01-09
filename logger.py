#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
日志模块 - 记录AI调用全流程和用户对话历史
"""

import os
import json
from datetime import datetime
from typing import Dict, Any, Optional


class AILogger:
    """AI调用日志记录器"""

    def __init__(self, log_dir: str = "logs"):
        """
        初始化日志记录器

        Args:
            log_dir: 日志目录路径
        """
        self.log_dir = log_dir

        # 确保日志目录存在
        if not os.path.exists(self.log_dir):
            os.makedirs(self.log_dir)

        # 创建用户对话日志目录
        self.conversation_log_dir = os.path.join(self.log_dir, "conversations")
        if not os.path.exists(self.conversation_log_dir):
            os.makedirs(self.conversation_log_dir)

    def log_call(
        self,
        model: str,
        system_prompt: str,
        user_message: str,
        conversation_history: list,
        response: Dict[str, Any],
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        记录完整的AI调用过程

        Args:
            model: 模型名称
            system_prompt: 系统提示词
            user_message: 用户消息
            conversation_history: 对话历史
            response: AI响应
            metadata: 额外的元数据

        Returns:
            日志文件路径
        """
        # 生成时间戳
        timestamp = datetime.now()
        timestamp_str = timestamp.strftime("%Y%m%d_%H%M%S")

        # 生成日志文件名
        log_filename = f"ai_call_{timestamp_str}.json"
        log_filepath = os.path.join(self.log_dir, log_filename)

        # 构建日志数据
        log_data = {
            "metadata": {
                "timestamp": timestamp.isoformat(),
                "model": model,
                "log_file": log_filename
            },
            "input": {
                "system_prompt": system_prompt,
                "user_message": user_message,
                "conversation_history": conversation_history,
                "metadata": metadata or {}
            },
            "output": {
                "response": response,
                "has_error": "error" in response and response["error"]
            },
            "statistics": {
                "system_prompt_length": len(system_prompt) if system_prompt else 0,
                "user_message_length": len(user_message),
                "conversation_turns": len(conversation_history) if conversation_history else 0,
                "response_length": len(str(response))
            }
        }

        # 如果响应中有内容，提取并计算token估算
        if response and not response.get("error"):
            try:
                # 尝试提取AI回复内容
                if "content" in response and len(response["content"]) > 0:
                    content = response["content"][0]
                    if "text" in content:
                        log_data["statistics"]["ai_response_length"] = len(content["text"])
                        log_data["output"]["ai_response_text"] = content["text"]
            except Exception as e:
                log_data["statistics"]["parse_error"] = str(e)

        # 写入日志文件
        with open(log_filepath, 'w', encoding='utf-8') as f:
            json.dump(log_data, f, ensure_ascii=False, indent=2)

        return log_filepath

    def log_conversation(
        self,
        user_name: str,
        user_message: str,
        ai_reply: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        记录用户对话到专门的日志文件（追加模式）

        Args:
            user_name: 用户名
            user_message: 用户消息
            ai_reply: AI回复
            metadata: 额外的元数据

        Returns:
            日志文件路径
        """
        # 生成用户对话日志文件名（按用户名和日期）
        timestamp = datetime.now()
        date_str = timestamp.strftime("%Y-%m-%d")

        # 清理用户名（移除特殊字符）
        safe_username = "".join(c if c.isalnum() or c in ('-', '_') else '_' for c in user_name)
        log_filename = f"conversation_{safe_username}_{date_str}.txt"
        log_filepath = os.path.join(self.conversation_log_dir, log_filename)

        # 构建日志条目（纯文本格式，便于阅读）
        log_entry = f"""
{'='*80}
时间: {timestamp.strftime("%Y-%m-%d %H:%M:%S")}
用户: {user_name}
{'='*80}

【用户消息】
{user_message}

【AI回复】
{ai_reply}

{'-'*80}

"""

        # 追加写入日志文件
        with open(log_filepath, 'a', encoding='utf-8') as f:
            f.write(log_entry)

        return log_filepath

    def get_latest_logs(self, limit: int = 10) -> list:
        """
        获取最近的日志文件列表

        Args:
            limit: 返回的日志数量

        Returns:
            日志文件路径列表（按时间倒序）
        """
        # 获取所有日志文件
        log_files = []
        for filename in os.listdir(self.log_dir):
            if filename.startswith("ai_call_") and filename.endswith(".json"):
                filepath = os.path.join(self.log_dir, filename)
                log_files.append(filepath)

        # 按修改时间排序（最新的在前）
        log_files.sort(key=lambda x: os.path.getmtime(x), reverse=True)

        return log_files[:limit]

    def read_log(self, log_filepath: str) -> Dict[str, Any]:
        """
        读取日志文件

        Args:
            log_filepath: 日志文件路径

        Returns:
            日志数据字典
        """
        with open(log_filepath, 'r', encoding='utf-8') as f:
            return json.load(f)

    def print_summary(self, log_filepath: str):
        """
        打印日志摘要

        Args:
            log_filepath: 日志文件路径
        """
        log_data = self.read_log(log_filepath)

        print("\n" + "="*60)
        print("AI调用日志摘要")
        print("="*60)

        # 元数据
        meta = log_data["metadata"]
        print(f"\n时间: {meta['timestamp']}")
        print(f"模型: {meta['model']}")
        print(f"日志文件: {meta['log_file']}")

        # 统计信息
        stats = log_data["statistics"]
        print(f"\n系统提示词长度: {stats['system_prompt_length']} 字符")
        print(f"用户消息长度: {stats['user_message_length']} 字符")
        print(f"对话轮次: {stats['conversation_turns']}")

        # 是否有错误
        if log_data["output"]["has_error"]:
            print("\n✗ 调用失败")
            response = log_data["output"]["response"]
            print(f"错误信息: {response.get('message', 'Unknown')}")
        else:
            print("\n✓ 调用成功")
            if "ai_response_length" in stats:
                print(f"AI回复长度: {stats['ai_response_length']} 字符")

        print("="*60 + "\n")


if __name__ == "__main__":
    # 测试代码
    print("日志模块测试\n")

    # 创建日志记录器
    logger = AILogger()
    print(f"✓ 日志目录: {logger.log_dir}")

    # 模拟一次AI调用
    test_log_data = {
        "model": "glm-4.7",
        "system_prompt": "你是一个助手",
        "user_message": "你好",
        "conversation_history": [],
        "response": {
            "content": [{"text": "你好！有什么我可以帮助你的吗？"}]
        },
        "metadata": {"test": True}
    }

    # 记录日志
    log_path = logger.log_call(**test_log_data)
    print(f"✓ 日志已保存: {log_path}")

    # 打印摘要
    logger.print_summary(log_path)

    # 获取最新日志列表
    latest_logs = logger.get_latest_logs(5)
    print(f"✓ 最近的日志文件 ({len(latest_logs)} 个):")
    for log in latest_logs:
        print(f"  - {log}")
