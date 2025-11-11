"""
Agent工厂 - 根据配置创建不同类型的Agent
"""
from langchain.agents import initialize_agent, AgentType
from langchain.tools import Tool
from core.model_provider import ModelProvider
from typing import Dict, Any, List
import config

class AgentFactory:
    """Agent工厂类"""
    
    # 模型提供者映射（延迟导入避免循环依赖）
    _providers = None
    
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
    def create_agent(cls, model_type: str = None, custom_config: Dict = None):
        """
        创建Agent实例
        
        Args:
            model_type: 模型类型 ("ollama", "gemini")
            custom_config: 自定义配置（可选）
        
        Returns:
            Agent实例
        """
        # 使用自定义配置或默认配置
        model_type = model_type or config.DEFAULT_CONFIG["model_type"]
        config_dict = custom_config or config.DEFAULT_CONFIG
        
        # 获取模型提供者
        providers = cls._get_providers()
        provider = providers.get(model_type)
        if not provider:
            raise ValueError(f"不支持的模型类型: {model_type}")
        
        # 获取模型配置
        model_config = config_dict.get(model_type, {})
        
        # 验证配置
        if not provider.validate_config(model_config):
            raise ValueError(f"{model_type} 配置无效或服务不可用")
        
        # 创建LLM
        llm = provider.get_llm(model_config)
        
        # 获取工具
        from tools.joke_tools import get_joke_tools
        tools = get_joke_tools()
        
        # 获取Agent配置
        agent_config = config_dict.get("agent", {})
        
        # 创建Agent
        agent = initialize_agent(
            tools=tools,
            llm=llm,
            agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
            verbose=agent_config.get("verbose", True),
            max_iterations=agent_config.get("max_iterations", 5),
            handle_parsing_errors=True,
        )
        
        return agent
    
    @classmethod
    def get_available_models(cls) -> List[str]:
        """获取可用的模型列表"""
        providers = cls._get_providers()
        return list(providers.keys())

