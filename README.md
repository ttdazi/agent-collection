# 可扩展笑话Agent

一个基于LangChain的可扩展Agent系统，支持多模型切换（Ollama、Gemini等），采用模块化架构便于修改和扩展。

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![LangChain](https://img.shields.io/badge/LangChain-0.1.20-orange.svg)](https://www.langchain.com/)

## 功能特性

- 支持多模型切换（Ollama、Google Gemini）
- 模块化架构，易于扩展新模型
- 使用LangChain Agent框架
- 支持动态切换模型
- 提供H5前端页面

## 安装步骤

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

## 项目结构

```
helloAgent/
├── app.py                    # Flask主应用
├── config.py                 # 统一配置文件
├── requirements.txt          # Python依赖
├── README.md                 # 项目说明
├── core/                     # 核心模块
│   ├── __init__.py
│   ├── agent_factory.py     # Agent工厂
│   ├── model_provider.py    # 模型提供者抽象基类
│   └── llm_logger.py        # LLM交互日志记录器
├── logs/                     # 日志目录（自动创建）
│   └── llm_interactions.log # LLM交互日志文件
├── providers/                # 模型提供者实现
│   ├── __init__.py
│   ├── ollama_provider.py   # Ollama模型提供者
│   └── gemini_provider.py   # Google Gemini提供者
├── tools/                    # Agent工具
│   ├── __init__.py
│   └── joke_tools.py        # 笑话相关工具
└── templates/                # 前端页面
    └── index.html           # H5页面
```

## 配置说明

### 修改默认模型

编辑 `config.py`：

```python
"model_type": "ollama"  # 或 "gemini"
```

### 修改Ollama模型

编辑 `config.py`：

```python
"ollama": {
    "model": "qwen2.5:1.5b",  # 改为其他模型
    ...
}
```

### 动态切换模型

通过API接口：

```bash
POST /api/config
Content-Type: application/json

{
    "model_type": "gemini"
}
```

### 日志配置

LLM交互日志默认保存到文件，控制台不显示详细内容：

编辑 `config.py`：

```python
"logging": {
    "llm_console_output": False,  # True=控制台显示详细日志，False=仅保存到文件
    "llm_log_file": "logs/llm_interactions.log",  # 日志文件路径
    "log_level": "INFO",  # 日志级别
}
```

**日志文件位置：** `logs/llm_interactions.log`

- 默认：控制台只显示简要信息，详细日志保存到文件
- 开启控制台输出：设置 `llm_console_output: True` 可同时在控制台查看详细日志
- 日志文件包含完整的Prompt和Response内容，便于调试和分析

## API接口

- `GET /` - 返回H5页面
- `POST /api/joke` - 获取笑话
  ```json
  {
      "input": "讲个笑话"
  }
  ```
- `GET /api/config` - 获取当前配置
- `POST /api/config` - 切换模型
  ```json
  {
      "model_type": "ollama"
  }
  ```

## 扩展新模型

1. 在 `providers/` 目录创建新的Provider类
2. 继承 `ModelProvider` 基类
3. 实现 `get_llm()` 和 `validate_config()` 方法
4. 在 `core/agent_factory.py` 中注册新Provider

## 贡献指南

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

## 许可证

本项目采用 [MIT License](LICENSE) 开源协议。

## 致谢

- [LangChain](https://www.langchain.com/) - Agent框架
- [Ollama](https://ollama.ai/) - 本地LLM运行环境
- [Google Gemini](https://ai.google.dev/) - AI模型API

## 作者

helloAgent Contributors

## 相关链接

- [问题反馈](https://github.com/your-username/helloAgent/issues)
- [功能建议](https://github.com/your-username/helloAgent/issues)

