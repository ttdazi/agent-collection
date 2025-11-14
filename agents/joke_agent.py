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
            """处理Agent输出解析错误，提供更清晰的格式指导"""
            error_str = str(error)
            
            # 如果缺少Action Input，提供完整的格式示例
            if "Missing 'Action Input:'" in error_str or "Action Input" in error_str:
                return (
                    "我需要使用正确的ReAct格式。格式应该是：\n"
                    "Thought: [我的思考过程]\n"
                    "Action: [工具名称]\n"
                    "Action Input: [工具输入]\n\n"
                    "例如：\n"
                    "Thought: 用户要求讲笑话，我应该使用GetRandomJoke工具。\n"
                    "Action: GetRandomJoke\n"
                    "Action Input: joke"
                )
            
            # 如果只是格式错误，提供通用指导
            if "Could not parse" in error_str:
                return (
                    "输出格式不正确。请使用以下格式：\n"
                    "Thought: [思考]\n"
                    "Action: [工具名]\n"
                    "Action Input: [输入]\n"
                    "Observation: [观察结果]\n"
                    "Final Answer: [最终答案]"
                )
            
            return f"格式错误，请重试。错误: {error_str}"
        
        # 注意：initialize_agent 在 LangChain 0.1.0+ 中已弃用
        # 但为了兼容性，我们继续使用它，直到升级到支持新API的版本
        return initialize_agent(
            tools=self.tools,
            llm=self.llm,
            agent=self.agent_type,
            verbose=self.config.get("verbose", True),
            max_iterations=self.config.get("max_iterations", 5),
            handle_parsing_errors=handle_parsing_error,
            max_execution_time=None,  # 不限制执行时间
        )
