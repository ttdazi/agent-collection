"""
反思策略 - 实现反思增强机制
"""
from typing import Dict, Any
from strategies.base_strategy import EnhancementStrategy
from agents.base_agent import BaseAgent
from agents.reflection_agent import ReflectionAgent
from graphs.reflection_graph import ReflectionGraph
from configs import config

class ReflectionStrategy(EnhancementStrategy):
    """反思策略 - 通过反思机制增强Agent输出"""
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(config)
        self._reflection_agent = None
    
    def enhance(self, agent: BaseAgent, input_data: Dict[str, Any], **kwargs) -> Any:
        """应用反思增强"""
        # 获取配置
        enhancement_config = config.DEFAULT_CONFIG.get("enhancement", {}).get("reflection", {})
        reflection_config = config.DEFAULT_CONFIG.get("reflection", {})
        # 合并配置
        merged_config = {**reflection_config, **enhancement_config, **self.config}
        
        # 检查是否启用
        if not merged_config.get("enable", False):
            return agent.invoke(input_data, **kwargs)
        
        max_iterations = merged_config.get("max_iterations", 2)
        
        try:
            # 创建反思Agent
            if self._reflection_agent is None:
                self._reflection_agent = ReflectionAgent(agent.llm)
            
            # 创建反思工作流
            reflection_graph = ReflectionGraph(
                agent=agent,
                reflection_agent=self._reflection_agent,
                max_iterations=max_iterations
            )
            
            # 执行反思工作流
            user_input = input_data.get("input", "")
            callbacks = kwargs.get("config", {}).get("callbacks", None)
            
            # ReflectionGraph.invoke现在返回字典
            result = reflection_graph.invoke(user_input, callbacks=callbacks)
            
            # 记录日志
            if merged_config.get("log_reflection", True):
                self._log_reflection(result)
            
            return {
                "output": result["output"],
                "reflection_metadata": {
                    "iterations": result["iterations"],
                    "reflection": result.get("reflection", ""),
                    "original_output": result.get("original_output", "")
                }
            }
        except Exception as e:
            print(f"⚠️ 反思机制执行出错: {e}")
            # 降级处理
            return agent.invoke(input_data, **kwargs)
    
    def _log_reflection(self, reflection_result: Dict[str, Any]) -> None:
        """记录反思过程"""
        # ... (保持原有日志逻辑)
        pass
