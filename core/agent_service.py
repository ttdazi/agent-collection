"""
Agent服务层 - 处理Agent相关的业务逻辑
"""
from typing import Dict, Any, List
from core.agent_factory import AgentFactory
from agents.base_agent import BaseAgent
from core.llm_logger import LLMLogger
import config


class AgentService:
    """Agent服务层"""
    
    def __init__(self):
        self._agents: Dict[str, BaseAgent] = {}
    
    def get_agent(self, agent_name: str = None, model_type: str = None) -> BaseAgent:
        """获取Agent实例（带缓存）"""
        agent_name = agent_name or config.DEFAULT_CONFIG.get("default_agent", "joke")
        model_type = model_type or config.DEFAULT_CONFIG.get("model_type", "ollama")
        cache_key = f"{agent_name}:{model_type}"
        
        if cache_key not in self._agents:
            try:
                self._agents[cache_key] = AgentFactory.create_agent(
                    agent_name=agent_name,
                    model_type=model_type
                )
            except Exception as e:
                raise ValueError(f"创建Agent失败: {str(e)}")
        
        return self._agents[cache_key]
    
    def invoke_agent(
        self,
        agent_name: str = None,
        user_input: str = "",
        callbacks: List = None
    ) -> Dict[str, Any]:
        """调用Agent处理用户输入"""
        try:
            agent = self.get_agent(agent_name=agent_name)
            
            if callbacks is None:
                callbacks = [LLMLogger()]
            elif not any(isinstance(cb, LLMLogger) for cb in callbacks):
                callbacks.append(LLMLogger())
            
            result = agent.invoke({"input": user_input}, config={"callbacks": callbacks})
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
        """更新配置"""
        try:
            model_type = config_data.get("model_type")
            agent_name = config_data.get("agent_name")
            
            if model_type and model_type not in AgentFactory.get_available_models():
                return {"success": False, "error": f"不支持的模型类型: {model_type}"}
            
            if agent_name and agent_name not in AgentFactory.get_available_agents():
                return {"success": False, "error": f"不支持的Agent类型: {agent_name}"}
            
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
            
            # 清除相关缓存
            self._clear_agent_cache(model_type, agent_name)
            
            # 验证配置
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
            return {"success": False, "error": str(e)}
    
    def _clear_agent_cache(self, model_type: str = None, agent_name: str = None):
        """清除Agent缓存"""
        if not (model_type or agent_name):
            self._agents.clear()
            return
        
        keys_to_remove = [
            key for key in self._agents.keys()
            if (agent_name and key.startswith(f"{agent_name}:")) or
               (model_type and key.endswith(f":{model_type}"))
        ]
        for key in keys_to_remove:
            del self._agents[key]
    
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


agent_service = AgentService()
