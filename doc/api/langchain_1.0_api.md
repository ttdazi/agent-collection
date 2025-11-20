# LangChain 1.0.5 API 使用指南

## create_agent API

### 函数签名

```python
from langchain.agents import create_agent

agent = create_agent(
    model: str | BaseChatModel,  # 必需：ChatModel实例
    tools: Sequence[BaseTool | Callable | dict[str, Any]] | None = None,  # 工具列表
    system_prompt: str | None = None,  # 系统提示词
    # ... 其他可选参数
) -> CompiledStateGraph
```

### 返回类型

- **返回**: `CompiledStateGraph[AgentState[ResponseT], ContextT, ...]`
- 这是一个LangGraph编译后的状态图，可以直接调用 `invoke` 方法

### 使用方法

```python
from langchain.agents import create_agent
from langchain_core.messages import HumanMessage

# 1. 创建agent
agent = create_agent(
    model=llm,
    tools=tools,
    system_prompt="你是一个助手。"
)

# 2. 调用agent
result = agent.invoke({
    "messages": [HumanMessage(content="用户输入")]
})

# 3. 获取结果
if "messages" in result and result["messages"]:
    last_message = result["messages"][-1]
    output = last_message.content
```

### 关键点

1. **输入格式**: `{"messages": [HumanMessage(...)]}`
2. **输出格式**: `{"messages": [AIMessage, ...]}`
3. **系统提示词**: 通过 `system_prompt` 参数传递
4. **工具**: 通过 `tools` 参数传递工具列表

### 与旧API的区别

**旧API (已废弃)**:
```python
from langchain.agents import initialize_agent, AgentType

agent = initialize_agent(
    tools=tools,
    llm=llm,
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True
)
```

**新API (LangChain 1.0+)**:
```python
from langchain.agents import create_agent

agent = create_agent(
    model=llm,
    tools=tools,
    system_prompt="系统提示词"
)
```

### 项目中的使用

在 `agents/task/joke_agent.py` 和 `agents/task/code_agent.py` 中：

```python
def create_agent_executor(self):
    agent = create_agent(
        model=self.llm,
        tools=self.tools,
        system_prompt=system_prompt,
    )
    return agent
```

然后在 `agents/base/base_agent.py` 中调用：

```python
executor = self.get_agent_executor()
result = executor.invoke(
    {"messages": [HumanMessage(content=input_data["input"])]},
    config=invoke_config
)
```

## 版本信息

- **LangChain版本**: 1.0.5
- **API状态**: 当前API用法正确，符合LangChain 1.0+规范

