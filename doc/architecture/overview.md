# 架构概览

## 系统架构

helloAgent 采用模块化、可扩展的架构设计，支持多Agent、多模型、多工具的动态组合。

## 核心组件

### 1. Agent系统

```
agents/
├── base/                  # Agent基类
│   └── base_agent.py     # Agent基类
├── task/                  # 任务Agent（执行具体任务）
│   ├── joke_agent.py     # 笑话Agent
│   └── code_agent.py     # 代码Agent
├── enhancement/           # 增强Agent（提供增强能力）
│   ├── reflection_agent.py    # 反思Agent
│   └── reflection_graph.py   # 反思工作流
└── strategies/            # 增强策略（可插拔的增强机制）
    ├── base_strategy.py       # 策略基类
    ├── reflection_strategy.py # 反思策略
    └── strategy_manager.py   # 策略管理器
```

**特点**：
- 统一的Agent接口（BaseAgent）
- 分类管理：任务Agent、增强Agent、策略分离
- 策略模式：可插拔的增强机制
- 每个Agent可以有自己的工具集和中文系统提示词
- 使用LangChain 1.0+的`create_agent` API

### 2. 工具系统

```
tools/
└── joke_tools.py          # 笑话工具
```

**特点**：
- 工具自动注册机制
- 支持工具分组
- 动态工具管理

### 3. 模型提供者

```
providers/
├── ollama_provider.py     # Ollama本地模型
└── gemini_provider.py     # Google Gemini云端模型
```

**特点**：
- 统一的Provider接口（返回ChatModel）
- 易于添加新模型
- 配置验证机制
- 支持Ollama（本地）和Gemini（云端）

### 4. 核心服务

```
core/
├── agent_factory.py       # Agent工厂
├── agent_service.py       # Agent服务层（集成策略管理器）
├── agent_registry.py      # Agent注册表
├── tool_registry.py       # 工具注册表
├── model_provider.py      # 模型提供者基类
└── llm_logger.py          # LLM日志记录器
```

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
└──────────────────┬──────────────────────────────┘
                   │
┌──────────────────▼──────────────────────────────┐
│            AgentFactory                          │
│         (Agent创建工厂)                          │
└──────┬──────────────────────┬───────────────────┘
       │                      │
┌──────▼──────┐      ┌────────▼────────┐
│ AgentRegistry│      │  ToolRegistry  │
│ (Agent注册表)│      │  (工具注册表)   │
└─────────────┘      └─────────────────┘
       │                      │
┌──────▼──────────────────────▼────────┐
│         ModelProvider                 │
│      (模型提供者接口)                  │
└──────┬──────────────────────┬─────────┘
       │                      │
┌──────▼──────┐      ┌────────▼────────┐
│ Ollama      │      │    Gemini       │
│ Provider    │      │    Provider     │
└─────────────┘      └─────────────────┘
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
  ↓
AgentFactory (创建Agent)
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

1. **单一职责**：每个模块只负责一个功能
2. **开闭原则**：对扩展开放，对修改封闭
3. **依赖注入**：通过注册表管理依赖
4. **接口抽象**：使用抽象基类定义接口

## 技术栈

- **LangChain 1.0+**: 使用最新的 `create_agent` API
- **ChatModel**: 统一使用ChatModel接口
- **中文Prompt**: 支持中文系统提示词
- **Flask**: Web框架

## 扩展点

1. **添加新任务Agent**：继承BaseAgent，使用`create_agent` API，注册到AgentRegistry
2. **添加新增强Agent**：继承BaseAgent，实现增强功能，放在`agents/enhancement/`目录
3. **添加新增强策略**：实现EnhancementStrategy接口，注册到StrategyManager
4. **添加新工具**：创建工具函数，注册到ToolRegistry
5. **添加新模型**：实现ModelProvider接口，返回ChatModel实例，注册到AgentFactory

## 相关文档

- [架构优化](optimization.md) - 架构优化历程
- [扩展指南](../guides/extension.md) - 如何扩展系统

