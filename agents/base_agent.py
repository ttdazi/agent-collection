"""
Agent基类 - 定义Agent的通用接口
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, List
from langchain.agents import AgentExecutor
from langchain.tools import Tool

class BaseAgent(ABC):
    """Agent基类"""
    
    def __init__(self, name: str, tools: List[Tool], llm, agent_type, config: Dict[str, Any] = None):
        """
        初始化Agent
        
        Args:
            name: Agent名称
            tools: 工具列表
            llm: LLM实例
            agent_type: LangChain Agent类型
            config: Agent配置
        """
        self.name = name
        self.tools = tools
        self.llm = llm
        self.agent_type = agent_type
        self.config = config or {}
        self._agent_executor: AgentExecutor = None
    
    @abstractmethod
    def create_agent_executor(self) -> AgentExecutor:
        """创建Agent执行器"""
        pass
    
    def get_agent_executor(self) -> AgentExecutor:
        """获取Agent执行器（懒加载）"""
        if self._agent_executor is None:
            self._agent_executor = self.create_agent_executor()
        return self._agent_executor
    
    def invoke(self, input_data: Dict[str, Any], **kwargs) -> Any:
        """调用Agent"""
        executor = self.get_agent_executor()
        return executor.invoke(input_data, **kwargs)
    
    def get_description(self) -> str:
        """获取Agent描述"""
        return self.config.get("description", f"Agent: {self.name}")

