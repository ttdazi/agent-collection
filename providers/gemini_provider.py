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
        """创建Gemini LLM实例"""
        api_key = config.get("api_key") or os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("GOOGLE_API_KEY未设置，请设置环境变量或配置文件中提供")
        
        return ChatGoogleGenerativeAI(
            model=config.get("model", "gemini-pro"),
            google_api_key=api_key,
            temperature=config.get("temperature", 0.7),
        )
    
    def validate_config(self, config: Dict[str, Any]) -> bool:
        """验证Gemini配置"""
        api_key = config.get("api_key") or os.getenv("GOOGLE_API_KEY")
        return bool(api_key)

