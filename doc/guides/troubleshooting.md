# 故障排除

## 常见问题

### 1. 模块导入错误

**错误**：`ModuleNotFoundError: No module named 'core'`

**原因**：Python无法找到项目模块

**解决方案**：
- 确保在项目根目录运行 `python app.py`
- 检查 `sys.path` 设置是否正确
- 确保所有 `__init__.py` 文件存在

### 2. Ollama连接失败

**错误**：`无法连接到Ollama服务`

**原因**：Ollama服务未启动或配置错误

**解决方案**：
```bash
# 检查Ollama是否运行
ollama list

# 启动Ollama服务（如果未启动）
# Windows: 启动Ollama应用
# Linux/Mac: ollama serve

# 检查配置中的base_url
# config.py 中的 "base_url": "http://localhost:11434"
```

### 3. Gemini API Key错误

**错误**：`GOOGLE_API_KEY未设置`

**原因**：API Key未配置

**解决方案**：
```bash
# 设置环境变量
# Windows PowerShell
$env:GOOGLE_API_KEY="your-api-key"

# Linux/Mac
export GOOGLE_API_KEY="your-api-key"

# 或在config.py中直接设置
"gemini": {
    "api_key": "your-api-key",
    ...
}
```

### 4. 工具重复注册警告

**警告**：`⚠️ 警告: 工具 'GetRandomJoke' 已存在，将被覆盖`

**原因**：工具被多次注册

**解决方案**：
- 检查 `core/__init__.py` 是否重复导入
- 检查工具文件是否被多次调用
- 工具注册表已自动处理重复注册，警告可以忽略

### 5. LLM输出格式错误

**错误**：`Could not parse LLM output`

**原因**：LLM输出不符合ReAct格式

**解决方案**：
- 检查工具描述是否清晰
- 改进错误处理函数
- 考虑使用更强大的模型
- 参考 [日志分析](../../LOG_ANALYSIS.md)

### 6. Agent创建失败

**错误**：`创建Agent失败: ...`

**原因**：配置无效或服务不可用

**解决方案**：
- 检查模型配置是否正确
- 验证模型服务是否可用
- 检查工具是否已正确注册
- 查看详细错误信息

### 7. 端口被占用

**错误**：`Address already in use`

**原因**：5000端口已被占用

**解决方案**：
```python
# 修改 app.py 中的端口
app.run(debug=True, host='0.0.0.0', port=5001)  # 改为其他端口
```

## 调试技巧

### 1. 启用详细日志

编辑 `config.py`：

```python
"logging": {
    "llm_console_output": True,  # 启用控制台输出
    "llm_log_file": "logs/llm_interactions.log",
    "log_level": "DEBUG",
}
```

### 2. 查看日志文件

```bash
# 查看最新日志
tail -f logs/llm_interactions.log

# Windows PowerShell
Get-Content logs/llm_interactions.log -Tail 50 -Wait
```

### 3. 测试API

```bash
# 测试配置接口
curl http://localhost:5000/api/config

# 测试Agent调用
curl -X POST http://localhost:5000/api/agent/invoke \
  -H "Content-Type: application/json" \
  -d '{"agent_name": "joke", "input": "test"}'
```

### 4. 检查工具注册

```python
# 在Python交互式环境中
from core.tool_registry import tool_registry
print(tool_registry.get_tool_names())
print(tool_registry.list_groups())
```

### 5. 检查Agent注册

```python
# 在Python交互式环境中
from core.agent_registry import agent_registry
print(agent_registry.list_agents())
```

## 性能优化

### 1. Agent缓存

Agent实例会被缓存，避免重复创建。如果配置更改，缓存会自动清除。

### 2. 模型选择

- Ollama：本地运行，速度快，但需要本地资源
- Gemini：云端运行，功能强大，但需要网络连接

### 3. 工具优化

- 保持工具函数简单高效
- 避免在工具中执行耗时操作
- 使用缓存机制（如需要）

## 获取帮助

如果问题仍未解决：

1. 查看 [日志分析](../../LOG_ANALYSIS.md)
2. 检查 [架构文档](../architecture/overview.md)
3. 提交 [Issue](https://github.com/your-username/helloAgent/issues)

## 相关文档

- [快速开始](getting-started.md) - 安装和基本使用
- [扩展指南](extension.md) - 如何扩展系统
- [API参考](../api/reference.md) - API文档

