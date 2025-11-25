# helloAgent 架构概览

## 目录结构

```
helloAgent/
├── agents/                      # Agent相关代码（扁平化结构）
│   ├── base_agent.py          # Agent基类
│   ├── joke_agent.py          # 笑话Agent
│   ├── code_agent.py          # 代码分析Agent
│   ├── reflection_agent.py    # 反思Agent
│   └── __init__.py
├── strategies/                  # 策略层（根目录独立）
│   ├── base_strategy.py       # 策略基类
│   ├── reflection_strategy.py # 反思策略
│   ├── strategy_manager.py    # 策略管理器
│   └── __init__.py
├── graphs/                      # 工作流层（根目录独立）
│   ├── reflection_graph.py    # 反思工作流
│   └── __init__.py
├── schemas/                     # 数据模型层（根目录独立）
│   ├── base_schema.py         # 基础Schema
│   ├── agent_schema.py        # Agent相关Schema
│   ├── workflow_schema.py     # 工作流Schema
│   └── __init__.py
├── configs/                     # 配置层（根目录独立）
│   ├── config.py              # 主配置文件
│   └── __init__.py
├── core/                        # 核心服务
│   ├── agent_factory.py       # Agent工厂
│   ├── agent_registry.py      # Agent注册表
│   ├── agent_service.py       # Agent服务
│   ├── tool_registry.py       # 工具注册表
│   └── llm_logger.py          # LLM日志记录
├── tools/                       # 工具集
│   └── joke_tools.py          # 笑话工具
├── tests/                       # 测试目录
│   ├── unit/                  # 单元测试
│   │   ├── test_agents.py
│   │   ├── test_graphs.py
│   │   ├── test_schemas.py
│   │   └── test_strategies.py
│   ├── integration/           # 集成测试
│   └── conftest.py            # pytest配置
├── static/                      # 静态资源
├── templates/                   # HTML模板
└── app.py                       # Flask应用入口
```

## 核心组件

### 1. Agent层（扁平化）

Agent层采用扁平化设计，所有Agent直接位于`agents/`目录：

- **base_agent.py**：Agent基类，提供通用接口
- **joke_agent.py**：笑话Agent，调用笑话工具
- **code_agent.py**：代码分析Agent
- **reflection_agent.py**：反思Agent，提供反思评估能力

### 2. 策略层（Strategies）

独立的策略管理层，位于根目录`strategies/`：

- **base_strategy.py**：策略基类，定义统一接口
- **reflection_strategy.py**：反思策略实现
- **strategy_manager.py**：策略管理器，支持按Agent配置策略

### 3. 工作流层（Graphs）

独立的LangGraph工作流层，位于根目录`graphs/`：

- **reflection_graph.py**：反思工作流，使用LangGraph构建

### 4. 数据模型层（Schemas）

使用Pydantic定义数据模型，位于根目录`schemas/`：

- **base_schema.py**：基础Schema类
- **agent_schema.py**：Agent相关数据模型
- **workflow_schema.py**：工作流状态模型

### 5. 配置层（Configs）

独立的配置管理，位于根目录`configs/`：

- **config.py**：主配置文件，支持按Agent配置策略

### 6. Core服务层

提供核心服务：

- **AgentFactory**：负责创建Agent实例
- **AgentRegistry**：注册和管理Agent定义
- **AgentService**：统一的Agent调用入口，集成策略管理
- **ToolRegistry**：注册和管理工具
- **LLMLogger**：记录LLM交互日志

### 7. 测试层（Tests）

完整的测试体系：

- **unit/**：单元测试（schemas、agents、strategies、graphs）
- **integration/**：集成测试

## 架构图

```
┌─────────────────────────────────────────────────┐
│                  Flask App                       │
│              (app.py - 路由层)                    │
└──────────────────┬──────────────────────────────┘
                   │
┌──────────────────▼──────────────────────────────┐
│            AgentService                          │
│         (业务逻辑层)                              │
│         集成StrategyManager                      │
└──────────────────┬──────────────────────────────┘
                   │
┌──────────────────▼──────────────────────────────┐
│         StrategyManager                          │
│         (策略应用层)                              │
└──────────────────┬──────────────────────────────┘
                   │
┌──────────────────▼──────────────────────────────┐
│            AgentFactory                          │
│         (Agent创建工厂)                          │
└──────┬──────────────────────┬───────────────────┘
       │                      │
┌──────▼──────┐      ┌────────▼────────┐
│   Agents/   │      │  Tools/         │
│  (扁平化)    │      │                 │
└─────────────┘      └─────────────────┘
       │                      │
┌──────▼──────────────────────▼────────┐
│         Strategies/                   │
│      (策略层-根目录)                   │
└───────────────────────────────────────┘
       │
┌──────▼──────────────────────┐
│         Graphs/              │
│      (工作流层-根目录)        │
└──────────────────────────────┘
```

## 数据流

```
用户请求
  ↓
Flask路由 (app.py)
  ↓
AgentService (业务逻辑)
  ↓
StrategyManager (应用增强策略)
  ↓  (如果配置了策略)
ReflectionGraph (反思工作流)
  ↓
Agent实例 (JokeAgent等)
  ↓
ChatModel (ChatOllama/ChatGoogleGenerativeAI)
  ↓
工具执行 (joke_tools等)
  ↓
返回结果
```

## 设计原则

1. **扁平化管理**：Agent、Strategies、Graphs、Schemas、Configs各自独立
2. **职责单一**：每个组件只负责一件事
3. **易于扩展**：通过继承和策略模式轻松添加新功能
4. **配置驱动**：通过配置文件控制行为，支持按Agent配置策略
5. **可观测性**：完整的日志记录系统
6. **数据验证**：使用Pydantic进行数据模型验证
7. **测试保障**：完整的单元测试和集成测试

## 技术栈

- **LangChain 1.0+**: 使用最新的 `create_agent` API
- **LangGraph**: 构建复杂的Agent工作流
- **Pydantic 2.0+**: 数据模型验证
- **ChatModel**: 统一使用ChatModel接口
- **Flask**: Web框架
- **pytest**: 测试框架

## 扩展点

1. **添加新Agent**：继承BaseAgent，放在`agents/`目录，注册到AgentFactory
2. **添加新策略**：实现EnhancementStrategy接口，放在`strategies/`目录
3. **添加新工作流**：使用LangGraph构建，放在`graphs/`目录
4. **添加新工具**：创建工具函数，注册到ToolRegistry
5. **添加新模型**：实现ModelProvider接口

## 相关文档

- [扩展指南](../guides/extension.md) - 如何扩展系统
- [反思机制](../guides/reflection.md) - 反思机制详解
