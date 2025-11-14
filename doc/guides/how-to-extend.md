# 如何扩展系统 - 快速指南

## 添加新Agent的完整示例

### 示例：创建一个代码分析Agent

#### 1. 创建工具（tools/code_tools.py）

```python
"""
代码相关工具
"""
from langchain.tools import Tool
from core.tool_registry import tool_registry

def analyze_code(code: str) -> str:
    """分析代码"""
    # 这里可以实现代码分析逻辑
    return f"代码分析结果: {code[:50]}..."

def generate_code(description: str) -> str:
    """根据描述生成代码"""
    # 这里可以实现代码生成逻辑
    return f"生成的代码: {description}"

def get_code_tools():
    """获取所有代码相关工具"""
    tools = [
        Tool(
            name="AnalyzeCode",
            func=analyze_code,
            description="分析代码，提供代码审查和建议。输入应该是代码片段。"
        ),
        Tool(
            name="GenerateCode",
            func=generate_code,
            description="根据描述生成代码。输入应该是代码功能的描述。"
        ),
    ]
    # 自动注册到工具注册表
    tool_registry.register_tools(tools, group="code")
    return tools
```

#### 2. 创建Agent类（agents/code_agent.py）

```python
"""
代码分析Agent
"""
from langchain.agents import initialize_agent, AgentType, AgentExecutor
from agents.base_agent import BaseAgent

class CodeAgent(BaseAgent):
    """代码分析Agent"""
    
    def create_agent_executor(self) -> AgentExecutor:
        """创建代码Agent执行器"""
        def handle_parsing_error(error):
            error_str = str(error)
            return f"代码分析出错，请重试。错误: {error_str}"
        
        agent = initialize_agent(
            tools=self.tools,
            llm=self.llm,
            agent=self.agent_type,
            verbose=self.config.get("verbose", True),
            max_iterations=self.config.get("max_iterations", 10),
            handle_parsing_errors=handle_parsing_error,
        )
        return agent
```

#### 3. 注册Agent（在core/agent_factory.py中）

```python
# 在_agent_classes字典中添加
from agents.code_agent import CodeAgent

_agent_classes = {
    "joke": JokeAgent,
    "code": CodeAgent,  # 添加新Agent
}
```

#### 4. 注册Agent定义（在应用启动时）

```python
# 在app.py的if __name__ == '__main__'之前添加
from core.agent_registry import agent_registry, AgentDefinition
from langchain.agents import AgentType
from tools.code_tools import get_code_tools

# 确保工具已注册
get_code_tools()

# 注册Agent定义
code_agent_def = AgentDefinition(
    name="code",
    display_name="代码分析Agent",
    description="用于代码分析、生成和审查的Agent",
    tool_groups=["code"],
    agent_type=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    default_config={
        "verbose": True,
        "max_iterations": 10,
    }
)
agent_registry.register_agent(code_agent_def)
```

#### 5. 使用新Agent

```bash
# 通过API调用
curl -X POST http://localhost:5000/api/agent/invoke \
  -H "Content-Type: application/json" \
  -d '{
    "agent_name": "code",
    "input": "分析这段Python代码：def hello(): print(\"Hello\")"
  }'
```

## 添加新工具的步骤

### 1. 创建工具函数

```python
def my_tool_function(input: str) -> str:
    """工具函数"""
    # 实现工具逻辑
    return "结果"
```

### 2. 创建Tool实例并注册

```python
from langchain.tools import Tool
from core.tool_registry import tool_registry

tool = Tool(
    name="MyTool",
    func=my_tool_function,
    description="工具描述，LLM会根据这个描述决定是否使用此工具"
)

# 注册工具
tool_registry.register_tool(tool, group="my_group")
```

### 3. 在Agent中使用

```python
# Agent定义时指定工具组
agent_def = AgentDefinition(
    name="my_agent",
    tool_groups=["my_group"],  # 使用这个工具组
    ...
)
```

## 添加新模型提供者

### 1. 实现ModelProvider接口

```python
# providers/my_provider.py
from core.model_provider import ModelProvider
from typing import Any, Dict

class MyProvider(ModelProvider):
    def get_llm(self, config: Dict[str, Any]):
        # 实现创建LLM的逻辑
        pass
    
    def validate_config(self, config: Dict[str, Any]) -> bool:
        # 实现配置验证逻辑
        return True
```

### 2. 在AgentFactory中注册

```python
# core/agent_factory.py
from providers.my_provider import MyProvider

_providers = {
    "ollama": OllamaProvider(),
    "gemini": GeminiProvider(),
    "my_provider": MyProvider(),  # 添加新提供者
}
```

## 最佳实践

1. **工具命名**: 使用清晰的名称，如`GetRandomJoke`而不是`get_joke`
2. **工具描述**: 提供详细的描述，帮助LLM理解何时使用此工具
3. **错误处理**: 在Agent中实现适当的错误处理
4. **配置管理**: 使用配置系统管理Agent参数
5. **测试**: 为新功能编写测试

## 常见问题

### Q: 如何让工具自动注册？
A: 在工具模块的`get_xxx_tools()`函数中调用`tool_registry.register_tools()`，然后在`core/__init__.py`中导入该函数。

### Q: 如何为不同Agent使用不同的模型？
A: 在调用`agent_service.invoke_agent()`时，可以通过配置系统设置不同Agent使用不同模型。

### Q: 如何添加自定义Agent类型？
A: 继承`BaseAgent`类，实现`create_agent_executor()`方法，然后在`AgentFactory._agent_classes`中注册。

### Q: 工具组的作用是什么？
A: 工具组用于将相关工具组织在一起，Agent可以指定使用哪些工具组，这样可以灵活组合工具。

