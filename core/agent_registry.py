"""
Agent注册表 - 管理所有Agent类型定义
"""
from typing import Dict, List, Optional, Callable, Any
from dataclasses import dataclass
from langchain.agents import AgentType

@dataclass
class AgentDefinition:
    """Agent定义"""
    name: str  # Agent名称（唯一标识）
    display_name: str  # 显示名称
    description: str  # Agent描述
    tool_groups: List[str]  # 使用的工具组列表
    agent_type: AgentType  # LangChain Agent类型
    default_config: Dict[str, Any]  # 默认配置
    handler_func: Optional[Callable] = None  # 自定义处理函数（可选）


class AgentRegistry:
    """Agent注册表 - 单例模式"""
    
    _instance = None
    _agents: Dict[str, AgentDefinition] = {}
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def register_agent(self, definition: AgentDefinition) -> None:
        """
        注册Agent定义
        
        Args:
            definition: Agent定义
        """
        if definition.name in self._agents:
            print(f"⚠️ 警告: Agent '{definition.name}' 已存在，将被覆盖")
        
        self._agents[definition.name] = definition
    
    def get_agent_definition(self, name: str) -> Optional[AgentDefinition]:
        """获取Agent定义"""
        return self._agents.get(name)
    
    def list_agents(self) -> List[str]:
        """列出所有已注册的Agent名称"""
        return list(self._agents.keys())
    
    def get_all_definitions(self) -> Dict[str, AgentDefinition]:
        """获取所有Agent定义"""
        return self._agents.copy()
    
    def unregister_agent(self, name: str) -> bool:
        """注销Agent"""
        if name in self._agents:
            del self._agents[name]
            return True
        return False
    
    def clear(self) -> None:
        """清空所有Agent定义"""
        self._agents.clear()


# 全局Agent注册表实例
agent_registry = AgentRegistry()


def register_agent(
    name: str,
    display_name: str,
    description: str,
    tool_groups: List[str],
    agent_type: AgentType = AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    default_config: Dict[str, Any] = None
):
    """
    Agent注册装饰器
    
    使用示例:
        @register_agent(
            name="joke",
            display_name="笑话Agent",
            description="讲笑话的Agent",
            tool_groups=["joke"],
            agent_type=AgentType.ZERO_SHOT_REACT_DESCRIPTION
        )
        class JokeAgent:
            ...
    """
    def decorator(cls_or_func):
        definition = AgentDefinition(
            name=name,
            display_name=display_name,
            description=description,
            tool_groups=tool_groups,
            agent_type=agent_type,
            default_config=default_config or {},
            handler_func=cls_or_func if callable(cls_or_func) else None
        )
        agent_registry.register_agent(definition)
        return cls_or_func
    return decorator

