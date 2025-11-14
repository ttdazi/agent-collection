"""
笑话相关工具 - 可以轻松添加新工具
"""
from langchain.tools import Tool
from core.tool_registry import tool_registry
import random

# 笑话数据库
JOKES_DB = [
    "为什么程序员总是分不清万圣节和圣诞节？因为 Oct 31 == Dec 25！",
    "一个SQL查询走进酒吧，看到两个表，然后说：我可以加入你们吗？",
    "为什么Python不用花括号？因为它想保持简洁！",
    "为什么程序员喜欢用暗色主题？因为bug也喜欢暗色！",
    "程序员最讨厌的事情是什么？没有注释的代码，还有有注释的代码！",
    "为什么程序员总是分不清白天和黑夜？因为他们一直在debug！",
    "一个变量走进酒吧，酒保说：抱歉，我们不服务未初始化的变量。",
    "为什么程序员不喜欢自然？因为那里有太多bug！",
]

def get_random_joke(query: str = "") -> str:
    """获取随机笑话"""
    return random.choice(JOKES_DB)

def search_joke_by_keyword(keyword: str) -> str:
    """根据关键词搜索笑话"""
    keyword_lower = keyword.lower()
    matching_jokes = [
        joke for joke in JOKES_DB 
        if keyword_lower in joke.lower()
    ]
    if matching_jokes:
        return random.choice(matching_jokes)
    return f"抱歉，没找到包含'{keyword}'的笑话"

def get_joke_tools():
    """获取所有笑话相关工具"""
    tools = [
        Tool(
            name="GetRandomJoke",
            func=get_random_joke,
            description=(
                "获取一个随机笑话。当用户要求讲笑话时使用此工具。\n"
                "使用格式：\n"
                "Action: GetRandomJoke\n"
                "Action Input: joke\n"
                "注意：Action Input可以是任意字符串，如'joke'、'ok'等。"
            )
        ),
        Tool(
            name="SearchJoke",
            func=search_joke_by_keyword,
            description=(
                "根据关键词搜索笑话。当用户指定了特定主题时使用此工具。\n"
                "使用格式：\n"
                "Action: SearchJoke\n"
                "Action Input: [关键词]\n"
                "示例：Action Input: 程序员\n"
                "注意：Action Input应该是单个关键词，如'程序员'、'Python'、'bug'等。"
            )
        ),
    ]
    # 自动注册到工具注册表
    tool_registry.register_tools(tools, group="joke")
    return tools

