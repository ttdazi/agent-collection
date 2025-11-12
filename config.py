"""
配置文件 - 可以轻松修改模型和设置
"""
import os
from typing import Literal

# 模型类型
ModelType = Literal["ollama", "gemini"]

# 默认配置
DEFAULT_CONFIG = {
    # 当前使用的模型类型
    "model_type": os.getenv("MODEL_TYPE", "ollama"),  # 可以改为 "gemini"
    
    # Ollama配置
    "ollama": {
        "model": "qwen2.5:1.5b",  # 可以改为 "llama3.2:3b" 或其他
        "base_url": "http://localhost:11434",
        "temperature": 0.7,
    },
    
    # Google Gemini配置
    "gemini": {
        "model": "gemini-pro",  # 或 "gemini-1.5-flash"
        "api_key": os.getenv("GOOGLE_API_KEY", ""),
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

