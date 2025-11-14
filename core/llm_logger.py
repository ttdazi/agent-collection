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
        
        # 格式化messages
        prompt = "\n".join([str(msg) for msg in messages])
        
        # 控制台显示（如果启用）
        if self.console_output:
            print(f"\n🤖 ChatModel调用 #{self.call_count} - {timestamp}")
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
        self._write_to_file(f"\n📤 发送给ChatModel的Messages:")
        self._write_to_file(f"数量: {len(messages)}")
        self._write_to_file(f"总长度: {len(prompt)} 字符")
        self._write_to_file("-"*80)
        self._write_to_file(prompt)
        self._write_to_file("-"*80)
    
    def on_chat_model_end(self, response, **kwargs: Any) -> None:
        """ChatModel调用结束时触发（新API）"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # 提取响应文本
        text = None
        if hasattr(response, 'generations') and response.generations:
            for gen_list in response.generations:
                for gen in gen_list:
                    if hasattr(gen, 'message') and hasattr(gen.message, 'content'):
                        text = gen.message.content
                        break
                if text:
                    break
        elif hasattr(response, 'content'):
            text = response.content
        
        self._log_response(timestamp, text, response)
    
    def _log_response(self, timestamp: str, text: str, response: Any) -> None:
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
            print("="*80 + "\n")
            sys.stdout.flush()
        
        # 文件保存
        self._write_to_file(f"\n📥 LLM返回的响应:")
        self._write_to_file(f"时间: {timestamp}")
        if text:
            self._write_to_file(f"长度: {len(text)} 字符")
            self._write_to_file("-"*80)
            self._write_to_file(text)
        else:
            self._write_to_file("-"*80)
            self._write_to_file(str(response))
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

