# 项目Prompt分析报告

## 项目概述

这是一个基于LangChain的可扩展Agent系统，支持多模型切换（Ollama、Gemini等），采用模块化架构。项目使用中文系统提示词（system_prompt）来指导Agent的行为。

## Prompt使用架构

### 1. Prompt传递机制

项目使用LangChain 1.0+的`create_agent` API，通过`system_prompt`参数传递系统提示词：

```python
from langchain.agents import create_agent

agent = create_agent(
    model=self.llm,
    tools=self.tools,
    system_prompt=system_prompt,  # 系统提示词
)
```

### 2. Prompt位置

所有Agent的prompt定义在各自的Agent类中的`create_agent_executor`方法内。

---

## 当前项目中的Prompt

### 1. JokeAgent（笑话Agent）

**文件位置**: `agents/joke_agent.py`

**完整Prompt**:
```
你是一个专门讲笑话的智能助手。

重要规则：
1. 当用户要求讲笑话时，你必须使用工具（GetRandomJoke或SearchJoke）来获取笑话
2. 不能自己编造笑话，必须通过工具获取
3. 严格按照ReAct格式思考和行动

可用工具：
- GetRandomJoke: 获取一个随机笑话
- SearchJoke: 根据关键词搜索笑话

使用格式：
思考: [你的思考过程]
行动: [工具名称]
行动输入: [工具输入]
观察: [工具返回的结果]
... (可以重复多次)
思考: 我现在知道最终答案了
最终答案: [对用户的最终回复]

请始终使用工具来获取笑话，不要直接编造答案。
```

**特点**:
- 使用中文编写
- 明确要求使用工具，禁止编造
- 包含ReAct格式说明
- 列出可用工具及其用途

---

### 2. CodeAgent（代码分析Agent - 示例）

**文件位置**: `doc/guides/extension.md`（文档示例）

**完整Prompt**:
```
你是一个代码分析助手。
当用户要求分析代码时，你必须使用工具来执行分析。
不能直接编造答案，必须通过工具获取结果。
```

**特点**:
- 简洁的提示词示例
- 强调使用工具的重要性
- 禁止直接编造答案

---

## Prompt设计模式

### 1. 标准结构

项目中的prompt通常包含以下部分：

1. **角色定义**: "你是一个..."
2. **重要规则**: 明确的行为约束
3. **工具说明**: 列出可用工具
4. **格式要求**: ReAct格式说明（如适用）
5. **禁止事项**: 明确不允许的行为

### 2. 设计原则

- ✅ **使用中文**: 所有prompt都使用中文编写
- ✅ **明确约束**: 强调必须使用工具，禁止编造
- ✅ **格式指导**: 提供ReAct格式示例
- ✅ **工具说明**: 清晰列出可用工具及其用途

---

## Prompt日志记录

### LLM Logger功能

项目包含完整的LLM交互日志记录功能（`core/llm_logger.py`），可以记录：

- 📤 发送给ChatModel的完整prompt（messages）
- 📥 LLM返回的响应
- ❌ 错误信息

**日志位置**: `logs/llm_interactions.log`

**配置**: 在`config.py`中配置是否在控制台显示详细日志

---

## 扩展新Agent时的Prompt模板

根据项目文档，添加新Agent时的prompt模板：

```python
system_prompt = """你是一个[Agent角色描述]。

重要规则：
1. [规则1：必须使用工具]
2. [规则2：禁止行为]
3. [规则3：格式要求]

可用工具：
- [工具1名称]: [工具1描述]
- [工具2名称]: [工具2描述]

使用格式：
思考: [你的思考过程]
行动: [工具名称]
行动输入: [工具输入]
观察: [工具返回的结果]
... (可以重复多次)
思考: 我现在知道最终答案了
最终答案: [对用户的最终回复]

[其他重要说明]"""
```

---

## 关键代码位置

| 组件 | 文件路径 | 说明 |
|------|---------|------|
| JokeAgent Prompt | `agents/joke_agent.py:14-34` | 笑话Agent的完整系统提示词 |
| CodeAgent示例 | `doc/guides/extension.md:20-22` | 代码Agent的prompt示例 |
| Prompt传递 | `agents/joke_agent.py:37-41` | 使用create_agent API传递prompt |
| 日志记录 | `core/llm_logger.py:46-73` | 记录prompt和响应的日志功能 |

---

## 总结

1. **Prompt数量**: 当前项目中有1个实际使用的prompt（JokeAgent），1个文档示例prompt（CodeAgent）

2. **Prompt语言**: 全部使用中文

3. **Prompt风格**: 
   - 结构清晰，包含角色、规则、工具、格式说明
   - 强调工具使用，禁止直接编造答案
   - 提供ReAct格式指导

4. **扩展性**: 通过继承BaseAgent并实现`create_agent_executor`方法，可以轻松添加新的prompt

5. **可观测性**: 通过LLMLogger可以完整记录所有prompt交互过程

---

## 建议

1. **Prompt版本管理**: 考虑将prompt提取到独立文件或配置中，便于版本管理和A/B测试

2. **Prompt模板化**: 可以创建prompt模板系统，支持变量替换

3. **Prompt优化**: 根据实际使用效果，持续优化prompt内容

4. **多语言支持**: 如果需要支持多语言，可以考虑prompt的多语言版本
