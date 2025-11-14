# helloAgent

一个基于LangChain的可扩展Agent系统，支持多模型切换（Ollama、Gemini等），采用模块化架构便于修改和扩展。

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![LangChain](https://img.shields.io/badge/LangChain-0.0.350-orange.svg)](https://www.langchain.com/)

## ✨ 功能特性

- 🎯 **多Agent支持** - 支持多种Agent类型（笑话、代码分析等），易于扩展
- 🤖 **多模型切换** - 支持Ollama（本地免费）和Google Gemini（免费额度）
- 🛠️ **工具系统** - 动态工具注册，支持工具分组管理
- 📦 **模块化架构** - 清晰的模块职责，易于维护和扩展
- 🎨 **Web界面** - 提供H5前端页面，支持模型和Agent切换
- 📊 **日志记录** - 完整的LLM交互日志，便于调试和分析

## 🚀 快速开始

### 安装

```bash
# 1. 安装Python依赖
pip install -r requirements.txt

# 2. 配置Ollama（默认模型）
ollama pull qwen2.5:1.5b

# 3. （可选）配置Google Gemini API
export GOOGLE_API_KEY="your-api-key-here"

# 4. 运行服务
python app.py
```

访问 http://localhost:5000

详细安装说明请参考 [快速开始指南](doc/guides/getting-started.md)

## 📁 项目结构

```
helloAgent/
├── app.py                    # Flask主应用（路由层）
├── config.py                 # 统一配置文件
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
├── templates/                # 前端页面
│   └── index.html           # H5页面
└── doc/                      # 文档目录
    ├── architecture/         # 架构文档
    ├── guides/              # 使用指南
    └── api/                 # API文档
```

## 📖 文档

完整文档请查看 [doc/](doc/) 目录：

- [📚 文档索引](doc/README.md) - 文档导航
- [🏗️ 架构概览](doc/architecture/overview.md) - 系统架构设计
- [⚡ 快速开始](doc/guides/getting-started.md) - 安装和基本使用
- [🔧 扩展指南](doc/guides/extension.md) - 如何添加新Agent、工具和模型
- [🐛 故障排除](doc/guides/troubleshooting.md) - 常见问题解决
- [📡 API参考](doc/api/reference.md) - 完整的API文档

## 🔌 API使用

### 调用Agent

```bash
curl -X POST http://localhost:5000/api/agent/invoke \
  -H "Content-Type: application/json" \
  -d '{
    "agent_name": "joke",
    "input": "讲个笑话"
  }'
```

### 获取配置

```bash
curl http://localhost:5000/api/config
```

### 更新配置

```bash
curl -X POST http://localhost:5000/api/config \
  -H "Content-Type: application/json" \
  -d '{
    "model_type": "ollama",
    "model": "qwen2.5:1.5b"
  }'
```

更多API文档请参考 [API参考](doc/api/reference.md)

## 🎯 核心特性

### 多Agent架构

系统支持多种Agent类型，每种Agent可以有自己的工具集：

- **笑话Agent** - 讲笑话
- **代码Agent** - 代码分析（示例）
- 更多Agent类型可以轻松添加

### 工具注册机制

工具可以动态注册，支持分组管理：

```python
from core.tool_registry import tool_registry
tool_registry.register_tools(tools, group="joke")
```

### Agent注册机制

Agent定义可以动态注册：

```python
from core.agent_registry import agent_registry, AgentDefinition
agent_def = AgentDefinition(...)
agent_registry.register_agent(agent_def)
```

### 模型提供者模式

支持多种模型，易于扩展：

- **Ollama** - 本地免费模型
- **Gemini** - Google云端模型
- 更多模型可以轻松添加

## 🔧 配置说明

### 基本配置

编辑 `config.py`：

```python
DEFAULT_CONFIG = {
    "model_type": "ollama",      # 默认模型类型
    "default_agent": "joke",     # 默认Agent类型
    # ...
}
```

### 日志配置

```python
"logging": {
    "llm_console_output": False,  # 控制台是否显示详细日志
    "llm_log_file": "logs/llm_interactions.log",
    "log_level": "INFO",
}
```

## 🛠️ 扩展系统

### 添加新Agent

1. 创建Agent类（继承 `BaseAgent`）
2. 注册Agent类到 `AgentFactory`
3. 注册Agent定义到 `AgentRegistry`

详细步骤请参考 [扩展指南](doc/guides/extension.md)

### 添加新工具

1. 创建工具函数
2. 创建Tool实例
3. 注册到 `ToolRegistry`

### 添加新模型

1. 实现 `ModelProvider` 接口
2. 注册到 `AgentFactory`

## 📊 架构优势

- ✅ **可扩展性** - 添加新功能无需修改核心代码
- ✅ **可维护性** - 清晰的模块职责，易于理解
- ✅ **可测试性** - 服务层抽象，便于单元测试
- ✅ **高性能** - Agent实例缓存，减少重复创建

## 🤝 贡献指南

欢迎贡献代码！请遵循以下步骤：

1. Fork 本仓库
2. 创建你的特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交你的更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启一个 Pull Request

### 代码规范

- 遵循 PEP 8 Python 代码风格
- 添加适当的注释和文档字符串
- 确保代码可以正常运行

## 📝 许可证

本项目采用 [MIT License](LICENSE) 开源协议。

## 🙏 致谢

- [LangChain](https://www.langchain.com/) - Agent框架
- [Ollama](https://ollama.ai/) - 本地LLM运行环境
- [Google Gemini](https://ai.google.dev/) - AI模型API

## 📞 相关链接

- [问题反馈](https://github.com/your-username/helloAgent/issues)
- [功能建议](https://github.com/your-username/helloAgent/issues)
- [文档中心](doc/README.md)
