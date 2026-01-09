#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
自动测试程序 - 模拟用户交互
"""

import requests
import json
import time


class RetireCalculationTester:
    """退休金测算系统测试器"""

    def __init__(self, base_url="http://localhost:5000"):
        self.base_url = base_url
        self.session = requests.Session()

    def send_message(self, message):
        """发送消息到AI"""
        try:
            response = self.session.post(
                f"{self.base_url}/api/chat",
                json={"message": message},
                timeout=30
            )
            response.raise_for_status()
            data = response.json()

            if data.get('success'):
                return data.get('reply', '')
            else:
                return f"错误: {data.get('error', 'Unknown error')}"

        except Exception as e:
            return f"异常: {str(e)}"

    def reset_conversation(self):
        """重置对话"""
        try:
            response = self.session.post(
                f"{self.base_url}/api/reset",
                timeout=10
            )
            response.raise_for_status()
            return response.json().get('success', False)
        except:
            return False

    def test_scenario_1(self):
        """测试场景1：40岁男性，2026年失业"""
        print("\n" + "="*70)
        print("测试场景1：40岁男性，2026年1月开始灵活就业")
        print("="*70)

        # 重置对话
        self.reset_conversation()
        time.sleep(1)

        # 模拟对话流程
        messages = [
            "你好，我是1985年出生的北京户口男性，2026年1月失业，想办理灵活就业交养老保险，应该选哪一档？",
            "我之前工作了15年，平均工资8000元左右",
            "没有视同缴费年限，都是实际缴费",
            "我预期寿命到80岁"
        ]

        for i, msg in enumerate(messages, 1):
            print(f"\n[用户第{i}轮]: {msg}")
            print("-" * 70)

            reply = self.send_message(msg)
            print(f"[AI回复]:")

            # 美化输出（处理emoji编码问题）
            if reply:
                try:
                    # 尝试直接打印
                    print(reply)
                except UnicodeEncodeError:
                    # 如果有emoji，替换后打印
                    safe_reply = reply.encode('gbk', errors='ignore').decode('gbk')
                    print(safe_reply)
                    print("(注: 部分特殊字符已过滤)")
            else:
                print("(无回复)")

            # 等待AI处理
            time.sleep(2)

        print("\n" + "="*70)

    def test_scenario_2(self):
        """测试场景2：55岁女性，即将退休"""
        print("\n" + "="*70)
        print("测试场景2：55岁女性，1970年出生，即将退休")
        print("="*70)

        # 重置对话
        self.reset_conversation()
        time.sleep(1)

        messages = [
            "你好，我是1970年6月出生的女性，北京城镇户口，2026年1月失业，想咨询灵活就业缴费问题",
            "我工作了30年，其中有5年视同缴费年限，25年实际缴费",
            "之前平均缴费基数是社平工资的80%"
        ]

        for i, msg in enumerate(messages, 1):
            print(f"\n[用户第{i}轮]: {msg}")
            print("-" * 70)

            reply = self.send_message(msg)
            print(f"[AI回复]:")

            try:
                print(reply)
            except UnicodeEncodeError:
                safe_reply = reply.encode('gbk', errors='ignore').decode('gbk')
                print(safe_reply)
                print("(注: 部分特殊字符已过滤)")

            time.sleep(2)

        print("\n" + "="*70)

    def test_scenario_3(self):
        """测试场景3：快速询问"""
        print("\n" + "="*70)
        print("测试场景3：简单快速咨询")
        print("="*70)

        self.reset_conversation()
        time.sleep(1)

        messages = [
            "灵活就业三档缴费分别是多少？",
            "如果我现在50岁，应该选哪档？"
        ]

        for i, msg in enumerate(messages, 1):
            print(f"\n[用户第{i}轮]: {msg}")
            print("-" * 70)

            reply = self.send_message(msg)
            print(f"[AI回复]:")

            try:
                display_reply = reply[:500] + "..." if len(reply) > 500 else reply
                print(display_reply)
            except UnicodeEncodeError:
                safe_reply = reply.encode('gbk', errors='ignore').decode('gbk')
                display_reply = safe_reply[:500] + "..." if len(safe_reply) > 500 else safe_reply
                print(display_reply)
                print("(注: 部分特殊字符已过滤)")

            time.sleep(2)

        print("\n" + "="*70)

    def analyze_results(self):
        """分析测试结果"""
        print("\n" + "="*70)
        print("测试结果分析")
        print("="*70)

        # 检查是否有日志生成
        import os
        log_dir = os.path.join(os.path.dirname(__file__), "..", "logs")

        if os.path.exists(log_dir):
            log_files = [f for f in os.listdir(log_dir) if f.endswith('.json')]
            log_files.sort(reverse=True)

            print(f"\n生成的日志文件: {len(log_files)} 个")

            if log_files:
                print("\n最新的3个日志:")
                for log_file in log_files[:3]:
                    log_path = os.path.join(log_dir, log_file)
                    try:
                        with open(log_path, 'r', encoding='utf-8') as f:
                            log_data = json.load(f)

                        timestamp = log_data.get('metadata', {}).get('timestamp', 'N/A')
                        has_error = log_data.get('output', {}).get('has_error', False)
                        status = "[失败]" if has_error else "[成功]"

                        print(f"  {status} {log_file}")
                        print(f"       时间: {timestamp}")
                    except Exception as e:
                        print(f"  [错误] {log_file}: {str(e)}")

        print("\n" + "="*70)

    def run_all_tests(self):
        """运行所有测试"""
        print("\n" + "#"*70)
        print("#" + " "*68 + "#")
        print("#" + "  北京退休金测算系统 - 自动化测试程序".center(66) + "#")
        print("#" + " "*68 + "#")
        print("#"*70)

        try:
            # 测试服务器连接
            print("\n[1/5] 检查服务器连接...")
            try:
                response = self.session.get(self.base_url, timeout=5)
                if response.status_code == 200:
                    print("      [OK] 服务器连接正常")
                else:
                    print(f"      [ERROR] 服务器响应异常: {response.status_code}")
                    return
            except Exception as e:
                print(f"      [ERROR] 无法连接到服务器: {str(e)}")
                print(f"      提示: 请确保应用已启动 (python app.py)")
                return

            # 运行测试场景
            print("\n[2/5] 运行测试场景1...")
            self.test_scenario_1()

            print("\n[3/5] 运行测试场景2...")
            self.test_scenario_2()

            print("\n[4/5] 运行测试场景3...")
            self.test_scenario_3()

            print("\n[5/5] 分析测试结果...")
            self.analyze_results()

            print("\n" + "#"*70)
            print("#" + " "*68 + "#")
            print("#" + "  所有测试完成！".center(66) + "#")
            print("#" + " "*68 + "#")
            print("#"*70 + "\n")

        except KeyboardInterrupt:
            print("\n\n测试被用户中断")
        except Exception as e:
            print(f"\n\n测试过程中发生错误: {str(e)}")
            import traceback
            traceback.print_exc()


if __name__ == "__main__":
    tester = RetireCalculationTester()
    tester.run_all_tests()
