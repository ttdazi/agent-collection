"""
反思策略 - 实现反思增强机制
"""
from typing import Dict, Any
from agents.strategies.base_strategy import EnhancementStrategy
from agents.base.base_agent import BaseAgent
from agents.enhancement.reflection_agent import ReflectionAgent
from agents.enhancement.reflection_graph import ReflectionGraph
import config


class ReflectionStrategy(EnhancementStrategy):
    """反思策略 - 通过反思机制增强Agent输出"""
    
    def __init__(self, config: Dict[str, Any] = None):
        """
        初始化反思策略
        
        Args:
            config: 策略配置
        """
        super().__init__(config)
        self._reflection_agent = None
    
    def enhance(self, agent: BaseAgent, input_data: Dict[str, Any], **kwargs) -> Any:
        """
        应用反思增强
        
        Args:
            agent: 要增强的Agent实例
            input_data: 输入数据
            **kwargs: 其他参数（如callbacks等）
        
        Returns:
            增强后的执行结果
        """
        # 获取配置（优先使用enhancement配置，向后兼容reflection配置）
        enhancement_config = config.DEFAULT_CONFIG.get("enhancement", {}).get("reflection", {})
        reflection_config = config.DEFAULT_CONFIG.get("reflection", {})
        # 合并配置，enhancement配置优先
        merged_config = {**reflection_config, **enhancement_config, **self.config}
        
        # 检查是否启用
        is_enabled = merged_config.get("enable", False)
        
        if not is_enabled:
            # 如果策略未启用，直接返回普通执行结果
            return agent.invoke(input_data, **kwargs)
        
        max_iterations = merged_config.get("max_iterations", 2)
        
        try:
            # 创建反思Agent（如果还没有创建）
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
            result = reflection_graph.invoke(user_input, callbacks=callbacks)
            
            # 记录反思过程（如果启用）
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
        except ImportError as e:
            # 如果LangGraph未安装，回退到普通模式
            print(f"⚠️ LangGraph未安装，无法使用反思机制: {e}")
            print("请运行: pip install langgraph>=0.2.0")
            return agent.invoke(input_data, **kwargs)
        except Exception as e:
            # 如果反思机制出错，回退到普通模式
            print(f"⚠️ 反思机制执行出错，回退到普通模式: {e}")
            return agent.invoke(input_data, **kwargs)
    
    def _log_reflection(self, reflection_result: Dict[str, Any]) -> None:
        """记录反思过程"""
        try:
            log_config = config.DEFAULT_CONFIG.get("logging", {})
            log_file = log_config.get("llm_log_file", "logs/llm_interactions.log")
            
            from datetime import datetime
            import os
            
            # 确保日志目录存在
            log_dir = os.path.dirname(log_file)
            if log_dir and not os.path.exists(log_dir):
                os.makedirs(log_dir, exist_ok=True)
            
            # 写入反思日志
            with open(log_file, 'a', encoding='utf-8') as f:
                f.write("\n" + "="*80 + "\n")
                f.write(f"🔄 反思机制执行记录 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write("="*80 + "\n")
                f.write(f"迭代次数: {reflection_result.get('iterations', 0)}\n")
                f.write(f"\n原始输出:\n{reflection_result.get('original_output', '')}\n")
                f.write(f"\n反思评估:\n{reflection_result.get('reflection', '')}\n")
                f.write(f"\n最终输出:\n{reflection_result.get('output', '')}\n")
                f.write("="*80 + "\n\n")
        except Exception as e:
            print(f"⚠️ 记录反思日志失败: {e}")

