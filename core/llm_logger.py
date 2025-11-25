"""
LLM交互日志记录器 - 记录每次ChatModel的询问和回答，包括ReAct循环的每一步
"""
from langchain_core.callbacks import BaseCallbackHandler
from langchain_core.messages import AIMessage, ToolMessage, HumanMessage, SystemMessage
from typing import Any, Dict, List
import sys
import os
from datetime import datetime
from configs import config
import re

class LLMLogger(BaseCallbackHandler):
    """LLM交互日志记录器（支持ChatModel和ReAct循环记录）"""
    
    def __init__(self):
        super().__init__()
        self.call_count = 0
        self._pending_calls = {}  # 跟踪未完成的调用
        self._react_steps = {}  # 跟踪ReAct循环的步骤
        
        # 从配置读取日志设置
        log_config = config.DEFAULT_CONFIG.get("logging", {})
        self.console_output = log_config.get("llm_console_output", False)
        self.log_file = log_config.get("llm_log_file", "logs/llm_interactions.log")
        
        # 确保日志目录存在
        log_dir = os.path.dirname(self.log_file)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir, exist_ok=True)
        
        # 初始化日志文件（追加模式）
        self._write_to_file("="*80)
        self._write_to_file(f"LLM交互日志 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        self._write_to_file("="*80 + "\n")
        
        if self.console_output:
            print("✅ LLMLogger初始化完成（控制台+文件，支持ReAct循环记录）")
        else:
            print("✅ LLMLogger初始化完成（仅保存到文件，支持ReAct循环记录）")
    
    def _write_to_file(self, content: str):
        """写入日志到文件"""
        try:
            with open(self.log_file, 'a', encoding='utf-8') as f:
                f.write(content + '\n')
        except Exception as e:
            print(f"⚠️ 写入日志文件失败: {e}")
    
    def _format_react_step(self, step_type: str, content: str, tool_name: str = None, tool_args: Any = None) -> str:
        """格式化ReAct步骤为易读格式，自动处理换行"""
        # 计算标题长度
        title_length = len(step_type)
        border_length = 78
        
        formatted = f"\n┌─ {step_type} " + "─" * (border_length - title_length - 4) + "┐\n"
        
        if step_type == "💭 思考 (Thought)":
            # 格式化思考内容，自动换行（每行最多76个字符）
            if content:
                lines = content.split('\n')
                for line in lines:
                    if line.strip():
                        # 如果行太长，自动换行
                        max_width = 76
                        if len(line) > max_width:
                            words = line.split()
                            current_line = ""
                            for word in words:
                                if len(current_line) + len(word) + 1 > max_width:
                                    if current_line:
                                        formatted += f"│ {current_line.strip()}\n"
                                    current_line = word + " "
                                else:
                                    current_line += word + " "
                            if current_line:
                                formatted += f"│ {current_line.strip()}\n"
                        else:
                            formatted += f"│ {line.strip()}\n"
            else:
                formatted += "│ (无内容)\n"
        
        elif step_type == "🔧 行动 (Action)":
            formatted += f"│ 工具名称: {tool_name}\n"
            if tool_args:
                # 格式化工具参数
                args_str = str(tool_args)
                if isinstance(tool_args, dict):
                    args_str = ", ".join([f"{k}={v}" for k, v in tool_args.items()])
                
                # 自动换行
                max_width = 76
                if len(args_str) > max_width:
                    words = args_str.split()
                    current_line = "│ 工具参数: "
                    for word in words:
                        if len(current_line) + len(word) + 1 > max_width:
                            formatted += current_line + "\n"
                            current_line = "│            " + word + " "
                        else:
                            current_line += word + " "
                    if current_line.strip() != "│":
                        formatted += current_line + "\n"
                else:
                    formatted += f"│ 工具参数: {args_str}\n"
            else:
                formatted += "│ 工具参数: (无参数)\n"
        
        elif step_type == "👀 观察 (Observation)":
            # 格式化观察内容，自动换行
            if content:
                lines = content.split('\n')
                for line in lines:
                    if line.strip():
                        max_width = 76
                        if len(line) > max_width:
                            words = line.split()
                            current_line = ""
                            for word in words:
                                if len(current_line) + len(word) + 1 > max_width:
                                    if current_line:
                                        formatted += f"│ {current_line.strip()}\n"
                                    current_line = word + " "
                                else:
                                    current_line += word + " "
                            if current_line:
                                formatted += f"│ {current_line.strip()}\n"
                        else:
                            formatted += f"│ {line.strip()}\n"
            else:
                formatted += "│ (无内容)\n"
        
        elif step_type == "✅ 最终答案 (Final Answer)":
            # 格式化最终答案，自动换行
            if content:
                lines = content.split('\n')
                for line in lines:
                    if line.strip():
                        max_width = 76
                        if len(line) > max_width:
                            words = line.split()
                            current_line = ""
                            for word in words:
                                if len(current_line) + len(word) + 1 > max_width:
                                    if current_line:
                                        formatted += f"│ {current_line.strip()}\n"
                                    current_line = word + " "
                                else:
                                    current_line += word + " "
                            if current_line:
                                formatted += f"│ {current_line.strip()}\n"
                        else:
                            formatted += f"│ {line.strip()}\n"
            else:
                formatted += "│ (无内容)\n"
        
        formatted += "└" + "─" * border_length + "┘\n"
        return formatted
    
    def _parse_react_content(self, content: str) -> Dict[str, Any]:
        """解析LLM返回的内容，提取ReAct格式的步骤"""
        result = {
            'thoughts': [],
            'actions': [],
            'observations': [],
            'final_answer': None
        }
        
        if not content:
            return result
        
        # 提取思考（支持中英文）
        thought_patterns = [
            r'思考[：:]\s*(.+?)(?=\n(?:行动|观察|最终答案|Final Answer|Action|Observation|Thought|$))',
            r'Thought[：:]\s*(.+?)(?=\n(?:行动|观察|最终答案|Final Answer|Action|Observation|Thought|$))'
        ]
        for pattern in thought_patterns:
            thoughts = re.findall(pattern, content, re.DOTALL | re.IGNORECASE)
            result['thoughts'].extend([t.strip() for t in thoughts if t.strip()])
        
        # 提取行动
        action_patterns = [
            r'行动[：:]\s*(.+?)(?=\n(?:行动输入|观察|思考|最终答案|Final Answer|Action Input|Observation|Thought|$))',
            r'Action[：:]\s*(.+?)(?=\n(?:行动输入|观察|思考|最终答案|Final Answer|Action Input|Observation|Thought|$))'
        ]
        for pattern in action_patterns:
            actions = re.findall(pattern, content, re.DOTALL | re.IGNORECASE)
            result['actions'].extend([a.strip() for a in actions if a.strip()])
        
        # 提取最终答案（支持中英文）
        final_answer_patterns = [
            r'最终答案[：:]\s*(.+?)(?:\n\n|\n思考:|\nThought:|$)',
            r'Final Answer[：:]\s*(.+?)(?:\n\n|\n思考:|\nThought:|$)'
        ]
        for pattern in final_answer_patterns:
            final_match = re.search(pattern, content, re.DOTALL | re.IGNORECASE)
            if final_match:
                result['final_answer'] = final_match.group(1).strip()
                break
        
        return result
    
    def on_chat_model_start(self, serialized: Dict[str, Any], messages: List, **kwargs: Any) -> None:
        """ChatModel开始调用时触发（新API）"""
        self.call_count += 1
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # 调试：记录回调被触发
        self._write_to_file(f"\n[DEBUG] on_chat_model_start 被触发 - {timestamp}")
        self._write_to_file(f"[DEBUG] call_count: {self.call_count}")
        
        # 记录调用ID用于匹配
        run_id = kwargs.get("run_id", f"run_{self.call_count}")
        self._pending_calls[run_id] = {
            "start_time": timestamp, 
            "call_count": self.call_count,
            "messages": messages
        }
        
        # 初始化ReAct步骤记录
        if run_id not in self._react_steps:
            self._react_steps[run_id] = []
        
        # 提取模型信息
        model_name = "unknown"
        if isinstance(serialized, dict):
            model_name = serialized.get("name", serialized.get("id", "unknown"))
        if model_name == "unknown":
            if "model_name" in kwargs:
                model_name = kwargs["model_name"]
            elif "model" in kwargs:
                model_name = kwargs["model"]
            elif "invocation_params" in kwargs:
                inv_params = kwargs["invocation_params"]
                if isinstance(inv_params, dict):
                    model_name = inv_params.get("model", inv_params.get("model_name", "unknown"))
        if model_name == "unknown" and "llm" in kwargs:
            llm = kwargs["llm"]
            if hasattr(llm, "model_name"):
                model_name = llm.model_name
            elif hasattr(llm, "model"):
                model_name = llm.model
            elif hasattr(llm, "_default_params") and isinstance(llm._default_params, dict):
                model_name = llm._default_params.get("model", "unknown")
        
        # 分析messages，提取ReAct步骤
        react_log = []
        for msg in messages:
            if isinstance(msg, AIMessage):
                # 提取思考过程和最终答案
                if hasattr(msg, 'content') and msg.content:
                    content_str = str(msg.content)
                    parsed = self._parse_react_content(content_str)
                    if parsed['thoughts']:
                        for thought in parsed['thoughts']:
                            react_log.append({
                                'type': 'thought',
                                'content': thought
                            })
                    if parsed['final_answer']:
                        react_log.append({
                            'type': 'final_answer',
                            'content': parsed['final_answer']
                        })
                
                # 提取工具调用（行动）
                if hasattr(msg, 'tool_calls') and msg.tool_calls:
                    for tool_call in msg.tool_calls:
                        tool_name = tool_call.get('name', 'unknown')
                        tool_args = tool_call.get('args', {})
                        react_log.append({
                            'type': 'action',
                            'tool_name': tool_name,
                            'tool_args': tool_args
                        })
            
            elif isinstance(msg, ToolMessage):
                # 工具返回结果（观察）
                tool_content = msg.content if hasattr(msg, 'content') else str(msg)
                react_log.append({
                    'type': 'observation',
                    'content': tool_content
                })
        
        # 记录ReAct步骤
        if react_log:
            self._react_steps[run_id].extend(react_log)
        
        # 格式化messages用于显示
        prompt = "\n".join([str(msg) for msg in messages])
        
        # 控制台显示（如果启用）
        if self.console_output:
            print(f"\n🤖 ChatModel调用 #{self.call_count} - {timestamp}")
            print(f"📦 模型: {model_name}")
            print(f"📤 Messages数量: {len(messages)}")
            sys.stdout.flush()
        
        # 文件保存
        self._write_to_file("\n" + "="*80)
        self._write_to_file(f"🤖 ChatModel调用 #{self.call_count} - {timestamp}")
        self._write_to_file("="*80)
        self._write_to_file(f"\n📦 使用的模型: {model_name}")
        if "llm" in kwargs:
            llm = kwargs["llm"]
            if hasattr(llm, "model"):
                self._write_to_file(f"📦 模型名称: {llm.model}")
            elif hasattr(llm, "model_name"):
                self._write_to_file(f"📦 模型名称: {llm.model_name}")
        
        # 记录ReAct循环步骤
        if react_log:
            self._write_to_file("\n" + "="*80)
            self._write_to_file("🔄 ReAct循环步骤:")
            self._write_to_file("="*80)
            
            for step in react_log:
                if step['type'] == 'thought':
                    self._write_to_file(self._format_react_step(
                        "💭 思考 (Thought)",
                        step['content']
                    ))
                elif step['type'] == 'action':
                    self._write_to_file(self._format_react_step(
                        "🔧 行动 (Action)",
                        "",
                        tool_name=step['tool_name'],
                        tool_args=step['tool_args']
                    ))
                elif step['type'] == 'observation':
                    self._write_to_file(self._format_react_step(
                        "👀 观察 (Observation)",
                        step['content']
                    ))
                elif step['type'] == 'final_answer':
                    self._write_to_file(self._format_react_step(
                        "✅ 最终答案 (Final Answer)",
                        step['content']
                    ))
        
        # 记录原始messages（用于调试）
        self._write_to_file("\n📤 发送给ChatModel的Messages:")
        self._write_to_file(f"数量: {len(messages)}")
        self._write_to_file(f"总长度: {len(prompt)} 字符")
        self._write_to_file("-"*80)
        
        # 格式化messages，每个message一行，自动换行
        for i, msg in enumerate(messages):
            msg_type = type(msg).__name__
            if isinstance(msg, SystemMessage):
                content = msg.content if hasattr(msg, 'content') else str(msg)
                self._write_to_file(f"\n[{i+1}] SystemMessage:")
                for line in content.split('\n'):
                    if line.strip():
                        self._write_to_file(f"    {line}")
            elif isinstance(msg, HumanMessage):
                content = msg.content if hasattr(msg, 'content') else str(msg)
                self._write_to_file(f"\n[{i+1}] HumanMessage:")
                for line in content.split('\n'):
                    if line.strip():
                        self._write_to_file(f"    {line}")
            elif isinstance(msg, AIMessage):
                content = msg.content if hasattr(msg, 'content') else str(msg)
                self._write_to_file(f"\n[{i+1}] AIMessage:")
                if content:
                    for line in content.split('\n'):
                        if line.strip():
                            self._write_to_file(f"    {line}")
                # 记录工具调用
                if hasattr(msg, 'tool_calls') and msg.tool_calls:
                    self._write_to_file(f"    工具调用: {len(msg.tool_calls)} 个")
                    for tc in msg.tool_calls:
                        self._write_to_file(f"      - {tc.get('name', 'unknown')}({tc.get('args', {})})")
            elif isinstance(msg, ToolMessage):
                content = msg.content if hasattr(msg, 'content') else str(msg)
                tool_name = msg.name if hasattr(msg, 'name') else 'unknown'
                self._write_to_file(f"\n[{i+1}] ToolMessage ({tool_name}):")
                for line in content.split('\n'):
                    if line.strip():
                        self._write_to_file(f"    {line}")
        
        self._write_to_file("-"*80)
    
    def on_chat_model_end(self, response, **kwargs: Any) -> None:
        """ChatModel调用结束时触发（新API）"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        run_id = kwargs.get("run_id", None)
        
        # 调试：记录回调被触发
        self._write_to_file(f"\n[DEBUG] on_chat_model_end 被触发 - {timestamp}")
        self._write_to_file(f"[DEBUG] run_id: {run_id}")
        self._write_to_file(f"[DEBUG] response类型: {type(response)}")
        if hasattr(response, '__dict__'):
            self._write_to_file(f"[DEBUG] response属性: {list(response.__dict__.keys())[:10]}")
        
        # 提取响应文本
        text = None
        response_str = None
        
        # 方法1: 检查是否是AIMessage类型（LangChain新API）
        if hasattr(response, 'content'):
            text = response.content
            self._write_to_file(f"[DEBUG] 从response.content提取文本: {len(str(text))} 字符")
        elif hasattr(response, 'text'):
            text = response.text
            self._write_to_file(f"[DEBUG] 从response.text提取文本: {len(str(text))} 字符")
        
        # 方法2: 检查是否有generations属性
        if not text and hasattr(response, 'generations') and response.generations:
            for gen_list in response.generations:
                for gen in gen_list:
                    if hasattr(gen, 'message') and hasattr(gen.message, 'content'):
                        text = gen.message.content
                        break
                    elif hasattr(gen, 'text'):
                        text = gen.text
                        break
                if text:
                    break
        
        # 方法3: 检查是否是字典类型
        if not text and isinstance(response, dict):
            if 'content' in response:
                text = response['content']
            elif 'text' in response:
                text = response['text']
            elif 'generations' in response:
                for gen_list in response['generations']:
                    for gen in gen_list:
                        if isinstance(gen, dict):
                            if 'message' in gen and 'content' in gen['message']:
                                text = gen['message']['content']
                                break
                            elif 'text' in gen:
                                text = gen['text']
                                break
                        elif hasattr(gen, 'message') and hasattr(gen.message, 'content'):
                            text = gen.message.content
                            break
                    if text:
                        break
        
        # 方法4: 如果还是没找到，尝试从字符串表示中提取
        if not text:
            response_str = str(response)
            # 尝试从字符串中提取content
            if 'content=' in response_str:
                import re
                match = re.search(r"content=['\"](.+?)['\"]", response_str)
                if match:
                    text = match.group(1)
        
        # 记录响应
        self._log_response(timestamp, text, response, response_str, run_id)
    
    def _log_response(self, timestamp: str, text: str, response: Any, response_str: str = None, run_id: str = None) -> None:
        """记录响应的通用方法，包括ReAct格式解析"""
        # 控制台显示（如果启用）
        if self.console_output:
            if text:
                print(f"📥 响应长度: {len(text)} 字符")
                if len(text) > 200:
                    print(f"   预览: {text[:200]}...")
                else:
                    print(f"   {text}")
            print("="*80 + "\n")
            sys.stdout.flush()
        
        # 文件保存
        self._write_to_file(f"\n📥 LLM返回的响应:")
        self._write_to_file(f"时间: {timestamp}")
        if text:
            self._write_to_file(f"长度: {len(text)} 字符")
            self._write_to_file("-"*80)
            
            # 解析并格式化ReAct内容
            parsed = self._parse_react_content(text)
            
            if parsed['thoughts'] or parsed['actions'] or parsed['final_answer']:
                self._write_to_file("\n🔄 解析的ReAct步骤:")
                self._write_to_file("-"*80)
                
                for thought in parsed['thoughts']:
                    self._write_to_file(self._format_react_step(
                        "💭 思考 (Thought)",
                        thought
                    ))
                
                for action in parsed['actions']:
                    # 尝试从action文本中提取工具名称
                    # 这里简化处理，实际可能需要更复杂的解析
                    self._write_to_file(self._format_react_step(
                        "🔧 行动 (Action)",
                        action
                    ))
                
                if parsed['final_answer']:
                    self._write_to_file(self._format_react_step(
                        "✅ 最终答案 (Final Answer)",
                        parsed['final_answer']
                    ))
            else:
                # 如果没有ReAct格式，直接显示原始内容（自动换行）
                for line in text.split('\n'):
                    if line.strip():
                        self._write_to_file(line)
            
            self._write_to_file("-"*80)
        else:
            self._write_to_file("-"*80)
            self._write_to_file("⚠️ 无法提取文本内容，以下是完整响应对象:")
            self._write_to_file("-"*80)
            if response_str:
                self._write_to_file(response_str)
            else:
                self._write_to_file(str(response))
            self._write_to_file("-"*80)
        
        self._write_to_file("="*80 + "\n")
    
    def on_llm_end(self, response, **kwargs: Any) -> None:
        """LLM调用结束时触发（兼容旧API）"""
        # 转发到 on_chat_model_end
        self.on_chat_model_end(response, **kwargs)
    
    def on_llm_start(self, serialized: Dict[str, Any], prompts: List[str], **kwargs: Any) -> None:
        """LLM调用开始时触发（兼容旧API）"""
        # 转换为 messages 格式
        from langchain_core.messages import HumanMessage
        messages = [HumanMessage(content=prompt) for prompt in prompts]
        self.on_chat_model_start(serialized, messages, **kwargs)
    
    def on_llm_error(self, error: Exception, **kwargs: Any) -> None:
        """LLM调用出错时触发（兼容旧API）"""
        self.on_chat_model_error(error, **kwargs)
    
    def on_tool_start(self, serialized: Dict[str, Any], input_str: str, **kwargs: Any) -> None:
        """工具开始执行时触发"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        tool_name = serialized.get("name", "unknown") if isinstance(serialized, dict) else "unknown"
        
        self._write_to_file(f"\n[工具执行] {tool_name} - {timestamp}")
        self._write_to_file(f"输入: {input_str}")
    
    def on_tool_end(self, output: str, **kwargs: Any) -> None:
        """工具执行结束时触发"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self._write_to_file(f"输出: {output}")
        self._write_to_file(f"[工具执行结束] - {timestamp}\n")
    
    def on_tool_error(self, error: Exception, **kwargs: Any) -> None:
        """工具执行出错时触发"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self._write_to_file(f"\n[工具执行错误] - {timestamp}")
        self._write_to_file(f"错误: {str(error)}\n")
    
    def on_agent_action(self, action, **kwargs: Any) -> None:
        """Agent执行行动时触发"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        tool_name = action.tool if hasattr(action, 'tool') else action.get('tool', 'unknown')
        tool_input = action.tool_input if hasattr(action, 'tool_input') else action.get('tool_input', '')
        
        self._write_to_file(self._format_react_step(
            "🔧 行动 (Action)",
            "",
            tool_name=tool_name,
            tool_args=tool_input
        ))
    
    def on_agent_finish(self, finish, **kwargs: Any) -> None:
        """Agent完成时触发"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        output = finish.return_values if hasattr(finish, 'return_values') else finish.get('return_values', {})
        output_text = output.get('output', '') if isinstance(output, dict) else str(output)
        
        if output_text:
            self._write_to_file(self._format_react_step(
                "✅ 最终答案 (Final Answer)",
                output_text
            ))
    
    def on_chat_model_error(self, error: Exception, **kwargs: Any) -> None:
        """ChatModel调用出错时触发"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        error_msg = str(error)
        
        # 控制台显示（如果启用）：简要错误信息
        if self.console_output:
            print(f"\n❌ LLM调用 #{self.call_count} 出错 - {timestamp}")
            print(f"   错误: {error_msg[:200]}...")
            print("   (完整错误信息已保存到文件)")
            print("="*80 + "\n")
            sys.stdout.flush()
        
        # 文件保存：完整错误信息
        self._write_to_file("\n" + "="*80)
        self._write_to_file(f"❌ LLM调用出错 (#{self.call_count}) - {timestamp}")
        self._write_to_file("-"*80)
        self._write_to_file(error_msg)
        self._write_to_file("="*80 + "\n")

