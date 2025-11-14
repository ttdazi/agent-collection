"""
Ollama模型提供者实现
"""
from langchain_ollama import ChatOllama
from core.model_provider import ModelProvider
from typing import Any, Dict

class OllamaProvider(ModelProvider):
    """Ollama模型提供者"""
    
    def get_llm(self, config: Dict[str, Any]) -> ChatOllama:
        """
        创建Ollama LLM实例
        
        这个方法创建LangChain的Ollama LLM包装器，用于访问本地Ollama服务。
        Ollama通过HTTP API与本地模型通信，完全免费且无需API密钥。
        
        Args:
            config: 包含model、base_url、temperature等配置的字典
        
        Returns:
            Ollama LLM实例，可以用于LangChain Agent
        """
        # ========== Ollama ChatModel初始化 ==========
        # Ollama是本地LLM运行环境，通过HTTP API提供服务
        # base_url: Ollama服务地址（默认localhost:11434）
        # model: 要使用的模型名称（如qwen2.5:1.5b）
        # temperature: 控制输出的随机性（0-1，越高越随机）
        # 
        # 当Agent调用这个模型时，会：
        # 1. 发送HTTP POST请求到 http://localhost:11434/api/chat
        # 2. Ollama服务加载指定模型并生成回复
        # 3. 返回生成的文本给Agent
        # 
        # 优势：完全免费、本地运行、数据隐私好、无需网络（模型下载后）
        # ====================================
        return ChatOllama(
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

