# CD命令不持久化问题说明

## 问题描述

在使用bash环境时，`cd` 命令只在当前命令执行期间有效，**不会持久化**到后续命令。

## 示例

### ❌ 错误方式

```bash
cd /c/D/CAIE_tool/MyAIProduct/retire
python app.py  # 这时可能不在retire目录！
ls -la         # 这时可能不在retire目录！
```

### ✅ 正确方式

**方式1：使用 && 连接**
```bash
cd /c/D/CAIE_tool/MyAIProduct/retire && python app.py
```

**方式2：使用绝对路径**
```bash
python /c/D/CAIE_tool/MyAIProduct/retire/app.py
```

**方式3：使用子shell**
```bash
(cd /c/D/CAIE_tool/MyAIProduct/retire && python app.py)
```

## 原因

每个bash命令调用都是独立的shell会话，不会保持之前命令的工作目录状态。

## 最佳实践

1. **执行单个命令时**：使用 `cd && command` 的方式
2. **执行多个相关命令时**：每个命令都加上完整路径或使用 `cd &&`
3. **在Python等代码中操作文件时**：始终使用绝对路径
4. **在脚本文件中**：脚本内部cd会保持，但外部调用后不会保持

## 项目中的正确用法示例

```bash
# 在retire目录中运行测试
cd /c/D/CAIE_tool/MyAIProduct/retire && python tests/test_api.py

# 查看日志
cd /c/D/CAIE_tool/MyAIProduct/retire && ls -la logs/

# 启动应用
cd /c/D/CAIE_tool/MyAIProduct/retire && python app.py
```

## 注意事项

- 此问题在Windows Git Bash、MSYS2、Cygwin等类Unix环境中存在
- 在PowerShell或CMD中，cd会保持（在同一个会话中）
- 在远程执行命令时尤其需要注意此问题

---

**记录日期**: 2025-01-08
**问题发现者**: 用户反馈
**适用环境**: Windows Git Bash / MSYS2
