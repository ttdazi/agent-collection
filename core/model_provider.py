"""
模型提供者抽象基类 - 定义统一接口
"""
from abc import ABC, abstractmethod
from langchain.llms.base import LLM
from typing import Any, Dict

class ModelProvider(ABC):
    """模型提供者抽象基类"""
    
    @abstractmethod
    def get_llm(self, config: Dict[str, Any]) -> LLM:
        """获取LangChain LLM实例"""
        pass
    
    @abstractmethod
    def validate_config(self, config: Dict[str, Any]) -> bool:
        """验证配置是否有效"""
        pass

