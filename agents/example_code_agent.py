"""
代码分析Agent示例 - 展示如何创建新Agent
这是一个示例，展示如何扩展系统添加新的Agent类型
"""
from langchain.agents import initialize_agent, AgentType, AgentExecutor
from agents.base_agent import BaseAgent
from typing import Dict, Any

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
    
    def create_agent_executor(self) -> AgentExecutor:
        """创建代码Agent执行器"""
        # 可以自定义错误处理
        def handle_parsing_error(error):
            error_str = str(error)
            return f"代码分析出错，请重试。错误: {error_str}"
        
        agent = initialize_agent(
            tools=self.tools,
            llm=self.llm,
            agent=self.agent_type,
            verbose=self.config.get("verbose", True),
            max_iterations=self.config.get("max_iterations", 10),  # 代码分析可能需要更多迭代
            handle_parsing_errors=handle_parsing_error,
        )
        return agent

