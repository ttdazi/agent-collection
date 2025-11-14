"""
Agent工厂 - 根据配置创建不同类型的Agent（重构版）
支持多Agent类型、工具注册、可扩展架构
"""
from langchain.agents import AgentType
from core.model_provider import ModelProvider
from core.agent_registry import agent_registry, AgentDefinition
from core.tool_registry import tool_registry
from agents.base_agent import BaseAgent
from agents.joke_agent import JokeAgent
from typing import Dict, Any, List, Optional
import config

class AgentFactory:
    """Agent工厂类 - 支持多Agent类型"""
    
    # 模型提供者映射（延迟导入避免循环依赖）
    _providers = None
    
    # Agent类映射
    _agent_classes = {
        "joke": JokeAgent,
        # 可以在这里添加更多Agent类型
    }
    
    @classmethod
    def _get_providers(cls):
        """延迟加载提供者，避免循环依赖"""
        if cls._providers is None:
            from providers.ollama_provider import OllamaProvider
            from providers.gemini_provider import GeminiProvider
            
            cls._providers = {
                "ollama": OllamaProvider(),
                "gemini": GeminiProvider(),
            }
        return cls._providers
    
    @classmethod
    def _register_default_agents(cls):
        """注册默认Agent定义"""
        # 确保工具已注册
        try:
            from tools.joke_tools import get_joke_tools
            get_joke_tools()  # 这会自动注册工具
        except ImportError:
            pass
        
        # 注册笑话Agent（如果尚未注册）
        if "joke" not in agent_registry.list_agents():
            from langchain.agents import AgentType
            agent_def = AgentDefinition(
                name="joke",
                display_name="笑话Agent",
                description="专门用于讲笑话的Agent",
                tool_groups=["joke"],
                agent_type=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
                default_config={
                    "verbose": True,
                    "max_iterations": 5,
                }
            )
            agent_registry.register_agent(agent_def)
    
    @classmethod
    def create_agent(
        cls,
        agent_name: str = None,
        model_type: str = None,
        custom_config: Dict = None
    ) -> BaseAgent:
        """
        创建Agent实例（新版本 - 支持多Agent类型）
        
        Args:
            agent_name: Agent名称（如"joke"），如果为None则使用配置中的默认Agent
            model_type: 模型类型 ("ollama", "gemini")，如果为None则使用配置中的默认模型
            custom_config: 自定义配置（可选）
        
        Returns:
            BaseAgent实例
        """
        # 注册默认Agent
        cls._register_default_agents()
        
        # 使用自定义配置或默认配置
        config_dict = custom_config or config.DEFAULT_CONFIG
        
        # 确定Agent名称
        if agent_name is None:
            agent_name = config_dict.get("default_agent", "joke")
        
        # 获取Agent定义
        agent_def = agent_registry.get_agent_definition(agent_name)
        if not agent_def:
            raise ValueError(f"未找到Agent定义: {agent_name}。可用Agent: {agent_registry.list_agents()}")
        
        # 确定模型类型
        if model_type is None:
            model_type = config_dict.get("model_type", "ollama")
        
        # 获取模型提供者
        providers = cls._get_providers()
        provider = providers.get(model_type)
        if not provider:
            raise ValueError(f"不支持的模型类型: {model_type}。可用模型: {list(providers.keys())}")
        
        # 获取模型配置
        model_config = config_dict.get(model_type, {})
        
        # 验证配置
        if not provider.validate_config(model_config):
            raise ValueError(f"{model_type} 配置无效或服务不可用")
        
        # 创建LLM实例
        llm = provider.get_llm(model_config)
        
        # 获取工具（从工具注册表）
        tools = tool_registry.get_tools(group=None)  # 获取所有工具
        if agent_def.tool_groups:
            # 如果Agent定义了工具组，只使用指定组的工具
            tools = []
            for group in agent_def.tool_groups:
                group_tools = tool_registry.get_tools(group=group)
                tools.extend(group_tools)
        
        if not tools:
            raise ValueError(f"Agent '{agent_name}' 没有可用的工具。工具组: {agent_def.tool_groups}")
        
        # 合并配置
        agent_config = {**agent_def.default_config, **config_dict.get("agent", {})}
        
        # 获取Agent类
        agent_class = cls._agent_classes.get(agent_name)
        if not agent_class:
            # 如果没有找到特定类，使用默认的JokeAgent
            agent_class = JokeAgent
        
        # 创建Agent实例
        agent = agent_class(
            name=agent_name,
            tools=tools,
            llm=llm,
            agent_type=agent_def.agent_type,
            config=agent_config
        )
        
        return agent
    
    @classmethod
    def create_legacy_agent(cls, model_type: str = None, custom_config: Dict = None):
        """
        创建传统Agent实例（向后兼容）
        
        这个方法保持与旧版本的兼容性，直接返回LangChain AgentExecutor
        """
        agent = cls.create_agent(agent_name="joke", model_type=model_type, custom_config=custom_config)
        return agent.get_agent_executor()
    
    @classmethod
    def get_available_models(cls) -> List[str]:
        """获取可用的模型列表"""
        providers = cls._get_providers()
        return list(providers.keys())
    
    @classmethod
    def get_available_agents(cls) -> List[str]:
        """获取可用的Agent列表"""
        cls._register_default_agents()
        return agent_registry.list_agents()
    
    @classmethod
    def register_agent_class(cls, agent_name: str, agent_class: type):
        """注册Agent类"""
        if not issubclass(agent_class, BaseAgent):
            raise ValueError(f"Agent类必须继承自BaseAgent，当前类型: {agent_class}")
        cls._agent_classes[agent_name] = agent_class
