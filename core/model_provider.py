"""
模型提供者抽象基类 - 定义统一接口
"""
from abc import ABC, abstractmethod
from typing import Any, Dict, Union
from langchain_core.language_models import BaseChatModel, BaseLLM

class ModelProvider(ABC):
    """模型提供者抽象基类"""
    
    @abstractmethod
    def get_llm(self, config: Dict[str, Any]) -> Union[BaseChatModel, BaseLLM]:
        """获取LangChain模型实例（ChatModel或LLM）"""
        pass
    
    @abstractmethod
    def validate_config(self, config: Dict[str, Any]) -> bool:
        """验证配置是否有效"""
        pass

