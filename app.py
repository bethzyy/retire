#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
北京退休金测算系统 - Flask Web应用
"""

import os
import sys
import json
from datetime import datetime
from flask import Flask, render_template, request, jsonify, session
from ai_client import GLMClient
from logger import AILogger
from user_manager import UserDataManager


# 创建Flask应用
app = Flask(__name__)
app.secret_key = 'retire-calculator-secret-key-2025'  # 用于session加密

# 初始化AI客户端、日志记录器和用户数据管理器
ai_client = GLMClient()
logger = AILogger(log_dir="logs")
user_manager = UserDataManager(data_dir="user_data")


def load_system_prompt():
    """加载系统提示词"""
    prompt_path = os.path.join(os.path.dirname(__file__), "prompts", "system_prompt.txt")
    try:
        with open(prompt_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        print(f"警告: 无法加载系统提示词 - {str(e)}")
        return "你是一位专业的北京社保和退休金计算专家。"


def load_policy_context():
    """加载政策背景信息"""
    policy_path = os.path.join(os.path.dirname(__file__), "prompts", "policy_context.txt")
    try:
        with open(policy_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        print(f"警告: 无法加载政策背景 - {str(e)}")
        return ""


@app.route('/')
def index():
    """首页"""
    return render_template('index.html')


@app.route('/api/set-name', methods=['POST'])
def set_name():
    """
    设置用户名字到session
    """
    try:
        data = request.get_json()
        user_name = data.get('name', '').strip()

        if not user_name:
            return jsonify({
                'success': False,
                'error': '名字不能为空'
            }), 400

        # 保存到session
        session['user_name'] = user_name

        # 创建或加载用户数据文件
        existing_data = user_manager.load_user_data(user_name)
        print(f"[DEBUG] /api/set-name: user_name = {user_name}")
        print(f"[DEBUG] /api/set-name: existing_data = {existing_data}")
        print(f"[DEBUG] /api/set-name: existing_data keys = {list(existing_data.keys()) if existing_data else 'None'}")

        if not existing_data:
            user_manager.save_user_data(user_name, {
                'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'user_name': user_name
            })
            print(f"[INFO] 创建新用户数据文件: {user_name}")
        else:
            print(f"[INFO] 加载现有用户数据: {user_name}")
            session['has_history'] = True

        return jsonify({
            'success': True,
            'user_name': user_name,
            'has_history': bool(existing_data)
        })

    except Exception as e:
        print(f"错误: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': f'服务器错误: {str(e)}'
        }), 500


@app.route('/api/chat', methods=['POST'])
def chat():
    """
    聊天接口
    接收用户消息，返回AI回复
    支持用户历史数据记录和读取
    """
    try:
        # 获取请求数据
        data = request.get_json()
        user_message = data.get('message', '').strip()
        uploaded_images = data.get('images', [])  # 获取上传的图片

        if not user_message and not uploaded_images:
            return jsonify({
                'success': False,
                'error': '消息或图片不能为空'
            }), 400

        # 获取或创建用户名字
        user_name = session.get('user_name')

        # 如果还没有用户名字，尝试从对话历史中提取
        if not user_name:
            conversation_history = session.get('conversation_history', [])
            # 简单实现：检查对话历史中是否有名字
            for msg in reversed(conversation_history):
                if msg.get('role') == 'assistant' and '请问您的名字是' in msg.get('content', ''):
                    # AI问过名字，检查用户的下一条回复
                    msg_index = conversation_history.index(msg)
                    if msg_index + 1 < len(conversation_history):
                        user_reply = conversation_history[msg_index + 1]
                        if user_reply.get('role') == 'user':
                            # 提取用户回复的名字（去除可能的标点符号）
                            extracted_name = user_reply.get('content', '').strip().rstrip('。，,.!！')
                            if extracted_name and len(extracted_name) <= 20:  # 合理的名字长度
                                user_name = extracted_name
                                session['user_name'] = user_name
                                session['name_extracted'] = True

                                # 创建初始用户数据文件（如果不存在）
                                existing_data = user_manager.load_user_data(user_name)
                                if not existing_data:
                                    user_manager.save_user_data(user_name, {})
                                    print(f"[INFO] 创建新用户数据文件: {user_name}")
                    break

        # 尝试加载用户历史数据（如果有名字）
        user_data = {}
        if user_name:
            user_data = user_manager.load_user_data(user_name) or {}
            session['has_history'] = bool(user_data)
        else:
            session['has_history'] = False

        # 如果是老用户，添加历史数据提示到系统提示词
        system_prompt = load_system_prompt()
        policy_context = load_policy_context()

        # 如果用户有历史数据，在系统提示词中说明
        if user_data and session.get('has_history'):
            history_info = "\n\n## 用户历史数据\n"
            history_info += f"该用户（名字：{user_name}）之前已经提供过以下信息，请直接使用这些数据，并用名字称呼用户：\n"

            # 列出已有的数据
            for key, value in user_data.items():
                if key not in ['created_at', 'last_updated', 'user_name'] and value:
                    # 将key转换为可读名称
                    field_names = {
                        'gender': '性别',
                        'birth_year': '出生年份',
                        'birth_month': '出生月份',
                        'hukou_type': '户口性质',
                        'unemployment_status': '失业状态',
                        'unemployment_start': '失业开始时间',
                        'retirement_age': '退休年龄',
                        'first_work_year': '首次工作时间',
                        'total_work_years': '累计工作年限',
                        'actual_years': '实际缴费年限',
                        'account_balance': '个人账户余额',
                        'special_title': '高级职称',
                        # 社保数据(非必填,AI搜索或用户提供)
                        'social_avg_wage': '社平工资(元/月)',
                        'flex_payment_bases': '灵活就业缴费基数上下限',
                        'flex_monthly_payments': '灵活就业月缴费额(低/中/高档)'
                    }
                    if key in field_names:
                        history_info += f"- {field_names[key]}: {value}\n"

            # 计算缺失字段
            missing_fields = user_manager.get_missing_fields(user_data)
            if missing_fields:
                history_info += f"\n还需要收集的信息（{len(missing_fields)}个）：\n"
                for field, name in missing_fields:
                    history_info += f"- {name}\n"
                history_info += "\n请继续询问缺失的信息，不要重复问已有信息。"

            # 将历史信息插入到系统提示词
            system_prompt = history_info + "\n\n" + system_prompt
        # 如果是新用户（有名字但无历史数据），也要告诉AI用户的名字
        elif user_name and (not user_data or not session.get('has_history')):
            name_info = f"\n\n## 当前用户信息\n"
            name_info += f"用户名字：{user_name}\n"
            name_info += f"该用户是新用户，还没有历史数据。请用名字称呼用户，从第1个问题（性别）开始询问。\n"
            system_prompt = name_info + "\n\n" + system_prompt

        # 组合系统提示词
        current_date = datetime.now().strftime("%Y年%m月%d日")

        full_system_prompt = f"## 📅 当前日期\n今天是：{current_date}\n\n所有时间计算请基于这个日期进行。\n\n"
        full_system_prompt += system_prompt

        if policy_context:
            full_system_prompt += f"\n\n## 政策背景参考\n{policy_context}"

        # 如果用户上传了图片，添加图片识别指令
        if uploaded_images:
            full_system_prompt += "\n\n## ⚠️ 图片识别要求\n"
            full_system_prompt += "用户上传了图片（可能是保险截图或相关文件）。\n"
            full_system_prompt += "请严格按照以下要求处理：\n"
            full_system_prompt += "1. **仔细识别图片中的所有文字和数据**\n"
            full_system_prompt += "2. **只能使用图片中明确显示的信息**，绝对不能猜测或假设\n"
            full_system_prompt += "3. **如果图片模糊或不清楚，明确告诉用户需要更清晰的图片**\n"
            full_system_prompt += "4. **如果图片中缺少关键信息，向用户询问**，不要自己编造\n"
            full_system_prompt += "5. **识别出的每个数据都要说明来源**：例如'从图片中可以看到您的姓名是XXX'\n"
            full_system_prompt += "6. **基于北京社保真实政策进行计算和分析**，提供官方政策链接\n"
            full_system_prompt += "7. **不确定的信息必须向用户确认**，宁可多问也不要猜测\n"
            full_system_prompt += "8. **计算过程必须透明**，展示每个步骤和公式来源\n"

            # 修改用户消息，说明包含图片
            if user_message:
                user_message = f"[用户上传了{len(uploaded_images)}张图片]\n{user_message}"
            else:
                user_message = f"[用户上传了{len(uploaded_images)}张图片，请识别其中的信息]"

        # 获取对话历史
        conversation_history = session.get('conversation_history', [])

        # 调用AI
        response = ai_client.chat(
            user_message=user_message,
            conversation_history=conversation_history,
            system_prompt=full_system_prompt,
            images=uploaded_images if uploaded_images else None
        )

        # 记录日志
        logger.log_call(
            model=ai_client.model,
            system_prompt=full_system_prompt,
            user_message=user_message,
            conversation_history=conversation_history,
            response=response,
            metadata={
                'ip': request.remote_addr,
                'user_agent': request.headers.get('User-Agent', ''),
                'user_name': user_name or '(未知)',
                'has_history': session.get('has_history', False)
            }
        )

        # 检查是否有错误
        if 'error' in response and response['error']:
            return jsonify({
                'success': False,
                'error': response.get('message', 'AI调用失败')
            }), 500

        # 提取AI回复
        ai_reply = ''
        try:
            if 'content' in response and len(response['content']) > 0:
                content = response['content'][0]
                if 'text' in content:
                    ai_reply = content['text']
        except Exception as e:
            print(f"警告: 解析AI响应失败 - {str(e)}")
            ai_reply = str(response)

        # 尝试从AI回复中提取DATA_UPDATE块并保存用户数据
        if user_name and 'DATA_UPDATE:' in ai_reply:
            try:
                # 提取DATA_UPDATE块（更简单的方法：找到DATA_UPDATE:后的所有内容）
                # 找到DATA_UPDATE:的位置
                data_update_start = ai_reply.find('DATA_UPDATE:')
                if data_update_start != -1:
                    # 从DATA_UPDATE:后开始查找JSON的开始和结束
                    json_start = ai_reply.find('{', data_update_start)
                    if json_start != -1:
                        # 从{开始，找到匹配的}
                        brace_count = 0
                        json_end = -1
                        for i in range(json_start, len(ai_reply)):
                            if ai_reply[i] == '{':
                                brace_count += 1
                            elif ai_reply[i] == '}':
                                brace_count -= 1
                                if brace_count == 0:
                                    json_end = i + 1
                                    break

                        if json_end != -1:
                            json_str = ai_reply[json_start:json_end]
                            # 解析JSON
                            new_data = json.loads(json_str)

                            # 加载现有数据
                            existing_data = user_manager.load_user_data(user_name) or {}

                            # 详细日志：保存前和保存后的数据
                            print(f"[DEBUG] 用户 {user_name} 数据更新:")
                            print(f"[DEBUG] - 新数据字段: {list(new_data.keys())}")
                            print(f"[DEBUG] - 保存前已有字段: {list(existing_data.keys())}")

                            # 合并数据
                            updated_data = user_manager.merge_user_data(existing_data, new_data)

                            print(f"[DEBUG] - 保存后共有字段: {list(updated_data.keys())}")

                            # 保存更新后的数据
                            user_manager.save_user_data(user_name, updated_data)

                            print(f"[INFO] 已保存用户数据更新: {user_name} - {list(new_data.keys())}")
            except Exception as e:
                print(f"[WARNING] 保存用户数据失败: {str(e)}")
                import traceback
                traceback.print_exc()

        # 更新对话历史
        conversation_history.append({
            'role': 'user',
            'content': user_message
        })
        conversation_history.append({
            'role': 'assistant',
            'content': ai_reply
        })

        # 限制历史记录长度（保留最近20轮）
        if len(conversation_history) > 40:
            conversation_history = conversation_history[-40:]

        session['conversation_history'] = conversation_history

        # 再次尝试提取名字（在更新对话历史后）
        # 因为用户的回答现在才在历史中
        if not session.get('user_name'):
            for msg in reversed(conversation_history):
                if msg.get('role') == 'assistant' and '请问您的名字是' in msg.get('content', ''):
                    # AI问过名字，检查用户的下一条回复
                    msg_index = conversation_history.index(msg)
                    if msg_index + 1 < len(conversation_history):
                        user_reply = conversation_history[msg_index + 1]
                        if user_reply.get('role') == 'user':
                            # 提取用户回复的名字（去除可能的标点符号）
                            extracted_name = user_reply.get('content', '').strip().rstrip('。，,.!！')
                            if extracted_name and len(extracted_name) <= 20:  # 合理的名字长度
                                session['user_name'] = extracted_name
                                session['name_extracted'] = True
                                user_name = extracted_name

                                # 创建初始用户数据文件（如果不存在）
                                existing_data = user_manager.load_user_data(user_name)
                                if not existing_data:
                                    user_manager.save_user_data(user_name, {})
                                    print(f"[INFO] 创建新用户数据文件: {user_name}")
                                else:
                                    print(f"[INFO] 加载现有用户数据: {user_name}")
                                    session['has_history'] = True
                    break

        # 记录用户对话到日志（便于自查）
        if user_name:
            try:
                logger.log_conversation(
                    user_name=user_name,
                    user_message=user_message,
                    ai_reply=ai_reply,
                    metadata={
                        'ip': request.remote_addr,
                        'user_agent': request.headers.get('User-Agent', ''),
                        'has_history': session.get('has_history', False)
                    }
                )
            except Exception as e:
                print(f"[WARNING] 记录用户对话失败: {str(e)}")

        # 从显示的回复中移除DATA_UPDATE块（仅用于前端显示）
        display_reply = ai_reply
        if 'DATA_UPDATE:' in display_reply:
            # 找到DATA_UPDATE:的位置
            data_update_start = display_reply.find('DATA_UPDATE:')
            if data_update_start != -1:
                # 查找DATA_UPDATE块之前的换行符，从那里截断
                # 向前查找最近的换行符或空行
                cut_pos = data_update_start
                # 向前查找，找到###标题或空行
                for i in range(data_update_start - 1, max(0, data_update_start - 200), -1):
                    if display_reply[i:i+4] == '\n###' or display_reply[i-3:i+1] == '\n\n':
                        cut_pos = i
                        break
                display_reply = display_reply[:cut_pos].rstrip()

        # 返回结果
        return jsonify({
            'success': True,
            'reply': display_reply,  # 使用过滤后的回复
            'conversation_history': conversation_history,
            'user_name': session.get('user_name') or '(未知)',
            'has_history': session.get('has_history', False)
        })

    except Exception as e:
        print(f"错误: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': f'服务器错误: {str(e)}'
        }), 500


@app.route('/api/reset', methods=['POST'])
def reset_conversation():
    """重置对话"""
    user_name = session.get('user_name')

    # 如果有用户名字，也删除用户数据文件
    if user_name:
        try:
            user_manager.delete_user_data(user_name)
            print(f"[INFO] 已删除用户数据文件: {user_name}")
        except Exception as e:
            print(f"[WARNING] 删除用户数据文件失败: {str(e)}")

    # 清空session
    session.pop('conversation_history', None)
    session.pop('user_name', None)
    session.pop('has_history', None)
    session.pop('name_extracted', None)

    return jsonify({
        'success': True,
        'message': '对话已重置，历史数据已清空'
    })


@app.route('/api/user-data', methods=['GET'])
def get_user_data():
    """获取当前用户的数据"""
    try:
        user_name = session.get('user_name')
        print(f"[DEBUG] /api/user-data: user_name from session = {user_name}")

        if not user_name:
            return jsonify({
                'success': True,
                'user_name': None,
                'data': {}
            })

        # 从文件加载用户数据
        user_data = user_manager.load_user_data(user_name)
        print(f"[DEBUG] /api/user-data: loaded user_data keys = {list(user_data.keys()) if user_data else 'None'}")
        print(f"[DEBUG] /api/user-data: loaded user_data = {user_data}")

        # 提取AI建议（从对话历史中）
        conversation_history = session.get('conversation_history', [])
        recommendations = []

        # 查找AI的最后一次重要回复（包含建议或结论）
        for msg in reversed(conversation_history):
            if msg.get('role') == 'assistant':
                content = msg.get('content', '')
                # 检查是否包含建议或结论
                if any(keyword in content for keyword in ['建议', '推荐', '结论', '档位', '最优', '选择']):
                    recommendations.append({
                        'content': content[:500],  # 只取前500字
                        'timestamp': '最近'
                    })
                    break

        return jsonify({
            'success': True,
            'user_name': user_name,
            'data': user_data or {},
            'recommendations': recommendations
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/update-user-data', methods=['POST'])
def update_user_data():
    """更新用户数据"""
    try:
        user_name = session.get('user_name')
        if not user_name:
            return jsonify({
                'success': False,
                'error': '用户未登录'
            }), 401

        # 获取请求数据
        updated_data = request.get_json()

        # 加载现有数据
        existing_data = user_manager.load_user_data(user_name) or {}

        # 更新数据（只更新提供的字段）
        for key, value in updated_data.items():
            if value:  # 只更新非空值
                existing_data[key] = value

        # 保存更新后的数据
        user_manager.save_user_data(user_name, existing_data)

        return jsonify({
            'success': True,
            'message': '用户数据更新成功',
            'data': existing_data
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/logs', methods=['GET'])
def get_logs():
    """获取最近的日志列表"""
    try:
        logs = logger.get_latest_logs(10)
        log_summaries = []

        for log_path in logs:
            try:
                log_data = logger.read_log(log_path)
                log_summaries.append({
                    'filename': os.path.basename(log_path),
                    'timestamp': log_data['metadata']['timestamp'],
                    'model': log_data['metadata']['model'],
                    'has_error': log_data['output']['has_error']
                })
            except Exception as e:
                print(f"警告: 读取日志失败 {log_path} - {str(e)}")

        return jsonify({
            'success': True,
            'logs': log_summaries
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


if __name__ == '__main__':
    print("\n" + "="*60)
    print("北京退休金测算系统")
    print("="*60)
    print(f"[OK] AI模型: {ai_client.model}")
    print(f"[OK] API接口: {ai_client.base_url}")
    print(f"[OK] 日志目录: {logger.log_dir}")
    print("="*60)
    print("\n启动Web服务器...")
    print("访问地址: http://localhost:5000")
    print("="*60 + "\n")

    # 启动Flask应用
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=True
    )
