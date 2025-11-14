# API参考

## 基础信息

- **Base URL**: `http://localhost:5000`
- **Content-Type**: `application/json`

## 端点列表

### 1. 调用Agent

调用指定的Agent处理请求。

**端点**: `POST /api/agent/invoke`

**请求体**:
```json
{
    "agent_name": "joke",  // 可选，默认使用配置中的default_agent
    "input": "讲个笑话"     // 必需，用户输入
}
```

**响应**:
```json
{
    "success": true,
    "output": "为什么程序员总是分不清万圣节和圣诞节？因为 Oct 31 == Dec 25！",
    "agent_name": "joke",
    "model_type": "ollama"
}
```

**错误响应**:
```json
{
    "success": false,
    "output": "错误: ...",
    "error": "详细错误信息"
}
```

### 2. 列出所有Agent

获取所有可用的Agent列表。

**端点**: `GET /api/agents`

**响应**:
```json
{
    "success": true,
    "agents": ["joke", "code"]
}
```

### 3. 获取配置

获取当前系统配置。

**端点**: `GET /api/config`

**响应**:
```json
{
    "model_type": "ollama",
    "default_agent": "joke",
    "available_models": ["ollama", "gemini"],
    "available_agents": ["joke"],
    "current_model_config": {
        "model": "qwen2.5:1.5b",
        "base_url": "http://localhost:11434",
        "temperature": 0.7
    }
}
```

### 4. 更新配置

更新系统配置（模型类型、Agent类型、模型参数等）。

**端点**: `POST /api/config`

**请求体**:
```json
{
    "model_type": "ollama",        // 可选，模型类型
    "agent_name": "joke",          // 可选，Agent类型
    "model": "qwen2.5:1.5b",       // 可选，Ollama模型名称
    "base_url": "http://...",      // 可选，Ollama服务地址
    "api_key": "..."               // 可选，Gemini API Key
}
```

**响应**:
```json
{
    "success": true,
    "message": "配置已更新",
    "model_type": "ollama",
    "agent_name": "joke",
    "current_model_config": {
        "model": "qwen2.5:1.5b",
        ...
    }
}
```

### 5. 获取Ollama模型列表

获取本地Ollama服务中可用的模型列表。

**端点**: `GET /api/ollama/models`

**响应**:
```json
{
    "success": true,
    "models": ["qwen2.5:1.5b", "llama3.2:3b"]
}
```

**错误响应**:
```json
{
    "success": false,
    "error": "无法连接到Ollama服务: ...",
    "models": []
}
```

## 使用示例

### Python示例

```python
import requests

# 调用Agent
response = requests.post(
    'http://localhost:5000/api/agent/invoke',
    json={
        'agent_name': 'joke',
        'input': '讲个笑话'
    }
)
print(response.json())

# 获取配置
response = requests.get('http://localhost:5000/api/config')
print(response.json())

# 更新配置
response = requests.post(
    'http://localhost:5000/api/config',
    json={
        'model_type': 'ollama',
        'model': 'qwen2.5:1.5b'
    }
)
print(response.json())
```

### cURL示例

```bash
# 调用Agent
curl -X POST http://localhost:5000/api/agent/invoke \
  -H "Content-Type: application/json" \
  -d '{"agent_name": "joke", "input": "讲个笑话"}'

# 获取配置
curl http://localhost:5000/api/config

# 更新配置
curl -X POST http://localhost:5000/api/config \
  -H "Content-Type: application/json" \
  -d '{"model_type": "ollama", "model": "qwen2.5:1.5b"}'

# 获取Ollama模型列表
curl http://localhost:5000/api/ollama/models
```

### JavaScript示例

```javascript
// 调用Agent
fetch('http://localhost:5000/api/agent/invoke', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
        agent_name: 'joke',
        input: '讲个笑话'
    })
})
.then(res => res.json())
.then(data => console.log(data));

// 获取配置
fetch('http://localhost:5000/api/config')
.then(res => res.json())
.then(data => console.log(data));
```

## 错误码

- `200` - 成功
- `400` - 请求错误（如配置无效）
- `500` - 服务器错误（如Agent创建失败）

## 注意事项

1. **Agent名称**：如果不提供 `agent_name`，将使用配置中的 `default_agent`
2. **模型类型**：更新配置时，相关Agent缓存会自动清除
3. **Ollama模型**：需要Ollama服务运行在配置的地址
4. **Gemini API**：需要有效的API Key

## 相关文档

- [快速开始](../guides/getting-started.md) - 安装和基本使用
- [扩展指南](../guides/extension.md) - 如何扩展系统
- [故障排除](../guides/troubleshooting.md) - 常见问题解决

