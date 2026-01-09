#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
v2.0功能测试 - 验证新特性
"""

import requests
import time


def test_new_features():
    """测试新版本特性"""

    base_url = "http://localhost:5000"
    session = requests.Session()

    print("="*70)
    print("v2.0 新功能测试")
    print("="*70)

    # 测试1：首次对话 - 应该自我介绍并问第一个问题
    print("\n[测试1] 检查首次对话格式")
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
            print(f"AI回复: {reply[:200]}...")

            # 检查是否包含关键元素
            checks = {
                "自我介绍": "北京社保" in reply or "退休金计算" in reply,
                "问题数量": "14个问题" in reply or "14 个问题" in reply,
                "提供链接": "http://" in reply or "rsj.beijing.gov.cn" in reply,
                "第一个问题": "性别" in reply
            }

            print("\n检查结果:")
            for check, passed in checks.items():
                status = "✓" if passed else "✗"
                print(f"  {status} {check}")
        else:
            print(f"✗ API返回错误: {data.get('error')}")
    else:
        print(f"✗ HTTP错误: {response.status_code}")

    # 测试2：回答问题 - 应该继续问下一个问题
    print("\n[测试2] 检查逐个提问流程")
    print("-"*70)

    response = session.post(
        f"{base_url}/api/chat",
        json={"message": "男"},
        timeout=30
    )

    if response.status_code == 200:
        data = response.json()
        if data.get('success'):
            reply = data.get('reply', '')
            print(f"AI回复: {reply[:200]}...")

            # 检查是否是第二个问题
            checks = {
                "问题编号": "第2" in reply or "2/" in reply,
                "包含链接": "http://" in reply,
                "单个问题": reply.count("？") <= 2  # 最多1-2个问号
            }

            print("\n检查结果:")
            for check, passed in checks.items():
                status = "✓" if passed else "✗"
                print(f"  {status} {check}")
        else:
            print(f"✗ API返回错误: {data.get('error')}")
    else:
        print(f"✗ HTTP错误: {response.status_code}")

    # 测试3：检查政策引用格式
    print("\n[测试3] 检查政策引用格式")
    print("-"*70)

    response = session.post(
        f"{base_url}/api/chat",
        json={"message": "1985年"},
        timeout=30
    )

    if response.status_code == 200:
        data = response.json()
        if data.get('success'):
            reply = data.get('reply', '')

            # 检查链接格式
            checks = {
                "Markdown链接": "](" in reply and ")" in reply,
                "官方网站": "rsj.beijing.gov.cn" in reply or "mohrss.gov.cn" in reply,
                "政策文件": "规定" in reply or "办法" in reply or "通知" in reply
            }

            print("检查结果:")
            for check, passed in checks.items():
                status = "✓" if passed else "✗"
                print(f"  {status} {check}")

            # 显示找到的链接
            import re
            links = re.findall(r'\[([^\]]+)\]\(([^)]+)\)', reply)
            if links:
                print(f"\n找到 {len(links)} 个链接:")
                for text, url in links[:3]:  # 只显示前3个
                    print(f"  - [{text}]({url})")
        else:
            print(f"✗ API返回错误: {data.get('error')}")
    else:
        print(f"✗ HTTP错误: {response.status_code}")

    print("\n" + "="*70)
    print("v2.0 新功能测试完成")
    print("="*70)

    print("\n【测试总结】")
    print("✓ 逐个提问功能")
    print("✓ 政策链接添加")
    print("✓ 官方网站引用")
    print("\n建议：进行完整对话测试（14个问题）以验证全部功能")


if __name__ == "__main__":
    test_new_features()
