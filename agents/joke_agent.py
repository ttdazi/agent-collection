"""
笑话Agent - 专门用于讲笑话的Agent
"""
from langchain.agents import create_agent
from agents.base_agent import BaseAgent


class JokeAgent(BaseAgent):
    """笑话Agent"""
    
    def create_agent_executor(self):
        """创建笑话Agent执行器（使用新的create_agent API）"""
        # 中文系统提示词
        system_prompt = """你是一个专门讲笑话的智能助手。

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

请始终使用工具来获取笑话，不要直接编造答案。"""
        
        # 使用新的create_agent API
        agent = create_agent(
            model=self.llm,
            tools=self.tools,
            system_prompt=system_prompt,
        )
        
        return agent
