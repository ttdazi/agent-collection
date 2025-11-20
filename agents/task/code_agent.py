"""
代码分析Agent示例 - 展示如何创建新Agent
这是一个示例，展示如何扩展系统添加新的Agent类型
"""
from langchain.agents import create_agent
from agents.base.base_agent import BaseAgent


class CodeAgent(BaseAgent):
    """
    代码分析Agent示例
    
    这个Agent可以用于：
    - 代码审查
    - 代码生成
    - 代码解释
    - 代码优化建议
    
    注意：这只是一个示例，需要配合相应的工具使用
    """
    
    def create_agent_executor(self):
        """创建代码Agent执行器（使用新的create_agent API）"""
        # 中文系统提示词
        system_prompt = """你是一个代码分析助手。

重要规则：
1. 当用户要求分析代码时，你必须使用工具来执行分析
2. 不能直接编造答案，必须通过工具获取结果
3. 严格按照ReAct格式思考和行动

可用工具：
- 根据实际注册的工具而定

使用格式：
思考: [你的思考过程]
行动: [工具名称]
行动输入: [工具输入]
观察: [工具返回的结果]
... (可以重复多次)
思考: 我现在知道最终答案了
最终答案: [对用户的最终回复]

请始终使用工具来分析代码，不要直接编造答案。"""
        
        # 使用新的create_agent API
        agent = create_agent(
            model=self.llm,
            tools=self.tools,
            system_prompt=system_prompt,
        )
        
        return agent

