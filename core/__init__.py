"""
核心模块初始化
自动注册默认工具和Agent
"""
# 导入工具以触发自动注册
try:
    from tools.joke_tools import get_joke_tools
    # 调用函数以触发工具注册
    get_joke_tools()
except ImportError:
    pass
