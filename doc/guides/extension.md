# 扩展指南

本指南介绍如何扩展系统，添加新的Agent、策略、工作流和工具。

## 1. 添加新的Agent

假设我们要添加一个天气查询Agent：

### 步骤1：创建Agent类

在 `agents/` 目录下创建 `weather_agent.py`：

```python
from agents.base_agent import BaseAgent
from langchain_core.tools import BaseTool
from typing import List, Dict, Any

class WeatherAgent(BaseAgent):
    """天气查询Agent"""
    
    def __init__(self, name: str, tools: List[BaseTool], llm, config: Dict[str, Any] = None):
        super().__init__(name, tools, llm, config)
        
    def get_system_prompt(self) -> str:
        return """你是一个专业的天气查询助手。
        
使用规则：
1. 当用户询问天气时，使用GetWeather工具
2. 提供准确的天气信息
3. 给出合适的建议"""
```

### 步骤2：创建工具（如需要）

在 `tools/` 目录下创建 `weather_tools.py`：

```python
from langchain_core.tools import StructuredTool
from core.tool_registry import tool_registry

def get_weather(city: str) -> str:
    """获取城市天气"""
    return f"{city}的天气：晴朗，25度"

def get_weather_tools():
    """获取天气工具"""
    tools = [
        StructuredTool.from_function(
            func=get_weather,
            name="GetWeather",
            description="获取指定城市的天气信息"
        ),
    ]
    tool_registry.register_tools(tools, group="weather")
    return tools
```

### 步骤3：在AgentFactory中注册

修改 `core/agent_factory.py`：

```python
from agents.weather_agent import WeatherAgent

class AgentFactory:
    _agent_classes = {
        "joke": JokeAgent,
        "weather": WeatherAgent,  # 添加这行
    }
```

### 步骤4：配置Agent

在 `configs/config.py` 中添加配置：

```python
"agents": {
    "weather": {
        "strategies": [],  # 不需要策略
        "description": "天气查询Agent"
    }
}
```

### 步骤5：编写测试

在 `tests/unit/test_agents.py` 中添加测试：

```python
def test_weather_agent_init():
    """测试WeatherAgent初始化"""
    llm = MagicMock()
    tools = []
    agent = WeatherAgent("weather", tools, llm)
    assert agent.name == "weather"
    assert agent.get_system_prompt() is not None
```

## 2. 添加增强策略

### 步骤1：创建策略类

在 `strategies/` 目录下创建新策略：

```python
from strategies.base_strategy import EnhancementStrategy
from agents.base_agent import BaseAgent
from typing import Dict, Any

class MyStrategy(EnhancementStrategy):
    """自定义策略"""
    
    def __init__(self, name: str):
        super().__init__(name)
    
    def enhance(self, agent: BaseAgent, input_data: Dict[str, Any], **kwargs) -> Any:
        """增强Agent的输出"""
        # 检查是否启用
        if not self._is_enabled(agent.name):
            return agent.invoke(input_data, **kwargs)
        
        # 实现增强逻辑
        result = agent.invoke(input_data, **kwargs)
        # ... 处理result
        return result
    
    def _is_enabled(self, agent_name: str) -> bool:
        """检查策略是否启用"""
        from configs import config
        
        # 优先检查Agent特定配置
        agents_config = config.DEFAULT_CONFIG.get("agents", {})
        agent_config = agents_config.get(agent_name, {})
        agent_strategies = agent_config.get("strategies", [])
        
        return self.name in agent_strategies
```

### 步骤2：注册策略

修改 `core/agent_service.py`：

```python
from strategies.my_strategy import MyStrategy

# 在AgentService初始化时
strategy_manager.register_strategy(MyStrategy("my_strategy"))
```

### 步骤3：更新配置

在 `configs/config.py` 中添加：

```python
"enhancement": {
    "strategies": ["my_strategy"],
    "my_strategy": {
        "enable": True,
        # 其他配置
    }
}
```

### 步骤4：编写策略测试

在 `tests/unit/test_strategies.py` 中添加测试。

## 3. 添加工作流

### 步骤1：定义状态模型

在 `schemas/workflow_schema.py` 中添加：

```python
from schemas.base_schema import BaseSchema
from pydantic import Field
from typing import Optional

class MyWorkflowState(BaseSchema):
    """自定义工作流状态"""
    user_input: str = Field(..., description="用户输入")
    result: Optional[str] = Field(default=None, description="结果")
```

### 步骤2：创建工作流

在 `graphs/` 目录下创建新的LangGraph工作流：

