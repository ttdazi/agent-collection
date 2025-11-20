"""
Agent工厂 - 创建不同类型的Agent
"""
from core.agent_registry import agent_registry, AgentDefinition
from core.tool_registry import tool_registry
from agents.base.base_agent import BaseAgent
from agents.task.joke_agent import JokeAgent
from typing import Dict, Any, List
import config


class AgentFactory:
    """Agent工厂类"""
    
    _providers = None
    _agent_classes = {"joke": JokeAgent}
    
    @classmethod
    def _get_providers(cls):
        """延迟加载提供者"""
        if cls._providers is None:
            from providers.ollama_provider import OllamaProvider
            from providers.gemini_provider import GeminiProvider
            from providers.deepseek_provider import DeepSeekProvider
            cls._providers = {
                "ollama": OllamaProvider(),
                "gemini": GeminiProvider(),
                "deepseek": DeepSeekProvider(),
            }
        return cls._providers
    
    @classmethod
    def _register_default_agents(cls):
        """注册默认Agent定义"""
        try:
            from tools.joke_tools import get_joke_tools
            get_joke_tools()
        except ImportError:
            pass
        
        if "joke" not in agent_registry.list_agents():
            agent_def = AgentDefinition(
                name="joke",
                display_name="笑话Agent",
                description="专门用于讲笑话的Agent",
                tool_groups=["joke"],
                default_config={"verbose": True, "max_iterations": 5}
            )
            agent_registry.register_agent(agent_def)
    
    @classmethod
    def create_agent(
        cls,
        agent_name: str = None,
        model_type: str = None,
        custom_config: Dict = None
    ) -> BaseAgent:
        """创建Agent实例"""
        cls._register_default_agents()
        
        config_dict = custom_config or config.DEFAULT_CONFIG
        agent_name = agent_name or config_dict.get("default_agent", "joke")
        model_type = model_type or config_dict.get("model_type", "ollama")
        
        # 获取Agent定义
        agent_def = agent_registry.get_agent_definition(agent_name)
        if not agent_def:
            raise ValueError(f"未找到Agent定义: {agent_name}。可用Agent: {agent_registry.list_agents()}")
        
        # 获取模型提供者
        providers = cls._get_providers()
        provider = providers.get(model_type)
        if not provider:
            raise ValueError(f"不支持的模型类型: {model_type}。可用模型: {list(providers.keys())}")
        
        # 验证并创建LLM
        model_config = config_dict.get(model_type, {})
        if not provider.validate_config(model_config):
            raise ValueError(f"{model_type} 配置无效或服务不可用")
        llm = provider.get_llm(model_config)
        
        # 获取工具
        tools = []
        for group in agent_def.tool_groups:
            tools.extend(tool_registry.get_tools(group=group))
        
        if not tools:
            raise ValueError(f"Agent '{agent_name}' 没有可用的工具。工具组: {agent_def.tool_groups}")
        
        # 创建Agent实例
        agent_config = {**agent_def.default_config, **config_dict.get("agent", {})}
        agent_class = cls._agent_classes.get(agent_name, JokeAgent)
        
        return agent_class(
            name=agent_name,
            tools=tools,
            llm=llm,
            config=agent_config
        )
    
    @classmethod
    def get_available_models(cls) -> List[str]:
        """获取可用的模型列表"""
        return list(cls._get_providers().keys())
    
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
