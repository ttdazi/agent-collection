"""
基于LangGraph的反思机制工作流
"""
from typing import Dict, Any, List, Literal
from langgraph.graph import StateGraph, END
from schemas.workflow_schema import ReflectionState
from agents.base_agent import BaseAgent
from agents.reflection_agent import ReflectionAgent


class ReflectionGraph:
    """基于LangGraph的反思机制"""
    
    def __init__(self, agent: BaseAgent, reflection_agent: ReflectionAgent, max_iterations: int = 2):
        self.agent = agent
        self.reflection_agent = reflection_agent
        self.max_iterations = max_iterations
        self.graph = self._create_graph()
    
    def _create_graph(self) -> StateGraph:
        """创建反思工作流图"""
        workflow = StateGraph(ReflectionState)
        
        # 节点1: 执行Agent
        def execute_agent(state: ReflectionState) -> Dict:
            """执行Agent获取初始输出"""
            # 从kwargs中获取callbacks（如果存在）
            callbacks = state.callbacks_handler if state.callbacks_handler else None
            
            # 临时禁用反思机制，避免递归
            # 保存原始配置
            original_config = self.agent.config.copy()
            self.agent.config["enable_reflection"] = False
            
            try:
                if callbacks:
                    result = self.agent.invoke(
                        {"input": state.user_input}, 
                        config={"callbacks": callbacks}
                    )
                else:
                    result = self.agent.invoke({"input": state.user_input})
                output = result.get("output", "")
            finally:
                # 恢复原始配置
                self.agent.config = original_config
            
            return {
                "agent_output": output,
                "improved_output": output,  # 初始时改进输出等于原始输出
                "iteration": 0
            }
        
        # 节点2: 反思评估
        def reflect(state: ReflectionState) -> Dict:
            """对Agent输出进行反思评估"""
            callbacks = state.callbacks_handler if state.callbacks_handler else None
            reflection_result = self.reflection_agent.reflect(
                state.user_input,
                state.improved_output,  # 使用改进后的输出进行反思
                callbacks=callbacks
            )
            
            return {
                "reflection": reflection_result["reflection"],
                "should_continue": reflection_result["needs_improvement"]
            }
        
        # 节点3: 改进输出
        def improve(state: ReflectionState) -> Dict:
            """基于反思改进输出"""
            callbacks = state.callbacks_handler if state.callbacks_handler else None
            if state.should_continue:
                improved = self.reflection_agent.improve(
                    state.user_input,
                    state.improved_output,
                    state.reflection,
                    callbacks=callbacks
                )
                
                return {
                    "improved_output": improved,
                    "iteration": state.iteration + 1
                }
            else:
                # 如果不需要改进，保持原样
                return {
                    "improved_output": state.improved_output
                }
        
        # 节点4: 判断是否继续
        def should_continue(state: ReflectionState) -> Literal["reflect", "end"]:
            """判断是否继续反思循环"""
            # 如果达到最大迭代次数，结束
            if state.iteration >= state.max_iterations:
                return "end"
            
            # 如果不需要改进，结束
            if not state.should_continue:
                return "end"
            
            # 继续反思
            return "reflect"
        
        # 节点5: 生成最终输出
        def finalize(state: ReflectionState) -> Dict:
            """生成最终输出"""
            return {
                "final_output": state.improved_output
            }
        
        # 添加节点
        workflow.add_node("execute", execute_agent)
        workflow.add_node("reflect", reflect)
        workflow.add_node("improve", improve)
        workflow.add_node("finalize", finalize)
        
        # 设置入口点
        workflow.set_entry_point("execute")
        
        # 添加边
        workflow.add_edge("execute", "reflect")
        workflow.add_edge("reflect", "improve")
        workflow.add_conditional_edges(
            "improve",
            should_continue,
            {
                "reflect": "reflect",  # 继续反思
                "end": "finalize"      # 结束并生成最终输出
            }
        )
        workflow.add_edge("finalize", END)
        
        return workflow.compile()
    
    def invoke(self, user_input: str, callbacks: List = None) -> Dict[str, Any]:
        """执行反思工作流"""
        # 创建初始状态，使用Pydantic模型
        initial_state = ReflectionState(
            user_input=user_input,
            max_iterations=self.max_iterations,
            callbacks_handler=callbacks
        )
        
        # 执行工作流
        # StateGraph.invoke接受dict或state对象
        # Pydantic对象可以直接传递给LangGraph，但通常建议转为dict
        final_state_dict = self.graph.invoke(initial_state)
        
        # 将结果转换回ReflectionState对象以便统一处理
        # 注意：LangGraph返回的是dict，包含了所有状态字段
        final_state = ReflectionState(**final_state_dict)
        
        return {
            "output": final_state.final_output or final_state.improved_output,
            "iterations": final_state.iteration,
            "reflection": final_state.reflection,
            "original_output": final_state.agent_output
        }

