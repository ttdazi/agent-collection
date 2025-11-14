"""
LLM交互日志记录器 - 记录每次ChatModel的询问和回答
"""
from langchain_core.callbacks import BaseCallbackHandler
from typing import Any, Dict, List
import sys
import os
from datetime import datetime
import config

class LLMLogger(BaseCallbackHandler):
    """LLM交互日志记录器（支持ChatModel）"""
    
    def __init__(self):
        super().__init__()
        self.call_count = 0
        self._pending_calls = {}  # 跟踪未完成的调用
        
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
            print("✅ LLMLogger初始化完成（控制台+文件）")
        else:
            print("✅ LLMLogger初始化完成（仅保存到文件）")
    
    def _write_to_file(self, content: str):
        """写入日志到文件"""
        try:
            with open(self.log_file, 'a', encoding='utf-8') as f:
                f.write(content + '\n')
        except Exception as e:
            print(f"⚠️ 写入日志文件失败: {e}")
    
    def on_chat_model_start(self, serialized: Dict[str, Any], messages: List, **kwargs: Any) -> None:
        """ChatModel开始调用时触发（新API）"""
        self.call_count += 1
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # 记录调用ID用于匹配
        run_id = kwargs.get("run_id", f"run_{self.call_count}")
        self._pending_calls[run_id] = {"start_time": timestamp, "call_count": self.call_count}
        
        # 提取模型信息 - 尝试多种方式
        model_name = "unknown"
        # 方法1: 从serialized中获取
        if isinstance(serialized, dict):
            model_name = serialized.get("name", serialized.get("id", "unknown"))
        # 方法2: 从kwargs中获取
        if model_name == "unknown":
            if "model_name" in kwargs:
                model_name = kwargs["model_name"]
            elif "model" in kwargs:
                model_name = kwargs["model"]
            elif "invocation_params" in kwargs:
                inv_params = kwargs["invocation_params"]
                if isinstance(inv_params, dict):
                    model_name = inv_params.get("model", inv_params.get("model_name", "unknown"))
        # 方法3: 从LLM对象中获取（如果可用）
        if model_name == "unknown" and "llm" in kwargs:
            llm = kwargs["llm"]
            if hasattr(llm, "model_name"):
                model_name = llm.model_name
            elif hasattr(llm, "model"):
                model_name = llm.model
            elif hasattr(llm, "_default_params") and isinstance(llm._default_params, dict):
                model_name = llm._default_params.get("model", "unknown")
        
        # 格式化messages
        prompt = "\n".join([str(msg) for msg in messages])
        
        # 控制台显示（如果启用）
        if self.console_output:
            print(f"\n🤖 ChatModel调用 #{self.call_count} - {timestamp}")
            print(f"📦 模型: {model_name}")
            print(f"📤 Messages数量: {len(messages)}")
            print(f"📤 总长度: {len(prompt)} 字符")
            if len(prompt) > 500:
                print(f"   (完整内容已保存到文件)")
            else:
                print(f"   {prompt[:200]}...")
            sys.stdout.flush()
        
        # 文件保存
        self._write_to_file("\n" + "="*80)
        self._write_to_file(f"🤖 ChatModel调用 #{self.call_count} - {timestamp}")
        self._write_to_file("="*80)
        self._write_to_file(f"\n📦 使用的模型: {model_name}")
        # 尝试从LLM对象获取更详细的模型信息
        if "llm" in kwargs:
            llm = kwargs["llm"]
            if hasattr(llm, "model"):
                self._write_to_file(f"📦 模型名称: {llm.model}")
            elif hasattr(llm, "model_name"):
                self._write_to_file(f"📦 模型名称: {llm.model_name}")
        self._write_to_file(f"\n📤 发送给ChatModel的Messages:")
        self._write_to_file(f"数量: {len(messages)}")
        self._write_to_file(f"总长度: {len(prompt)} 字符")
        self._write_to_file("-"*80)
        self._write_to_file(prompt)
        self._write_to_file("-"*80)
    
    def on_chat_model_end(self, response, **kwargs: Any) -> None:
        """ChatModel调用结束时触发（新API）"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # 获取run_id用于匹配
        run_id = kwargs.get("run_id", None)
        
        # 调试：记录回调被触发
        self._write_to_file(f"\n[DEBUG] on_chat_model_end 被触发 - {timestamp}")
        self._write_to_file(f"[DEBUG] run_id: {run_id}")
        self._write_to_file(f"[DEBUG] response类型: {type(response)}")
        if hasattr(response, '__dict__'):
            self._write_to_file(f"[DEBUG] response属性: {list(response.__dict__.keys())}")
        
        # 提取响应文本 - 尝试多种方式
        text = None
        response_str = None
        
        # 方法1: 检查是否有generations属性
        if hasattr(response, 'generations') and response.generations:
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
        
        # 方法2: 检查是否有content属性
        if not text and hasattr(response, 'content'):
            text = response.content
        
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
        
        # 方法4: 如果还是没找到，保存完整响应用于调试
        if not text:
            response_str = str(response)
            # 尝试从字符串中提取内容
            if 'content' in response_str.lower():
                # 简单尝试提取，但主要保存完整响应
                pass
        
        # 调试：记录提取结果
        self._write_to_file(f"[DEBUG] 提取的文本: {text[:100] if text else 'None'}...")
        self._write_to_file(f"[DEBUG] kwargs keys: {list(kwargs.keys())}")
        
        self._log_response(timestamp, text, response, response_str)
    
    def _log_response(self, timestamp: str, text: str, response: Any, response_str: str = None) -> None:
        """记录响应的通用方法"""
        # 控制台显示（如果启用）
        if self.console_output:
            if text:
                print(f"📥 响应长度: {len(text)} 字符")
                if len(text) > 200:
                    print(f"   预览: {text[:200]}...")
                    print(f"   (完整内容已保存到文件)")
                else:
                    print(f"   {text}")
            else:
                print(f"📥 响应: {str(response)[:200]}...")
                print(f"   ⚠️ 无法提取文本内容，完整响应已保存到文件")
            print("="*80 + "\n")
            sys.stdout.flush()
        
        # 文件保存
        self._write_to_file(f"\n📥 LLM返回的响应:")
        self._write_to_file(f"时间: {timestamp}")
        if text:
            self._write_to_file(f"长度: {len(text)} 字符")
            self._write_to_file("-"*80)
            self._write_to_file(text)
            self._write_to_file("-"*80)
        else:
            self._write_to_file("-"*80)
            self._write_to_file("⚠️ 无法提取文本内容，以下是完整响应对象:")
            self._write_to_file("-"*80)
            # 保存完整响应用于调试
            if response_str:
                self._write_to_file(response_str)
            else:
                self._write_to_file(str(response))
            # 尝试打印响应类型和属性
            self._write_to_file(f"\n响应类型: {type(response)}")
            if hasattr(response, '__dict__'):
                self._write_to_file(f"响应属性: {list(response.__dict__.keys())}")
            self._write_to_file("-"*80)
        self._write_to_file("="*80 + "\n")
    
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

