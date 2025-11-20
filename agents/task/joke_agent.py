"""
笑话Agent - 专门用于讲笑话的Agent
"""
from langchain.agents import create_agent
from agents.base.base_agent import BaseAgent


class JokeAgent(BaseAgent):
    """笑话Agent"""
    
    def create_agent_executor(self):
        """创建笑话Agent执行器（使用新的create_agent API）"""
        # 中文系统提示词 - 更强调必须使用工具
        system_prompt = """你是一个专门讲笑话的智能助手。

⚠️ 重要规则（必须严格遵守）：
1. 当用户要求讲笑话时，你必须立即调用GetRandomJoke工具来获取笑话
2. 绝对禁止自己编造笑话，必须通过工具获取
3. 不要只是说"我会找笑话"，必须实际调用工具

可用工具：
- GetRandomJoke: 获取一个随机笑话。当用户要求讲笑话时，必须调用此工具。
- SearchJoke: 根据关键词搜索笑话。当用户指定了特定主题时使用此工具。

工作流程：
1. 用户要求讲笑话
2. 立即调用GetRandomJoke工具
3. 将工具返回的笑话内容直接告诉用户

请记住：必须调用工具，不能自己编造笑话！"""
        
        # 使用新的create_agent API
        agent = create_agent(
            model=self.llm,
            tools=self.tools,
            system_prompt=system_prompt,
        )
        
        return agent

