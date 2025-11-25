"""
测试工作流
"""
import unittest
from unittest.mock import MagicMock, patch
from graphs.reflection_graph import ReflectionGraph
from schemas.workflow_schema import ReflectionState

class TestReflectionGraph(unittest.TestCase):
    
    def setUp(self):
        # Mock Agent
        self.mock_agent = MagicMock()
        self.mock_agent.config = {}
        self.mock_agent.invoke.return_value = {"output": "初始回答"}
        
        # Mock ReflectionAgent
        self.mock_reflection_agent = MagicMock()
        self.mock_reflection_agent.reflect.return_value = {
            "reflection": "需要改进",
            "needs_improvement": True
        }
        self.mock_reflection_agent.improve.return_value = "改进后的回答"
        
    def test_initialization(self):
        """测试初始化"""
        graph = ReflectionGraph(self.mock_agent, self.mock_reflection_agent)
        self.assertIsNotNone(graph.graph)
        self.assertEqual(graph.max_iterations, 2)
        
    def test_invoke(self):
        """测试调用"""
        # 由于LangGraph编译后的图形难以直接mock执行，这里主要测试结构构建
        # 实际执行测试需要更复杂的设置或集成测试
        graph = ReflectionGraph(self.mock_agent, self.mock_reflection_agent)
        
        # 验证StateGraph构建逻辑
        # 这里我们假设_create_graph方法成功返回了编译后的图
        self.assertIsNotNone(graph.graph)

if __name__ == '__main__':
    unittest.main()