```python
from langgraph.graph import StateGraph, END
from schemas.workflow_schema import MyWorkflowState
from agents.base_agent import BaseAgent

class MyWorkflowGraph:
    """自定义工作流"""
    
    def __init__(self, agent: BaseAgent):
        self.agent = agent
        self.graph = self._create_graph()
    
    def _create_graph(self) -> StateGraph:
        """创建工作流图"""
        workflow = StateGraph(MyWorkflowState)
        
        # 添加节点
        workflow.add_node("process", self._process)
        
        # 设置入口
        workflow.set_entry_point("process")
        
        # 添加边
        workflow.add_edge("process", END)
        
        return workflow.compile()
    
    def _process(self, state: MyWorkflowState) -> dict:
        """处理节点"""
        result = self.agent.invoke({"input": state.user_input})
        return {"result": result.get("output", "")}
    
    def invoke(self, user_input: str) -> Dict[str, Any]:
        """执行工作流"""
        initial_state = MyWorkflowState(user_input=user_input)
        result = self.graph.invoke(initial_state)
        return result
```

### 步骤3：编写工作流测试

在 `tests/unit/test_graphs.py` 中添加测试。

## 4. 使用反思机制

反思机制通过LangGraph实现，位于 `graphs/reflection_graph.py`。

### 启用反思

在 `configs/config.py` 中配置：

```python
"enhancement": {
    "strategies": ["reflection"],
    "reflection": {
        "enable": True,
        "max_iterations": 2,
        "log_reflection": True,
    }
}
```

### 按Agent配置策略

```python
"agents": {
    "weather": {
        "strategies": ["reflection"],  # weather Agent需要反思
        "description": "天气查询Agent"
    },
    "joke": {
        "strategies": [],  # joke Agent不需要策略
        "description": "笑话Agent"
    }
}
```

## 5. 添加新工具

### 步骤1：实现工具函数

在 `tools/` 目录创建新文件：

```python
from langchain_core.tools import StructuredTool
from core.tool_registry import tool_registry

def my_tool_function(param: str) -> str:
    """工具功能描述"""
    return f"处理结果: {param}"

def get_my_tools():
    """获取工具列表"""
    tools = [
        StructuredTool.from_function(
            func=my_tool_function,
            name="MyTool",
            description="工具描述，帮助LLM理解何时使用"
        ),
    ]
    tool_registry.register_tools(tools, group="my_group")
    return tools
```

### 步骤2：确保工具被注册

在 `core/__init__.py` 中导入：

```python
try:
    from tools.my_tools import get_my_tools
    get_my_tools()
except ImportError:
    pass
```

## 6. 添加新模型

### 步骤1：实现ModelProvider接口

在 `providers/` 目录创建新文件：

```python
from core.model_provider import ModelProvider
from typing import Any, Dict
from langchain_openai import ChatOpenAI

class OpenAIProvider(ModelProvider):
    """OpenAI模型提供者"""
    
    def get_llm(self, config: Dict[str, Any]):
        """创建OpenAI ChatModel实例"""
        return ChatOpenAI(
            model=config.get("model", "gpt-3.5-turbo"),
            openai_api_key=config.get("api_key"),
            temperature=config.get("temperature", 0.7),
        )
    
    def validate_config(self, config: Dict[str, Any]) -> bool:
        """验证配置"""
        return bool(config.get("api_key"))
```

### 步骤2：注册Provider

在 `core/agent_factory.py` 中添加。

### 步骤3：添加配置

在 `configs/config.py` 中添加模型配置。

## 最佳实践

### 1. 工具命名
- 使用PascalCase命名规范（如 `GetRandomJoke`）
- 名称清晰明确

### 2. 工具描述
- 提供详细的描述
- 说明输入参数要求
- 包含使用场景示例

### 3. 数据验证
- 使用Pydantic定义数据模型
- 添加字段描述和约束
- 确保数据类型正确

### 4. 错误处理
- 实现适当的错误处理
- 提供清晰的错误消息
- 记录错误日志

### 5. 测试
- 为新功能编写单元测试
- 测试边界情况
- 使用Mock对象隔离依赖

### 6. 配置管理
- 使用配置文件管理参数
- 支持环境变量覆盖
- 提供合理的默认值

## 示例代码

参考现有实现：
- **Agent**: `agents/joke_agent.py`
- **Strategy**: `strategies/reflection_strategy.py`
- **Graph**: `graphs/reflection_graph.py`
- **Schema**: `schemas/workflow_schema.py`
- **Tools**: `tools/joke_tools.py`

## 相关文档

- [快速开始](getting-started.md) - 安装和基本使用
- [架构概览](../architecture/overview.md) - 系统架构设计
- [反思机制](reflection.md) - 反思机制详解
