# 北京退休金测算系统

基于智谱AI GLM-4.7大模型开发的北京养老保险退休金测算Web应用，帮助灵活就业人员对比三档缴费方案，找到最优选择。

## 功能特点

- ✅ **智能对话**：通过自然语言交互收集用户信息
- ✅ **精准测算**：基于北京社保政策精确计算退休金
- ✅ **三档对比**：详细分析低/中/高三档缴费的优劣
- ✅ **性价比分析**：计算回本周期和净收益
- ✅ **完整日志**：记录所有AI调用过程便于审计

## 项目结构

```
retire/
├── app.py                    # Flask主应用
├── ai_client.py             # GLM AI客户端（Anthropic兼容接口）
├── logger.py                # 日志记录模块
├── prompts/                 # 提示词文件夹
│   ├── system_prompt.txt    # 系统提示词
│   └── policy_context.txt   # 政策背景信息
├── templates/               # HTML模板
│   └── index.html          # 前端页面
├── static/                  # 静态资源（预留）
├── logs/                    # AI调用日志
├── tests/                   # 测试文件
│   ├── test_api.py         # API测试
│   └── test_data.json      # 测试数据
├── config.env              # 配置文件（API Key）
└── README.md              # 本文档
```

## 环境要求

- Python 3.8+
- 智谱AI API Key（从系统变量读取）

## 安装步骤

### 1. 安装依赖

```bash
pip install flask requests
```

### 2. 配置API Key

**Windows CMD:**
```cmd
set ZHIPU_API_KEY=your_api_key_here
```

**Windows PowerShell:**
```powershell
$env:ZHIPU_API_KEY='your_api_key_here'
```

**Linux/Mac:**
```bash
export ZHIPU_API_KEY=your_api_key_here
```

⚠️ **重要**：
- API Key格式为 `id.secret`（例如：`1234.abcde123456`）
- 不要将API Key硬编码到代码中
- 每次重启终端后需要重新设置环境变量

### 3. 永久设置环境变量（可选）

**Windows系统变量:**
1. 右键"此电脑" → 属性 → 高级系统设置
2. 环境变量 → 新建
3. 变量名：`ZHIPU_API_KEY`
4. 变量值：你的API Key

**Linux/Mac (添加到 ~/.bashrc 或 ~/.zshrc):**
```bash
export ZHIPU_API_KEY='your_api_key_here'
```

## 使用方法

### 启动Web服务

```bash
python app.py
```

启动成功后会显示：
```
============================================================
北京退休金测算系统
============================================================
✓ AI模型: glm-4.7
✓ API接口: https://open.bigmodel.cn/api/anthropic/v1/messages
✓ 日志目录: logs
============================================================

启动Web服务器...
访问地址: http://localhost:5000
============================================================
```

### 访问Web界面

在浏览器中打开：http://localhost:5000

### 对话示例

**用户**：你好，我是1980年出生的北京户口男性，现在失业了，想咨询灵活就业交养老保险的事情。

**AI**：您好！我来帮您分析最适合的缴费档位。请问：
1. 您首次工作时间是？
2. 累计工作年限和缴费年限？
3. 近几年平均工资？
...

## 运行测试

```bash
cd tests
python test_api.py
```

测试内容：
- 提示词文件检查
- AI客户端调用
- 日志记录功能

## 技术架构

### 后端技术栈
- **Flask**: Web框架
- **requests**: HTTP请求库
- **GLM-4.7**: 智谱AI大模型（Anthropic兼容接口）

### 前端技术栈
- **原生HTML/CSS/JavaScript**
- **Fetch API**: 异步请求
- **CSS Grid/Flexbox**: 响应式布局

### AI调用流程

```
用户输入
  ↓
Flask后端接收
  ↓
加载系统提示词 + 政策背景
  ↓
调用GLM-4.7（Anthropic兼容接口）
  ↓
记录完整日志到logs/
  ↓
返回AI回复给前端
  ↓
前端展示并保存对话历史
```

### 日志记录格式

每次AI调用都会生成JSON日志文件：`logs/ai_call_YYYYMMDD_HHMMSS.json`

```json
{
  "metadata": {
    "timestamp": "2025-01-08T12:00:00",
    "model": "glm-4.7"
  },
  "input": {
    "system_prompt": "...",
    "user_message": "...",
    "conversation_history": [...]
  },
  "output": {
    "response": {...},
    "has_error": false
  },
  "statistics": {
    "system_prompt_length": 5000,
    "user_message_length": 100,
    "ai_response_length": 2000
  }
}
```

## 政策说明

### 灵活就业养老保险三档（2025年北京标准）

| 档位 | 缴费基数 | 月缴费额 | 个人账户 |
|------|----------|----------|----------|
| 低档 | 社平60% | 1362元 | 544元 |
| 中档 | 社平100% | 2270元 | 908元 |
| 高档 | 社平300% | 6810元 | 2724元 |

**缴费比例**：20%（个人账户8% + 统筹账户12%）

**2024年北京社平工资**：11350元/月（暂定，以官方公布为准）

### 退休金计算公式

```
基础养老金 = (社平工资 + 指数化工资) ÷ 2 × 缴费年限 × 1%
个人账户养老金 = 个人账户储存额 ÷ 计发月数
过渡性养老金 = 社平工资 × 视同缴费年限 × 1%
总养老金 = 基础养老金 + 个人账户养老金 + 过渡性养老金
```

**计发月数**：
- 55岁退休：170个月
- 60岁退休：139个月

## 常见问题

### Q1: 提示"未找到ZHIPU_API_KEY环境变量"？

**解决方法**：
1. 确认已设置环境变量（见"配置API Key"章节）
2. Windows CMD重启后需重新设置
3. 使用 `echo %ZHIPU_API_KEY%` 检查是否设置成功

### Q2: API调用失败怎么办？

**可能原因**：
- API Key格式错误（应为 `id.secret` 格式）
- API Key已过期或余额不足
- 网络连接问题

**解决方法**：
1. 检查API Key格式是否正确
2. 访问智谱AI控制台检查余额：https://open.bigmodel.cn/
3. 检查网络连接

### Q3: 日志文件在哪里？

所有日志文件保存在 `logs/` 目录，文件名格式为：`ai_call_YYYYMMDD_HHMMSS.json`

### Q4: 如何修改系统提示词？

编辑 `prompts/system_prompt.txt` 文件，修改后重启服务即可生效。

## 重要提示

⚠️ **CD命令不持久化问题**：
在使用bash时，`cd` 命令只在当前命令内有效，每次执行新命令都需要重新指定完整路径或使用 `cd && command` 的方式。

示例：
```bash
# 错误方式（cd不会保持）
cd /c/D/CAIE_tool/MyAIProduct/retire
python app.py

# 正确方式
cd /c/D/CAIE_tool/MyAIProduct/retire && python app.py

# 或使用绝对路径
python /c/D/CAIE_tool/MyAIProduct/retire/app.py
```

## 开发计划

- [ ] 添加用户认证
- [ ] 支持多用户并发
- [ ] 数据持久化（数据库）
- [ ] 导出测算报告PDF
- [ ] 添加更多城市支持
- [ ] 移动端适配优化

## 技术支持

如遇问题，请检查：
1. `logs/` 目录下的日志文件
2. 控制台错误输出
3. 浏览器开发者工具Console

## 许可证

本项目仅供学习交流使用。

---

**更新日期**: 2025-01-08
**版本**: v1.0.0
**模型**: GLM-4.7 (Anthropic兼容接口)
