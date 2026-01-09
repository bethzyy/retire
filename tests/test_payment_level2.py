#!/usr/bin/env python
# -*- coding: utf-8 -*-
import requests
import json
import sys
import io
import time

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

base_url = "http://localhost:5000"

session = requests.Session()

# 设置用户名
session.post(f"{base_url}/api/set-name", json={"name": "测试缴费水平2"}, timeout=10)

# 回答所有问题直到出现缴费水平
answers = [
    "你好",
    "A",  # 性别
    "A",  # 户口
    "1990-06",  # 出生日期
    "A",  # 就业状态(在职)
    "2020",  # 首次工作
    "15",  # 累计年限
    "0",  # 视同
    "15",  # 实际
    "100000",  # 个人账户
    "A",  # 可能还会问就业状态
    "A",  # 可能还会问其他状态
]

for i, answer in enumerate(answers):
    print(f"\n[第{i+1}轮] 发送: {answer}")
    response = session.post(f"{base_url}/api/chat", json={"message": answer}, timeout=30)
    
    if response.status_code == 200:
        data = response.json()
        if data.get('success'):
            reply = data.get('reply', '')
            print(f"AI回复: {reply[:300]}...")
            
            # 检查是否出现缴费水平问题
            if "缴费" in reply and ("档" in reply or "%" in reply):
                print("\n[SUCCESS] 出现缴费水平问题!")
                if "60%" in reply and "100%" in reply and "300%" in reply:
                    print("[SUCCESS] 包含所有档位选项!")
                break
            
            time.sleep(1)
        else:
            print(f"错误: {data.get('error')}")
    else:
        print(f"HTTP错误: {response.status_code}")
