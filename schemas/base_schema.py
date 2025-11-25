"""
基础数据模型
"""
from pydantic import BaseModel, Field, ConfigDict
from typing import Dict, Any, Optional

class BaseSchema(BaseModel):
    """基础Schema"""
    model_config = ConfigDict(extra="ignore")  # 忽略多余字段

class BaseResponse(BaseSchema):
    """基础响应模型"""
    success: bool = Field(default=True, description="是否成功")
    message: Optional[str] = Field(default=None, description="消息")
    error: Optional[str] = Field(default=None, description="错误信息")

