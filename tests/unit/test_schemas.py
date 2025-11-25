"""
测试Schemas
"""
import unittest
from schemas.agent_schema import AgentState, AgentResponse
from schemas.workflow_schema import ReflectionState
from schemas.config_schema import AppConfig, ModelConfig

class TestSchemas(unittest.TestCase):
    
    def test_agent_state(self):
        """测试Agent状态模型"""
        state = AgentState(name="test", input="hello")
        self.assertEqual(state.name, "test")
        self.assertEqual(state.input, "hello")
        self.assertIsNone(state.output)
        
        # 测试无效数据
        with self.assertRaises(ValueError):
            AgentState(name="test")  # 缺少input
            
    def test_reflection_state(self):
        """测试反思状态模型"""
        state = ReflectionState(user_input="hello")
        self.assertEqual(state.user_input, "hello")
        self.assertEqual(state.iteration, 0)
        self.assertEqual(state.max_iterations, 2)
        
        # 测试状态更新
        state.iteration += 1
        self.assertEqual(state.iteration, 1)
        
    def test_app_config(self):
        """测试应用配置模型"""
        config_data = {
            "model_type": "ollama",
            "ollama": {"model": "llama2"},
            "gemini": {"model": "gemini-pro"},
            "deepseek": {"model": "deepseek-chat"},
            "agents": {
                "joke": {"strategies": []},
                "code": {"strategies": ["reflection"]}
            }
        }
        config = AppConfig(**config_data)
        self.assertEqual(config.model_type, "ollama")
        self.assertEqual(config.ollama.model, "llama2")
        self.assertEqual(len(config.agents), 2)
        self.assertIn("reflection", config.agents["code"].strategies)

if __name__ == '__main__':
    unittest.main()

