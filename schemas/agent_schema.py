"""
Agent相关数据模型
"""
from typing import List, Dict, Any, Optional
from pydantic import Field
from schemas.base_schema import BaseSchema

class AgentState(BaseSchema):
    """Agent状态模型"""
    name: str = Field(..., description="Agent名称")
    input: str = Field(..., description="当前输入")
    output: Optional[str] = Field(default=None, description="当前输出")
    history: List[Dict[str, Any]] = Field(default_factory=list, description="对话历史")

class AgentResponse(BaseSchema):
    """Agent响应模型"""
    output: str = Field(..., description="Agent输出内容")
    agent_name: str = Field(..., description="Agent名称")
    model_type: str = Field(default="unknown", description="使用的模型类型")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="元数据")
    tool_calls: List[Dict[str, Any]] = Field(default_factory=list, description="工具调用记录")

