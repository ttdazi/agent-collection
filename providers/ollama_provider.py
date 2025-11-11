"""
Ollama模型提供者实现
"""
from langchain_community.llms import Ollama
from core.model_provider import ModelProvider
from typing import Any, Dict

class OllamaProvider(ModelProvider):
    """Ollama模型提供者"""
    
    def get_llm(self, config: Dict[str, Any]) -> Ollama:
        """创建Ollama LLM实例"""
        return Ollama(
            model=config.get("model", "qwen2.5:1.5b"),
            base_url=config.get("base_url", "http://localhost:11434"),
            temperature=config.get("temperature", 0.7),
        )
    
    def validate_config(self, config: Dict[str, Any]) -> bool:
        """验证Ollama配置"""
        try:
            import requests
            base_url = config.get("base_url", "http://localhost:11434")
            response = requests.get(f"{base_url}/api/tags", timeout=2)
            return response.status_code == 200
        except:
            return False

