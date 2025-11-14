"""
工具注册表 - 管理所有可用工具
"""
from typing import Dict, List, Optional
from langchain.tools import Tool


class ToolRegistry:
    """工具注册表 - 单例模式"""
    
    _instance = None
    _tools: Dict[str, Tool] = {}
    _tool_groups: Dict[str, List[str]] = {}
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def register_tool(self, tool: Tool, group: str = "default") -> None:
        """注册工具"""
        if not isinstance(tool, Tool):
            raise ValueError(f"工具必须是Tool实例，当前类型: {type(tool)}")
        
        # 如果工具已存在且在同一组，跳过注册
        if tool.name in self._tools:
            existing_groups = [g for g, tools in self._tool_groups.items() if tool.name in tools]
            if group in existing_groups:
                return  # 已注册，跳过
            print(f"⚠️ 警告: 工具 '{tool.name}' 已存在，将被覆盖")
        
        self._tools[tool.name] = tool
        
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
        """获取工具列表"""
        if names:
            return [self._tools[name] for name in names if name in self._tools]
        elif group:
            group_tool_names = self._tool_groups.get(group, [])
            return [self._tools[name] for name in group_tool_names if name in self._tools]
        else:
            return list(self._tools.values())
    
    def get_tool_names(self, group: str = None) -> List[str]:
        """获取工具名称列表"""
        return self._tool_groups.get(group, []) if group else list(self._tools.keys())
    
    def list_groups(self) -> List[str]:
        """列出所有工具组"""
        return list(self._tool_groups.keys())
    
    def unregister_tool(self, name: str) -> bool:
        """注销工具"""
        if name in self._tools:
            del self._tools[name]
            for group_tools in self._tool_groups.values():
                if name in group_tools:
                    group_tools.remove(name)
            return True
        return False
    
    def clear(self) -> None:
        """清空所有工具"""
        self._tools.clear()
        self._tool_groups.clear()


tool_registry = ToolRegistry()
