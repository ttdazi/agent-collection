"""
Google Gemini模型提供者实现
"""
from langchain_google_genai import ChatGoogleGenerativeAI
from core.model_provider import ModelProvider
from typing import Any, Dict
import os

class GeminiProvider(ModelProvider):
    """Google Gemini模型提供者"""
    
    def get_llm(self, config: Dict[str, Any]) -> ChatGoogleGenerativeAI:
        """
        创建Gemini LLM实例
        
        这个方法创建LangChain的Gemini LLM包装器，用于访问Google Gemini API。
        Gemini是云端模型服务，需要API密钥，但有免费额度。
        
        Args:
            config: 包含model、api_key、temperature等配置的字典
        
        Returns:
            ChatGoogleGenerativeAI LLM实例，可以用于LangChain Agent
        """
        # 从配置或环境变量获取API密钥
        api_key = config.get("api_key") or os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("GOOGLE_API_KEY未设置，请设置环境变量或配置文件中提供")
        
        # ========== Gemini LLM初始化 ==========
        # Google Gemini是云端AI模型服务
        # google_api_key: 从Google AI Studio获取的API密钥
        #   - 获取地址: https://aistudio.google.com/
        #   - 免费额度: 每日15亿Token
        # model: 模型名称（gemini-pro或gemini-1.5-flash）
        #   - gemini-pro: 功能更强大
        #   - gemini-1.5-flash: 更快更便宜
        # temperature: 控制输出的随机性（0-1，越高越随机）
        #
        # 当Agent调用这个LLM时，会：
        # 1. 通过LangChain SDK发送请求到Google Gemini API
        # 2. API地址: https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent
        # 3. 使用API密钥进行身份验证（Bearer Token）
        # 4. Gemini云端模型处理请求并返回结果
        # 5. 返回生成的文本给Agent
        #
        # 注意：
        # - Gemini API有免费额度限制，超出后需要付费
        # - 需要稳定的网络连接
        # - API密钥不要提交到代码仓库
        # ====================================
        return ChatGoogleGenerativeAI(
            model=config.get("model", "gemini-pro"),
            google_api_key=api_key,
            temperature=config.get("temperature", 0.7),
            timeout=30,  # 30秒超时
            max_retries=2,  # 最多重试2次
        )
    
    def validate_config(self, config: Dict[str, Any]) -> bool:
        """验证Gemini配置"""
        api_key = config.get("api_key") or os.getenv("GOOGLE_API_KEY")
        return bool(api_key)

