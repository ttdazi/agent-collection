"""
Agent服务层 - 处理Agent相关的业务逻辑
分离路由和业务逻辑，便于测试和复用
"""
from typing import Dict, Any, Optional, List
from core.agent_factory import AgentFactory
from agents.base_agent import BaseAgent
from core.llm_logger import LLMLogger
import config

class AgentService:
    """Agent服务层"""
    
    def __init__(self):
        self._agents: Dict[str, BaseAgent] = {}  # Agent缓存：agent_name -> Agent实例
    
    def get_agent(self, agent_name: str = None, model_type: str = None) -> BaseAgent:
        """
        获取Agent实例（带缓存）
        
        Args:
            agent_name: Agent名称，如果为None则使用默认Agent
            model_type: 模型类型，如果为None则使用配置中的默认模型
        
        Returns:
            BaseAgent实例
        """
        # 确定Agent名称
        if agent_name is None:
            agent_name = config.DEFAULT_CONFIG.get("default_agent", "joke")
        
        # 确定模型类型
        if model_type is None:
            model_type = config.DEFAULT_CONFIG.get("model_type", "ollama")
        
        # 生成缓存键
        cache_key = f"{agent_name}:{model_type}"
        
        # 检查缓存
        if cache_key not in self._agents:
            try:
                agent = AgentFactory.create_agent(
                    agent_name=agent_name,
                    model_type=model_type
                )
                self._agents[cache_key] = agent
            except Exception as e:
                raise ValueError(f"创建Agent失败: {str(e)}")
        
        return self._agents[cache_key]
    
    def invoke_agent(
        self,
        agent_name: str = None,
        user_input: str = "",
        callbacks: List = None
    ) -> Dict[str, Any]:
        """
        调用Agent处理用户输入
        
        Args:
            agent_name: Agent名称
            user_input: 用户输入
            callbacks: 回调函数列表
        
        Returns:
            包含success、output、error等字段的字典
        """
        try:
            agent = self.get_agent(agent_name=agent_name)
            
            # 创建LLM日志记录器
            if callbacks is None:
                callbacks = [LLMLogger()]
            elif not any(isinstance(cb, LLMLogger) for cb in callbacks):
                callbacks.append(LLMLogger())
            
            # 调用Agent
            result = agent.invoke(
                {"input": user_input},
                config={"callbacks": callbacks}
            )
            
            # 提取输出
            output = result.get("output", result if isinstance(result, str) else str(result))
            
            return {
                "success": True,
                "output": output,
                "agent_name": agent_name or config.DEFAULT_CONFIG.get("default_agent", "joke"),
                "model_type": config.DEFAULT_CONFIG.get("model_type", "ollama")
            }
        except Exception as e:
            return {
                "success": False,
                "output": f"错误: {str(e)}",
                "error": str(e)
            }
    
    def update_config(self, config_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        更新配置
        
        Args:
            config_data: 配置数据，包含model_type、agent_name、model、api_key等
        
        Returns:
            更新结果
        """
        try:
            model_type = config_data.get("model_type")
            agent_name = config_data.get("agent_name")
            
            if model_type and model_type not in AgentFactory.get_available_models():
                return {
                    "success": False,
                    "error": f"不支持的模型类型: {model_type}"
                }
            
            if agent_name and agent_name not in AgentFactory.get_available_agents():
                return {
                    "success": False,
                    "error": f"不支持的Agent类型: {agent_name}"
                }
            
            # 更新配置
            if model_type:
                config.DEFAULT_CONFIG["model_type"] = model_type
            
            if agent_name:
                config.DEFAULT_CONFIG["default_agent"] = agent_name
            
            # 更新模型特定配置
            if model_type == "ollama":
                if "model" in config_data:
                    config.DEFAULT_CONFIG["ollama"]["model"] = config_data["model"]
                if "base_url" in config_data:
                    config.DEFAULT_CONFIG["ollama"]["base_url"] = config_data["base_url"]
            elif model_type == "gemini":
                if "api_key" in config_data:
                    config.DEFAULT_CONFIG["gemini"]["api_key"] = config_data["api_key"]
                if "model" in config_data:
                    config.DEFAULT_CONFIG["gemini"]["model"] = config_data["model"]
            
            # 清除相关Agent缓存
            self._clear_agent_cache(model_type, agent_name)
            
            # 重新创建Agent以验证配置
            self.get_agent(agent_name=agent_name, model_type=model_type)
            
            return {
                "success": True,
                "message": "配置已更新",
                "model_type": model_type or config.DEFAULT_CONFIG.get("model_type"),
                "agent_name": agent_name or config.DEFAULT_CONFIG.get("default_agent", "joke"),
                "current_model_config": config.DEFAULT_CONFIG.get(
                    model_type or config.DEFAULT_CONFIG.get("model_type"), {}
                )
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def _clear_agent_cache(self, model_type: str = None, agent_name: str = None):
        """清除Agent缓存"""
        if model_type or agent_name:
            # 清除匹配的缓存
            keys_to_remove = []
            for key in self._agents.keys():
                agent_key, model_key = key.split(":")
                if (agent_name and agent_key == agent_name) or (model_type and model_key == model_type):
                    keys_to_remove.append(key)
            for key in keys_to_remove:
                del self._agents[key]
        else:
            # 清除所有缓存
            self._agents.clear()
    
    def get_config(self) -> Dict[str, Any]:
        """获取当前配置"""
        return {
            "model_type": config.DEFAULT_CONFIG.get("model_type", "ollama"),
            "default_agent": config.DEFAULT_CONFIG.get("default_agent", "joke"),
            "available_models": AgentFactory.get_available_models(),
            "available_agents": AgentFactory.get_available_agents(),
            "current_model_config": config.DEFAULT_CONFIG.get(
                config.DEFAULT_CONFIG.get("model_type", "ollama"), {}
            )
        }


# 全局服务实例
agent_service = AgentService()

