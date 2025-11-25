"""
工作流相关数据模型
"""
from typing import List, Any, Optional
from pydantic import Field
from schemas.base_schema import BaseSchema

class WorkflowState(BaseSchema):
    """工作流基础状态"""
    user_input: str = Field(..., description="用户输入")
    final_output: Optional[str] = Field(default=None, description="最终输出")
    errors: List[str] = Field(default_factory=list, description="错误列表")

class ReflectionState(WorkflowState):
    """反思工作流状态"""
    agent_output: str = Field(default="", description="Agent的初始输出")
    reflection: str = Field(default="", description="反思评估结果")
    improved_output: str = Field(default="", description="改进后的输出")
    iteration: int = Field(default=0, ge=0, description="当前迭代次数")
    max_iterations: int = Field(default=2, ge=1, description="最大迭代次数")
    should_continue: bool = Field(default=True, description="是否继续迭代")
    original_output: str = Field(default="", description="原始输出备份")
    callbacks_handler: Optional[Any] = Field(default=None, description="Callbacks处理器", exclude=True)

