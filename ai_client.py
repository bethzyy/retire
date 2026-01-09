#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
GLM AI客户端 - 使用Anthropic兼容接口调用智谱AI
"""

import os
import json
import time
from datetime import datetime
from typing import List, Dict, Optional
import requests


class GLMClient:
    """GLM-4.7客户端，使用Anthropic兼容接口"""

    def __init__(self):
        """初始化客户端"""
        # 从系统变量读取API Key
        self.api_key = os.environ.get('ZHIPU_API_KEY')
        if not self.api_key:
            raise ValueError(
                "未找到ZHIPU_API_KEY环境变量！\n"
                "请先设置环境变量：\n"
                "Windows CMD: set ZHIPU_API_KEY=your_api_key\n"
                "Windows PowerShell: $env:ZHIPU_API_KEY='your_api_key'\n"
                "Linux/Mac: export ZHIPU_API_KEY=your_api_key"
            )

        # Anthropic兼容接口地址
        self.base_url = "https://open.bigmodel.cn/api/anthropic/v1/messages"

        # 模型配置
        self.model = "glm-4.7"  # 使用GLM-4.7模型
        self.max_tokens = 8192
        self.temperature = 0.7

    def create_message(
        self,
        messages: List[Dict[str, str]],
        system_prompt: Optional[str] = None,
        stream: bool = False
    ) -> Dict:
        """
        调用GLM-4.7模型（Anthropic兼容接口）

        Args:
            messages: 消息列表 [{"role": "user", "content": "..."}]
            system_prompt: 系统提示词（可选）
            stream: 是否使用流式输出

        Returns:
            响应字典
        """
        # 构建请求头
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "anthropic-version": "2023-06-01"
        }

        # 构建请求体
        payload = {
            "model": self.model,
            "max_tokens": self.max_tokens,
            "temperature": self.temperature,
            "messages": messages
        }

        # 添加系统提示词
        if system_prompt:
            payload["system"] = system_prompt

        # 流式输出标志
        if stream:
            payload["stream"] = True

        try:
            # 发送请求（超时时间增加到120秒，避免Chrome浏览器兼容性问题）
            response = requests.post(
                self.base_url,
                headers=headers,
                json=payload,
                timeout=120  # 增加到120秒，适配不同浏览器的API调用
            )
            response.raise_for_status()

            return response.json()

        except requests.exceptions.RequestException as e:
            return {
                "error": True,
                "message": f"API请求失败: {str(e)}",
                "details": str(e)
            }

    def chat(
        self,
        user_message: str,
        conversation_history: Optional[List[Dict[str, str]]] = None,
        system_prompt: Optional[str] = None,
        images: Optional[List[str]] = None
    ) -> Dict:
        """
        简化的对话接口，支持图片

        Args:
            user_message: 用户消息
            conversation_history: 对话历史（可选）
            system_prompt: 系统提示词（可选）
            images: 图片列表（base64编码，可选）

        Returns:
            响应字典
        """
        # 构建消息列表
        messages = conversation_history[:] if conversation_history else []

        # 如果有图片，构建多模态消息
        if images:
            content = []
            # 添加文本
            content.append({
                "type": "text",
                "text": user_message
            })
            # 添加图片
            for img_data in images:
                # 移除data:image/xxx;base64,前缀
                if "," in img_data:
                    img_base64 = img_data.split(",", 1)[1]
                else:
                    img_base64 = img_data

                content.append({
                    "type": "image",
                    "source": {
                        "type": "base64",
                        "media_type": "image/jpeg",
                        "data": img_base64
                    }
                })

            messages.append({"role": "user", "content": content})
        else:
            # 纯文本消息
            messages.append({"role": "user", "content": user_message})

        # 调用API
        return self.create_message(messages, system_prompt)


if __name__ == "__main__":
    # 测试代码
    print("GLM客户端测试\n")

    try:
        # 创建客户端
        client = GLMClient()
        print(f"✓ 客户端初始化成功")
        print(f"✓ API Key: {client.api_key[:10]}...")
        print(f"✓ 模型: {client.model}")
        print(f"✓ 接口地址: {client.base_url}\n")

        # 读取系统提示词
        system_prompt_path = "prompts/system_prompt.txt"
        if os.path.exists(system_prompt_path):
            with open(system_prompt_path, 'r', encoding='utf-8') as f:
                system_prompt = f.read()
            print(f"✓ 已加载系统提示词 ({len(system_prompt)} 字符)\n")
        else:
            system_prompt = None
            print(f"✗ 未找到系统提示词文件\n")

        # 测试对话
        print("发送测试消息...")
        response = client.chat(
            user_message="你好，我是北京户口，1980年出生，男性，现在失业了，想咨询灵活就业交养老保险的问题。",
            system_prompt=system_prompt
        )

        # 打印响应
        if "error" in response and response["error"]:
            print(f"\n✗ 错误: {response['message']}")
        else:
            print(f"\n✓ 响应成功:")
            print(json.dumps(response, ensure_ascii=False, indent=2))

    except Exception as e:
        print(f"\n✗ 测试失败: {str(e)}")
