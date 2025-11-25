"""
配置相关数据模型
"""
from typing import List, Dict, Any, Optional, Literal
from pydantic import Field
from schemas.base_schema import BaseSchema

class StrategyConfig(BaseSchema):
    """策略配置"""
    strategies: List[str] = Field(default_factory=list, description="启用的策略列表")

class AgentConfig(BaseSchema):
    """Agent配置"""
    strategies: List[str] = Field(default_factory=list, description="该Agent启用的策略列表")
    description: Optional[str] = Field(default=None, description="Agent描述")
    verbose: bool = Field(default=True, description="是否显示详细日志")
    max_iterations: int = Field(default=5, description="最大迭代次数")

class ReflectionConfig(BaseSchema):
    """反思机制配置"""
    enable: bool = Field(default=False, description="是否启用")
    max_iterations: int = Field(default=2, description="最大迭代次数")
    log_reflection: bool = Field(default=True, description="是否记录日志")

class ModelConfig(BaseSchema):
    """模型配置"""
    model: str = Field(..., description="模型名称")
    base_url: Optional[str] = Field(default=None, description="API基础地址")
    api_key: Optional[str] = Field(default=None, description="API Key")
    temperature: float = Field(default=0.7, description="温度参数")

class AppConfig(BaseSchema):
    """应用总配置"""
    model_type: Literal["ollama", "gemini", "deepseek"] = Field(default="ollama", description="当前模型类型")
    default_agent: str = Field(default="joke", description="默认Agent")
    
    # 模型配置
    ollama: ModelConfig
    gemini: ModelConfig
    deepseek: ModelConfig
    
    # 策略配置
    enhancement: StrategyConfig = Field(default_factory=StrategyConfig)
    reflection: ReflectionConfig = Field(default_factory=ReflectionConfig)
    
    # Agent特定配置
    agents: Dict[str, AgentConfig] = Field(default_factory=dict, description="各Agent的配置")

