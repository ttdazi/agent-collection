# 快速开始

## 安装

### 1. 安装Python依赖

```bash
pip install -r requirements.txt
```

### 2. 配置Ollama（默认模型）

确保已安装Ollama并下载模型：

```bash
# 下载推荐模型
ollama pull qwen2.5:1.5b
# 或
ollama pull llama3.2:3b
```

### 3. （可选）配置Google Gemini API

如果需要使用Gemini模型，设置环境变量：

```bash
# Windows PowerShell
$env:GOOGLE_API_KEY="your-api-key-here"

# Linux/Mac
export GOOGLE_API_KEY="your-api-key-here"
```

获取API Key: https://aistudio.google.com/

### 4. 运行服务

```bash
python app.py
```

访问 http://localhost:5000

## 基本使用

### Web界面

1. 打开浏览器访问 http://localhost:5000
2. 选择模型类型（Ollama或Gemini）
3. 如果选择Ollama，选择本地模型
4. 如果选择Gemini，输入API Key
5. 点击"讲个笑话"按钮

### API调用

#### 调用Agent

```bash
curl -X POST http://localhost:5000/api/agent/invoke \
  -H "Content-Type: application/json" \
  -d '{
    "agent_name": "joke",
    "input": "讲个笑话"
  }'
```

#### 获取配置

```bash
curl http://localhost:5000/api/config
```

#### 更新配置

```bash
curl -X POST http://localhost:5000/api/config \
  -H "Content-Type: application/json" \
  -d '{
    "model_type": "ollama",
    "model": "qwen2.5:1.5b"
  }'
```

#### 获取Ollama模型列表

```bash
curl http://localhost:5000/api/ollama/models
```

## 配置说明

### 修改默认模型

编辑 `config.py`：

```python
"model_type": "ollama"  # 或 "gemini"
"default_agent": "joke"  # 默认Agent类型
```

### 修改Ollama模型

编辑 `config.py`：

```python
"ollama": {
    "model": "qwen2.5:1.5b",  # 改为其他模型
    "base_url": "http://localhost:11434",
    "temperature": 0.7,
}
```

### 日志配置

编辑 `config.py`：

```python
"logging": {
    "llm_console_output": False,  # True=控制台显示详细日志
    "llm_log_file": "logs/llm_interactions.log",
    "log_level": "INFO",
}
```

## 项目结构

```
helloAgent/
├── app.py                    # Flask主应用
├── config.py                 # 配置文件
├── requirements.txt          # Python依赖
├── core/                     # 核心模块
│   ├── agent_factory.py     # Agent工厂
│   ├── agent_service.py    # Agent服务层
│   ├── agent_registry.py    # Agent注册表
│   ├── tool_registry.py     # 工具注册表
│   ├── model_provider.py    # 模型提供者基类
│   └── llm_logger.py        # LLM日志记录器
├── agents/                   # Agent定义
│   ├── base_agent.py        # Agent基类
│   └── joke_agent.py        # 笑话Agent
├── providers/                # 模型提供者
│   ├── ollama_provider.py   # Ollama提供者
│   └── gemini_provider.py   # Gemini提供者
├── tools/                    # Agent工具
│   └── joke_tools.py        # 笑话工具
└── templates/                # 前端页面
    └── index.html           # H5页面
```

## 下一步

- [扩展指南](extension.md) - 学习如何添加新Agent和工具
- [API参考](../api/reference.md) - 查看完整的API文档
- [故障排除](troubleshooting.md) - 解决常见问题

