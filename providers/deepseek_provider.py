"""
DeepSeek模型提供者实现
支持DeepSeek官方API和硅基流动（SiliconFlow）API
"""
from langchain_openai import ChatOpenAI
from core.model_provider import ModelProvider
from typing import Any, Dict
import os

class DeepSeekProvider(ModelProvider):
    """DeepSeek模型提供者（支持官方API和硅基流动）"""
    
    def get_llm(self, config: Dict[str, Any]) -> ChatOpenAI:
        """
        创建DeepSeek LLM实例
        
        这个方法创建LangChain的DeepSeek LLM包装器，支持：
        1. DeepSeek官方API: https://api.deepseek.com/v1
        2. 硅基流动API: https://api.siliconflow.cn/v1
        
        Args:
            config: 包含model、api_key、base_url、temperature等配置的字典
        
        Returns:
            ChatOpenAI LLM实例（兼容OpenAI API），可以用于LangChain Agent
        """
        # 从配置或环境变量获取API密钥
        api_key = config.get("api_key") or os.getenv("DEEPSEEK_API_KEY") or os.getenv("SILICONFLOW_API_KEY")
        if not api_key:
            raise ValueError("API Key未设置，请设置DEEPSEEK_API_KEY或SILICONFLOW_API_KEY环境变量，或在配置文件中提供")
        
        # 获取base_url，默认使用硅基流动（国内更稳定）
        base_url = config.get("base_url", "https://api.siliconflow.cn/v1")
        
        # 获取模型名称
        # 硅基流动格式: deepseek-ai/DeepSeek-V3.2-Exp
        # DeepSeek官方格式: deepseek-chat
        model = config.get("model", "deepseek-ai/DeepSeek-V3.2-Exp")
        
        # ========== DeepSeek LLM初始化 ==========
        # 支持两种API服务：
        # 1. DeepSeek官方API: https://api.deepseek.com/v1
        #    - 模型: deepseek-chat, deepseek-coder
        #    - 获取地址: https://platform.deepseek.com/
        # 2. 硅基流动API: https://api.siliconflow.cn/v1
        #    - 模型: deepseek-ai/DeepSeek-V3.2-Exp, deepseek-ai/DeepSeek-V3等
        #    - 获取地址: https://siliconflow.cn/
        #    - 国内可用，无需VPN，价格相对便宜
        #
        # 当Agent调用这个LLM时，会：
        # 1. 通过LangChain SDK发送请求到指定的API
        # 2. 使用API密钥进行身份验证（Bearer Token）
        # 3. 云端模型处理请求并返回结果
        # 4. 返回生成的文本给Agent
        #
        # 注意：
        # - API需要付费，但价格相对便宜
        # - 需要稳定的网络连接
        # - API密钥不要提交到代码仓库
        # - 硅基流动支持中文，无需VPN（国内可用）
        # ====================================
        return ChatOpenAI(
            model=model,
            api_key=api_key,
            base_url=base_url,
            temperature=config.get("temperature", 0.7),
            timeout=30,  # 30秒超时
            max_retries=2,  # 最多重试2次
        )
    
    def validate_config(self, config: Dict[str, Any]) -> bool:
        """验证DeepSeek配置"""
        api_key = config.get("api_key") or os.getenv("DEEPSEEK_API_KEY") or os.getenv("SILICONFLOW_API_KEY")
        return bool(api_key)

