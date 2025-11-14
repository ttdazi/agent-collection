"""
工具注册表 - 管理所有可用工具，支持动态注册
"""
from typing import Dict, List, Callable, Optional
from langchain.tools import Tool
import inspect

class ToolRegistry:
    """工具注册表 - 单例模式"""
    
    _instance = None
    _tools: Dict[str, Tool] = {}
    _tool_groups: Dict[str, List[str]] = {}  # 工具组：组名 -> 工具名列表
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def register_tool(self, tool: Tool, group: str = "default") -> None:
        """
        注册工具
        
        Args:
            tool: LangChain Tool实例
            group: 工具所属组（用于按组获取工具）
        """
        if not isinstance(tool, Tool):
            raise ValueError(f"工具必须是Tool实例，当前类型: {type(tool)}")
        
        if tool.name in self._tools:
            print(f"⚠️ 警告: 工具 '{tool.name}' 已存在，将被覆盖")
        
        self._tools[tool.name] = tool
        
        # 添加到工具组
        if group not in self._tool_groups:
            self._tool_groups[group] = []
        if tool.name not in self._tool_groups[group]:
            self._tool_groups[group].append(tool.name)
    
    def register_tools(self, tools: List[Tool], group: str = "default") -> None:
        """批量注册工具"""
        for tool in tools:
            self.register_tool(tool, group)
    
    def get_tool(self, name: str) -> Optional[Tool]:
        """根据名称获取工具"""
        return self._tools.get(name)
    
    def get_tools(self, names: List[str] = None, group: str = None) -> List[Tool]:
        """
        获取工具列表
        
        Args:
            names: 工具名称列表，如果提供则只返回指定的工具
            group: 工具组名称，如果提供则返回该组的所有工具
        
        Returns:
            工具列表
        """
        if names:
            # 返回指定名称的工具
            return [self._tools[name] for name in names if name in self._tools]
        elif group:
            # 返回指定组的所有工具
            group_tool_names = self._tool_groups.get(group, [])
            return [self._tools[name] for name in group_tool_names if name in self._tools]
        else:
            # 返回所有工具
            return list(self._tools.values())
    
    def get_tool_names(self, group: str = None) -> List[str]:
        """获取工具名称列表"""
        if group:
            return self._tool_groups.get(group, [])
        return list(self._tools.keys())
    
    def list_groups(self) -> List[str]:
        """列出所有工具组"""
        return list(self._tool_groups.keys())
    
    def unregister_tool(self, name: str) -> bool:
        """注销工具"""
        if name in self._tools:
            del self._tools[name]
            # 从所有组中移除
            for group_tools in self._tool_groups.values():
                if name in group_tools:
                    group_tools.remove(name)
            return True
        return False
    
    def clear(self) -> None:
        """清空所有工具"""
        self._tools.clear()
        self._tool_groups.clear()


# 全局工具注册表实例
tool_registry = ToolRegistry()


def register_tool(group: str = "default"):
    """
    工具注册装饰器
    
    使用示例:
        @register_tool(group="joke")
        def get_joke_tools():
            return [Tool(...), Tool(...)]
    """
    def decorator(func: Callable):
        def wrapper(*args, **kwargs):
            tools = func(*args, **kwargs)
            if isinstance(tools, list):
                tool_registry.register_tools(tools, group=group)
            elif isinstance(tools, Tool):
                tool_registry.register_tool(tools, group=group)
            return tools
        return wrapper
    return decorator

