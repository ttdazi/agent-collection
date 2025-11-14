"""
笑话Agent - 专门用于讲笑话的Agent
"""
from langchain.agents import initialize_agent, AgentExecutor
from agents.base_agent import BaseAgent


class JokeAgent(BaseAgent):
    """笑话Agent"""
    
    def create_agent_executor(self) -> AgentExecutor:
        """创建笑话Agent执行器"""
        def handle_parsing_error(error):
            error_str = str(error)
            if "Missing 'Action Input:'" in error_str or "Action Input" in error_str:
                return "我需要重新格式化输出。让我使用正确的格式：\nAction: GetRandomJoke\nAction Input: joke"
            return f"输出格式错误，请重试。错误: {error_str}"
        
        return initialize_agent(
            tools=self.tools,
            llm=self.llm,
            agent=self.agent_type,
            verbose=self.config.get("verbose", True),
            max_iterations=self.config.get("max_iterations", 5),
            handle_parsing_errors=handle_parsing_error,
        )
