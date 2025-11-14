"""
笑话Agent - 专门用于讲笑话的Agent
"""
from langchain.agents import initialize_agent, AgentType
from agents.base_agent import BaseAgent
from typing import Dict, Any, List
from langchain.tools import Tool
from langchain.agents import AgentExecutor

class JokeAgent(BaseAgent):
    """笑话Agent"""
    
    def create_agent_executor(self) -> AgentExecutor:
        """创建笑话Agent执行器"""
        # 自定义解析错误处理函数
        def handle_parsing_error(error):
            """处理Agent输出解析错误，自动修复格式问题"""
            error_str = str(error)
            if "Missing 'Action Input:'" in error_str or "Action Input" in error_str:
                return "我需要重新格式化输出。让我使用正确的格式：\nAction: GetRandomJoke\nAction Input: joke"
            return f"输出格式错误，请重试。错误: {error_str}"
        
        agent = initialize_agent(
            tools=self.tools,
            llm=self.llm,
            agent=self.agent_type,
            verbose=self.config.get("verbose", True),
            max_iterations=self.config.get("max_iterations", 5),
            handle_parsing_errors=handle_parsing_error,
        )
        return agent

