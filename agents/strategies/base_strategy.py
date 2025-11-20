"""
增强策略基类 - 定义可插拔的增强机制接口
"""
from abc import ABC, abstractmethod
from typing import Dict, Any
from agents.base.base_agent import BaseAgent


class EnhancementStrategy(ABC):
    """增强策略基类 - 定义Agent增强机制的接口"""
    
    def __init__(self, config: Dict[str, Any] = None):
        """
        初始化策略
        
        Args:
            config: 策略配置
        """
        self.config = config or {}
        self.name = self.__class__.__name__
    
    @abstractmethod
    def enhance(self, agent: BaseAgent, input_data: Dict[str, Any], **kwargs) -> Any:
        """
        增强Agent的执行
        
        Args:
            agent: 要增强的Agent实例
            input_data: 输入数据
            **kwargs: 其他参数（如callbacks等）
        
        Returns:
            增强后的执行结果
        """
        pass
    
    def is_enabled(self) -> bool:
        """检查策略是否启用"""
        return self.config.get("enable", False)
    
    def get_description(self) -> str:
        """获取策略描述"""
        return self.config.get("description", f"Strategy: {self.name}")

