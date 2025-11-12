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
        
        # ========== LLM实例化 ==========
        # 通过Provider创建LangChain LLM实例
        # 这里会根据model_type创建对应的LLM：
        # - Ollama: 本地运行的模型（通过HTTP API调用）
        # - Gemini: Google云端模型（通过REST API调用）
        # LLM实例将用于Agent的推理和决策
        # ==============================
        llm = provider.get_llm(model_config)
        
        # 获取工具
        from tools.joke_tools import get_joke_tools
        tools = get_joke_tools()
        
        # 获取Agent配置
        agent_config = config_dict.get("agent", {})
        
        # ========== Agent创建 ==========
        # 使用LangChain创建ReAct模式的Agent
        # Agent会结合LLM和工具，实现：
        # 1. 理解用户意图（通过LLM）
        # 2. 选择合适工具（LLM决策）
        # 3. 执行工具获取结果
        # 4. 整合结果生成回复（LLM生成）
        # 
        # llm参数：传入LLM实例，Agent会通过它访问AI模型
        # handle_parsing_errors: 自定义错误处理函数，当LLM输出格式不符合ReAct格式时自动修复
        # ==============================
        
        # 自定义解析错误处理函数
        def handle_parsing_error(error):
            """处理Agent输出解析错误，自动修复格式问题"""
            # 如果缺少Action Input，自动添加
            error_str = str(error)
            if "Missing 'Action Input:'" in error_str or "Action Input" in error_str:
                # 返回修复后的格式，让Agent重试
                return "我需要重新格式化输出。让我使用正确的格式：\nAction: GetRandomJoke\nAction Input: joke"
            # 其他错误返回默认消息
            return f"输出格式错误，请重试。错误: {error_str}"
        
        agent = initialize_agent(
            tools=tools,
            llm=llm,  # 这里传入LLM实例，Agent会通过它访问AI模型
            agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
            verbose=agent_config.get("verbose", True),
            max_iterations=agent_config.get("max_iterations", 5),
            handle_parsing_errors=handle_parsing_error,  # 使用自定义错误处理
        )
        
        return agent
    
    @classmethod
    def get_available_models(cls) -> List[str]:
        """获取可用的模型列表"""
        providers = cls._get_providers()
        return list(providers.keys())

