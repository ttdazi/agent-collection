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
            
            # 确保输出是字符串
            if not isinstance(output, str):
                output = str(output)
            
            return {
                "success": True,
                "output": output,
                "agent_name": agent_name or config.DEFAULT_CONFIG.get("default_agent", "joke"),
                "model_type": config.DEFAULT_CONFIG.get("model_type", "ollama")
            }
        except Exception as e:
            error_msg = str(e)
            error_str = str(e)
            
            # 提供更友好的错误信息
            if "402" in error_str or "Insufficient Balance" in error_str or "余额不足" in error_str:
                error_msg = "💰 账户余额不足，请充值后重试。"
            elif "401" in error_str or "Unauthorized" in error_str or "Invalid API key" in error_str:
                error_msg = "🔑 API Key无效或已过期，请检查API Key是否正确。"
            elif "timeout" in error_msg.lower() or "timed out" in error_msg.lower():
                error_msg = "⏱️ 请求超时，请检查网络连接。如果使用Gemini，可能需要VPN。"
            elif "API key" in error_msg or "api_key" in error_msg.lower():
                error_msg = f"🔑 API Key错误: {error_msg}"
            elif "connection" in error_msg.lower() or "network" in error_msg.lower():
                error_msg = "🌐 网络连接失败，请检查网络或VPN设置。"
            elif "rate limit" in error_msg.lower() or "429" in error_str:
                error_msg = "🚦 请求频率过高，请稍后再试。"
            elif "model" in error_msg.lower() and ("not found" in error_msg.lower() or "invalid" in error_msg.lower()):
                error_msg = f"❌ 模型不存在或无效: {error_msg}"
            
            return {
                "success": False,
                "output": f"错误: {error_msg}",
                "error": error_msg
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
            # 如果指定了model_type，更新对应模型的配置
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
            elif model_type == "deepseek":
                if "api_key" in config_data:
                    config.DEFAULT_CONFIG["deepseek"]["api_key"] = config_data["api_key"]
                if "model" in config_data:
                    config.DEFAULT_CONFIG["deepseek"]["model"] = config_data["model"]
                if "base_url" in config_data:
                    config.DEFAULT_CONFIG["deepseek"]["base_url"] = config_data["base_url"]
            # 如果没有指定model_type，但提供了api_key，说明用户只想更新api_key
            elif not model_type and "api_key" in config_data:
                # 如果当前模型类型是需要API key的模型，更新api_key
                current_model_type = config.DEFAULT_CONFIG.get("model_type", "ollama")
                if current_model_type == "gemini":
                    config.DEFAULT_CONFIG["gemini"]["api_key"] = config_data["api_key"]
                elif current_model_type == "deepseek":
                    config.DEFAULT_CONFIG["deepseek"]["api_key"] = config_data["api_key"]
                else:
                    # 如果当前不是需要API key的模型，也保存api_key（可能是为后续切换准备）
                    # 尝试保存到deepseek（优先）或gemini
                    if "deepseek" in config.DEFAULT_CONFIG:
                        config.DEFAULT_CONFIG["deepseek"]["api_key"] = config_data["api_key"]
                    elif "gemini" in config.DEFAULT_CONFIG:
                        config.DEFAULT_CONFIG["gemini"]["api_key"] = config_data["api_key"]
            
            # 清除相关缓存
            self._clear_agent_cache(model_type, agent_name)
            
            # 验证配置（只有在提供了model_type且配置完整时才验证）
            if model_type:
                # 检查配置是否完整
                model_config = config.DEFAULT_CONFIG.get(model_type, {})
                if model_type in ["gemini", "deepseek"]:
                    # 对于需要API key的模型，如果API key为空，允许切换但不验证
                    api_key = model_config.get("api_key") or config_data.get("api_key")
                    if not api_key:
                        # API key为空，允许切换但不验证
                        return {
                            "success": True,
                            "message": "模型类型已切换，请输入API Key",
                            "model_type": model_type,
                            "agent_name": agent_name or config.DEFAULT_CONFIG.get("default_agent", "joke"),
                            "current_model_config": model_config,
                            "warning": "API Key未设置，请先输入API Key"
                        }
                
                # 配置完整，尝试验证
                try:
                    self.get_agent(agent_name=agent_name, model_type=model_type)
                except Exception as e:
                    # 如果验证失败，返回错误但不阻止配置保存
                    error_msg = str(e)
                    if "API key" in error_msg or "api_key" in error_msg.lower() or "配置无效" in error_msg:
                        return {
                            "success": True,
                            "message": "模型类型已切换，但配置验证失败",
                            "model_type": model_type,
                            "agent_name": agent_name or config.DEFAULT_CONFIG.get("default_agent", "joke"),
                            "current_model_config": model_config,
                            "warning": f"请检查配置: {error_msg}"
                        }
                    return {
                        "success": False,
                        "error": f"配置验证失败: {error_msg}",
                        "message": "配置已保存，但验证失败，请检查配置是否正确"
                    }
            
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
            error_msg = str(e)
            # 提供更友好的错误信息
            if "API key" in error_msg or "api_key" in error_msg.lower():
                error_msg = f"API Key配置错误: {error_msg}。请检查API Key是否正确。"
            elif "model" in error_msg.lower() and "not found" in error_msg.lower():
                error_msg = f"模型不存在: {error_msg}。请检查模型名称是否正确。"
            return {"success": False, "error": error_msg}
    
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
