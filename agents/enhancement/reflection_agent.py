"""
反思Agent - 评估和改进Agent的输出
作为增强Agent的一种，继承BaseAgent
"""
from typing import Dict, Any, List
from langchain_core.messages import HumanMessage
from langchain_core.tools import Tool
from agents.base.base_agent import BaseAgent


class ReflectionAgent(BaseAgent):
    """反思Agent - 评估和改进其他Agent的输出"""
    
    def __init__(self, llm, config: Dict[str, Any] = None):
        """
        初始化反思Agent
        
        Args:
            llm: ChatModel实例
            config: Agent配置
        """
        # 反思Agent不需要工具，传入空列表
        super().__init__(
            name="reflection",
            tools=[],  # 反思Agent不使用工具
            llm=llm,
            config=config or {}
        )
        
        self.reflection_prompt_template = """你是一个反思评估助手。请评估以下Agent的输出质量。

用户输入: {user_input}

Agent的初始输出:
{initial_output}

请进行以下评估：
1. 输出是否准确回答了用户的问题？
2. 输出是否完整？
3. 输出是否有错误或不足？
4. 如果需要改进，应该如何改进？

请按照以下格式回答：
评估结果: [你的评估]
是否需要改进: [是/否]
改进建议: [如果需要改进，提供具体建议]"""
        
        self.improvement_prompt_template = """基于以下反思，请改进Agent的输出。

用户输入: {user_input}
初始输出: {initial_output}
反思评估: {reflection_text}

请提供改进后的输出，确保：
1. 更准确地回答用户问题
2. 更完整地提供信息
3. 修正所有错误
4. 保持友好和专业的语气

改进后的输出:"""
    
    def create_agent_executor(self):
        """反思Agent不需要executor，直接使用LLM"""
        # 返回None，因为反思Agent直接使用LLM，不通过create_agent
        return None
    
    def reflect(self, user_input: str, agent_output: str, callbacks: List = None) -> Dict[str, Any]:
        """执行反思评估"""
        prompt = self.reflection_prompt_template.format(
            user_input=user_input,
            initial_output=agent_output
        )
        
        # 使用callbacks记录日志
        if callbacks:
            response = self.llm.invoke([HumanMessage(content=prompt)], config={"callbacks": callbacks})
        else:
            response = self.llm.invoke([HumanMessage(content=prompt)])
        reflection_text = response.content if hasattr(response, 'content') else str(response)
        
        # 解析反思结果
        needs_improvement = self._parse_reflection(reflection_text)
        
        return {
            'reflection': reflection_text,
            'needs_improvement': needs_improvement,
            'original_output': agent_output
        }
    
    def improve(self, user_input: str, original_output: str, reflection_text: str, callbacks: List = None) -> str:
        """基于反思改进输出"""
        prompt = self.improvement_prompt_template.format(
            user_input=user_input,
            initial_output=original_output,
            reflection_text=reflection_text
        )
        
        # 使用callbacks记录日志
        if callbacks:
            response = self.llm.invoke([HumanMessage(content=prompt)], config={"callbacks": callbacks})
        else:
            response = self.llm.invoke([HumanMessage(content=prompt)])
        improved_output = response.content if hasattr(response, 'content') else str(response)
        
        return improved_output
    
    def _parse_reflection(self, reflection_text: str) -> bool:
        """解析反思结果，判断是否需要改进"""
        # 检查"是否需要改进"后面的内容
        if '是否需要改进' in reflection_text:
            idx = reflection_text.find('是否需要改进')
            if idx != -1:
                after_text = reflection_text[idx:idx+50]
                # 检查"是"是否在"否"之前
                if '是' in after_text:
                    yes_idx = after_text.find('是')
                    no_idx = after_text.find('否')
                    if no_idx == -1 or yes_idx < no_idx:
                        return True
        
        # 关键词匹配
        improvement_keywords = ['需要改进', '有错误', '不完整', '不准确', '应该改进', '需要修正']
        for keyword in improvement_keywords:
            if keyword in reflection_text:
                return True
        
        return False

