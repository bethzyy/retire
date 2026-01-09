#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试第一条消息
"""

import requests

base_url = "http://localhost:5000"
session = requests.Session()

print("="*70)
print("测试第一条消息 - AI是否询问名字")
print("="*70)

# 发送第一条消息
print("\n发送消息：你好")
response = session.post(
    f"{base_url}/api/chat",
    json={"message": "你好"},
    timeout=30
)

if response.status_code == 200:
    data = response.json()
    if data.get('success'):
        reply = data.get('reply', '')
        print(f"\nAI完整回复：")
        print("-"*70)
        print(reply)
        print("-"*70)

        # 检查是否包含名字问题
        if "名字" in reply and "第1" in reply:
            print("\n✅ 成功！AI询问了名字（第1个问题）")
        elif "名字" in reply:
            print("\n⚠️ AI提到了名字，但问题编号可能不对")
        else:
            print("\n❌ 失败！AI没有询问名字")
    else:
        print(f"错误：{data.get('error')}")
else:
    print(f"HTTP错误：{response.status_code}")

print("\n"+"="*70)
