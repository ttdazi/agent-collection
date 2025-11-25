"""
Agent基类 - 定义Agent的通用接口
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, List
from langchain_core.tools import BaseTool


class BaseAgent(ABC):
    """Agent基类"""
    
    def __init__(self, name: str, tools: List[BaseTool], llm, config: Dict[str, Any] = None):
        """
        初始化Agent
        
        Args:
            name: Agent名称
            tools: 工具列表
            llm: ChatModel实例
            config: Agent配置
        """
        self.name = name
        self.tools = tools
        self.llm = llm
        self.config = config or {}
        self._agent_executor = None
    
    @abstractmethod
    def create_agent_executor(self):
        """创建Agent执行器（返回create_agent创建的agent）"""
        pass
    
    def get_agent_executor(self):
        """获取Agent执行器（懒加载）"""
        if self._agent_executor is None:
            self._agent_executor = self.create_agent_executor()
        return self._agent_executor
    
    def invoke(self, input_data: Dict[str, Any], **kwargs) -> Any:
        """调用Agent（核心执行逻辑）"""
        executor = self.get_agent_executor()
        if "input" in input_data:
            from langchain_core.messages import HumanMessage
            messages = [HumanMessage(content=input_data["input"])]
            
            # 确保callbacks正确传递
            # LangChain的invoke方法需要config参数包含callbacks
            invoke_config = {}
            if "config" in kwargs:
                invoke_config = kwargs["config"].copy() if isinstance(kwargs["config"], dict) else {}
            
            # 确保callbacks在config中
            if "callbacks" not in invoke_config and "callbacks" in kwargs:
                invoke_config["callbacks"] = kwargs["callbacks"]
            
            # 设置recursion_limit以确保工具调用能够完成
            if invoke_config:
                if "recursion_limit" not in invoke_config:
                    invoke_config["recursion_limit"] = 20
            else:
                invoke_config = {"recursion_limit": 20}
            
            result = executor.invoke({"messages": messages}, config=invoke_config)
            
            # 提取最后一条消息的内容
            output_text = None
            if "messages" in result and result["messages"]:
                # 查找最后一条AIMessage（没有tool_calls的，表示最终答案）
                messages_list = result["messages"]
                last_ai_message = None
                
                # 从后往前查找最后一条AIMessage
                for msg in reversed(messages_list):
                    from langchain_core.messages import AIMessage
                    if isinstance(msg, AIMessage):
                        # 如果这条AIMessage没有tool_calls，说明是最终答案
                        if not (hasattr(msg, 'tool_calls') and msg.tool_calls):
                            last_ai_message = msg
                            break
                        # 如果有tool_calls，继续查找下一条
                
                # 如果没找到没有tool_calls的AIMessage，使用最后一条AIMessage
                if last_ai_message is None:
                    for msg in reversed(messages_list):
                        from langchain_core.messages import AIMessage
                        if isinstance(msg, AIMessage):
                            last_ai_message = msg
                            break
                
                # 如果还是没找到，使用最后一条消息
                if last_ai_message is None:
                    last_ai_message = messages_list[-1]
                
                if hasattr(last_ai_message, "content"):
                    output_text = last_ai_message.content
                elif hasattr(last_ai_message, "text"):
                    output_text = last_ai_message.text
            
            # 如果输出是ReAct格式，提取最终答案
            if output_text:
                output_text = self._extract_final_answer(output_text)
            
            if output_text:
                return {"output": output_text}
            return result
        else:
            return executor.invoke(input_data, **kwargs)
    
    def _extract_final_answer(self, text: str) -> str:
        """从ReAct格式输出中提取最终答案"""
        if not text:
            return text
        
        # 查找"最终答案:"或"Final Answer:"后面的内容
        import re
        
        # 尝试匹配中文"最终答案:"
        pattern_zh = r'最终答案[：:]\s*(.+?)(?:\n\n|\n思考:|$)'
        match_zh = re.search(pattern_zh, text, re.DOTALL | re.IGNORECASE)
        if match_zh:
            answer = match_zh.group(1).strip()
            # 如果答案很长，可能包含多行，取第一段
            if '\n' in answer:
                answer = answer.split('\n')[0].strip()
            return answer
        
        # 尝试匹配英文"Final Answer:"
        pattern_en = r'Final Answer[：:]\s*(.+?)(?:\n\n|\nThought:|$)'
        match_en = re.search(pattern_en, text, re.DOTALL | re.IGNORECASE)
        if match_en:
            answer = match_en.group(1).strip()
            if '\n' in answer:
                answer = answer.split('\n')[0].strip()
            return answer
        
        # 如果没有找到"最终答案"，检查是否整个输出就是一个简单的回答
        # 如果输出很短且不包含"思考"、"行动"等关键词，可能是直接答案
        if len(text) < 200 and not any(keyword in text for keyword in ['思考:', '行动:', '观察:', 'Thought:', 'Action:', 'Observation:']):
            return text.strip()
        
        # 如果找不到最终答案，返回原始文本（至少能看到完整输出）
        return text
    
    def get_description(self) -> str:
        """获取Agent描述"""
        return self.config.get("description", f"Agent: {self.name}")

