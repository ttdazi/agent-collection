"""
Agent基类 - 定义Agent的通用接口
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Union
from langchain_core.tools import Tool

class BaseAgent(ABC):
    """Agent基类"""
    
    def __init__(self, name: str, tools: List[Tool], llm, config: Dict[str, Any] = None):
        """
        初始化Agent
        
        Args:
            name: Agent名称
            tools: 工具列表
            llm: ChatModel实例
            config: Agent配置
        """
        self.name = name
        self.tools = tools
        self.llm = llm
        self.config = config or {}
        self._agent_executor = None
    
    @abstractmethod
    def create_agent_executor(self):
        """创建Agent执行器（返回create_agent创建的agent）"""
        pass
    
    def get_agent_executor(self):
        """获取Agent执行器（懒加载）"""
        if self._agent_executor is None:
            self._agent_executor = self.create_agent_executor()
        return self._agent_executor
    
    def invoke(self, input_data: Dict[str, Any], **kwargs) -> Any:
        """调用Agent"""
        executor = self.get_agent_executor()
        # 新API使用messages格式
        if "input" in input_data:
            from langchain_core.messages import HumanMessage
            messages = [HumanMessage(content=input_data["input"])]
            result = executor.invoke({"messages": messages}, **kwargs)
            # 提取最后一条消息的内容
            if "messages" in result and result["messages"]:
                last_message = result["messages"][-1]
                if hasattr(last_message, "content"):
                    return {"output": last_message.content}
                elif hasattr(last_message, "text"):
                    return {"output": last_message.text}
            return result
        else:
            return executor.invoke(input_data, **kwargs)
    
    def get_description(self) -> str:
        """获取Agent描述"""
        return self.config.get("description", f"Agent: {self.name}")

