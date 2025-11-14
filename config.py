"""
配置文件 - 可以轻松修改模型和设置
"""
import os
from typing import Literal

# 模型类型
ModelType = Literal["ollama", "gemini", "deepseek"]

# 默认配置
DEFAULT_CONFIG = {
    # 当前使用的模型类型
    "model_type": os.getenv("MODEL_TYPE", "ollama"),  # 可以改为 "gemini", "deepseek"
    
    # 默认Agent类型
    "default_agent": os.getenv("DEFAULT_AGENT", "joke"),  # 可以改为其他Agent类型
    
    # Ollama配置
    "ollama": {
        "model": "qwen2.5:1.5b",  # 可以改为 "llama3.2:3b" 或其他
        "base_url": "http://localhost:11434",
        "temperature": 0.7,
    },
    
    # Google Gemini配置
    "gemini": {
        "model": "gemini-2.0-flash-exp",  # 或 "gemini-pro", "gemini-1.5-flash", "gemini-2.0-flash-exp"
        "api_key": os.getenv("GOOGLE_API_KEY", ""),
        "temperature": 0.7,
    },
    
    # DeepSeek配置（支持官方API和硅基流动）
    "deepseek": {
        "model": "deepseek-ai/DeepSeek-V3.2-Exp",  # 硅基流动模型，或 "deepseek-chat"（官方）
        "api_key": os.getenv("DEEPSEEK_API_KEY", "") or os.getenv("SILICONFLOW_API_KEY", ""),
        "base_url": "https://api.siliconflow.cn/v1",  # 硅基流动API，或 "https://api.deepseek.com/v1"（官方）
        "temperature": 0.7,
    },
    
    # Agent配置
    "agent": {
        "agent_type": "zero-shot-react-description",  # 可以改为其他类型
        "verbose": True,
        "max_iterations": 5,
    },
    
    # 日志配置
    "logging": {
        "llm_console_output": False,  # 是否在控制台显示LLM详细日志（False=只保存到文件）
        "llm_log_file": "logs/llm_interactions.log",  # LLM交互日志文件路径
        "log_level": "INFO",  # 日志级别：DEBUG, INFO, WARNING, ERROR
    }
}

