# 扩展指南

本指南介绍如何扩展系统，添加新的Agent、工具和模型。

## 添加新任务Agent

### 步骤1: 创建Agent类

在 `agents/task/` 目录创建新文件，例如 `code_agent.py`：

```python
from langchain.agents import create_agent
from agents.base.base_agent import BaseAgent

class CodeAgent(BaseAgent):
    """代码分析Agent"""
    
    def create_agent_executor(self):
        """创建代码Agent执行器（使用create_agent API）"""
        system_prompt = """你是一个代码分析助手。
当用户要求分析代码时，你必须使用工具来执行分析。
不能直接编造答案，必须通过工具获取结果。"""
        
        return create_agent(
            model=self.llm,
            tools=self.tools,
            system_prompt=system_prompt,
        )
```

### 步骤2: 注册Agent类

在 `core/agent_factory.py` 中注册：

```python
from agents.task.code_agent import CodeAgent

_agent_classes = {
    "joke": JokeAgent,
    "code": CodeAgent,  # 添加新Agent
}
```

### 步骤3: 注册Agent定义

在 `core/agent_factory.py` 的 `_register_default_agents` 方法中：

```python
if "code" not in agent_registry.list_agents():
    agent_def = AgentDefinition(
        name="code",
        display_name="代码分析Agent",
        description="用于代码分析、生成和审查的Agent",
        tool_groups=["code"],  # 指定使用的工具组
        agent_type=None,  # 新API不再需要AgentType
        default_config={"verbose": True, "max_iterations": 10}
    )
    agent_registry.register_agent(agent_def)
```

### 步骤4: 创建工具（如果需要）

参考"添加新工具"部分。

## 添加新工具

### 步骤1: 创建工具函数

在 `tools/` 目录创建新文件，例如 `code_tools.py`：

```python
from langchain_core.tools import Tool
from core.tool_registry import tool_registry

def analyze_code(code: str) -> str:
    """分析代码"""
    # 实现代码分析逻辑
    return f"代码分析结果: {code[:50]}..."

def get_code_tools():
    """获取所有代码相关工具"""
    tools = [
        Tool(
            name="AnalyzeCode",
            func=analyze_code,
            description=(
                "分析代码，提供代码审查和建议。\n"
                "使用格式：\n"
                "Action: AnalyzeCode\n"
                "Action Input: [代码片段]"
            )
        ),
    ]
    # 自动注册到工具注册表
    tool_registry.register_tools(tools, group="code")
    return tools
```

### 步骤2: 确保工具被注册

在 `core/__init__.py` 中导入：

```python
try:
    from tools.code_tools import get_code_tools
    get_code_tools()
except ImportError:
    pass
```

## 添加新模型

### 步骤1: 实现ModelProvider接口

在 `providers/` 目录创建新文件，例如 `openai_provider.py`：

```python
from core.model_provider import ModelProvider
from typing import Any, Dict
from langchain_openai import ChatOpenAI

class OpenAIProvider(ModelProvider):
    """OpenAI模型提供者"""
    
    def get_llm(self, config: Dict[str, Any]):
        """创建OpenAI ChatModel实例"""
        api_key = config.get("api_key")
        if not api_key:
            raise ValueError("OpenAI API key未设置")
        
        return ChatOpenAI(
            model=config.get("model", "gpt-3.5-turbo"),
            openai_api_key=api_key,
            temperature=config.get("temperature", 0.7),
        )
    
    def validate_config(self, config: Dict[str, Any]) -> bool:
        """验证OpenAI配置"""
        return bool(config.get("api_key"))
```

### 步骤2: 注册Provider

在 `core/agent_factory.py` 的 `_get_providers` 方法中：

```python
from providers.openai_provider import OpenAIProvider

cls._providers = {
    "ollama": OllamaProvider(),
    "gemini": GeminiProvider(),
    "openai": OpenAIProvider(),  # 添加新Provider
}
```

### 步骤3: 添加配置

在 `config.py` 中添加：

```python
"openai": {
    "model": "gpt-3.5-turbo",
    "api_key": os.getenv("OPENAI_API_KEY", ""),
    "temperature": 0.7,
}
```

## 最佳实践

### 1. 工具命名
- 使用清晰的名称，如 `GetRandomJoke` 而不是 `get_joke`
- 遵循PascalCase命名规范

### 2. 工具描述
- 提供详细的描述，帮助LLM理解何时使用此工具
- 包含使用格式示例
- 说明Action Input的要求

### 3. 错误处理
- 在Agent中实现适当的错误处理
- 提供清晰的错误消息
- 帮助LLM理解正确的格式

### 4. 配置管理
- 使用配置系统管理Agent参数
- 支持环境变量覆盖
- 提供合理的默认值

### 5. 测试
- 为新功能编写测试
- 测试工具函数
- 测试Agent集成

## 示例：完整的代码Agent

参考 `agents/example_code_agent.py` 查看完整的示例实现。

## 相关文档

- [快速开始](getting-started.md) - 安装和基本使用
- [架构概览](../architecture/overview.md) - 系统架构设计
- [API参考](../api/reference.md) - API文档

