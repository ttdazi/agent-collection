"""
核心模块初始化 - 自动注册默认工具
"""
try:
    from tools.joke_tools import get_joke_tools
    get_joke_tools()
except ImportError:
    pass
