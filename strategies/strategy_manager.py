"""
策略管理器 - 管理增强策略的注册和应用
"""
from typing import Dict, List, Optional, Any
from strategies.base_strategy import EnhancementStrategy
from agents.base_agent import BaseAgent
from configs import config

class StrategyManager:
    """策略管理器 - 单例模式"""
    
    _instance = None
    _strategies: Dict[str, EnhancementStrategy] = {}
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def register_strategy(self, name: str, strategy: EnhancementStrategy) -> None:
        """注册策略"""
        if name in self._strategies:
            print(f"⚠️ 警告: 策略 '{name}' 已存在，将被覆盖")
        self._strategies[name] = strategy
    
    def get_strategy(self, name: str) -> Optional[EnhancementStrategy]:
        """获取策略"""
        return self._strategies.get(name)
    
    def list_strategies(self) -> List[str]:
        """列出所有已注册的策略名称"""
        return list(self._strategies.keys())
    
    def apply_strategies(self, agent: BaseAgent, input_data: Dict, **kwargs) -> Any:
        """
        按顺序应用所有启用的策略
        
        支持按Agent配置策略，优先级：
        1. Agent特定配置 (config.agents[agent_name].strategies)
        2. 全局增强配置 (config.enhancement.strategies)
        """
        # 获取Agent名称
        agent_name = getattr(agent, "name", "unknown")
        
        # 1. 尝试获取Agent特定策略配置
        agent_strategies = []
        if hasattr(config, "DEFAULT_CONFIG") and "agents" in config.DEFAULT_CONFIG:
            agent_config = config.DEFAULT_CONFIG["agents"].get(agent_name, {})
            agent_strategies = agent_config.get("strategies", [])
            
        # 2. 如果没有Agent特定配置，使用全局配置
        if not agent_strategies:
            enhancement_config = config.DEFAULT_CONFIG.get("enhancement", {})
            agent_strategies = enhancement_config.get("strategies", [])
            
            # 向后兼容逻辑
            if not agent_strategies:
                reflection_config = config.DEFAULT_CONFIG.get("reflection", {})
                if reflection_config.get("enable", False):
                    agent_strategies = ["reflection"]
        
        if not agent_strategies:
            # 如果没有配置策略，直接执行Agent
            return agent.invoke(input_data, **kwargs)
        
        # 按顺序应用策略
        result = input_data
        strategy_applied = False
        
        for strategy_name in agent_strategies:
            strategy = self.get_strategy(strategy_name)
            if strategy and strategy.is_enabled():
                try:
                    result = strategy.enhance(agent, result, **kwargs)
                    strategy_applied = True
                except Exception as e:
                    print(f"⚠️ 策略 '{strategy_name}' 执行出错: {e}")
                    continue
        
        # 如果没有任何策略被应用，直接执行Agent
        if not strategy_applied:
            return agent.invoke(input_data, **kwargs)
        
        return result
    
    def clear(self) -> None:
        """清空所有策略"""
        self._strategies.clear()


# 全局策略管理器实例
strategy_manager = StrategyManager()
