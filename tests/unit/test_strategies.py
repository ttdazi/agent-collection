"""
测试策略
"""
import unittest
from unittest.mock import MagicMock
from strategies.strategy_manager import StrategyManager
from configs import config

class TestStrategyManager(unittest.TestCase):
    
    def setUp(self):
        self.manager = StrategyManager()
        self.manager.clear()
        
        # Mock Agent
        self.mock_agent = MagicMock()
        self.mock_agent.name = "test_agent"
        self.mock_agent.invoke.return_value = {"output": "直接执行结果"}
        
        # Mock Strategy
        self.mock_strategy = MagicMock()
        self.mock_strategy.is_enabled.return_value = True
        self.mock_strategy.enhance.return_value = {"output": "策略增强结果"}
        
    def test_register_strategy(self):
        """测试策略注册"""
        self.manager.register_strategy("test", self.mock_strategy)
        self.assertIn("test", self.manager.list_strategies())
        
    def test_apply_no_strategy(self):
        """测试无策略应用"""
        # 清空配置
        config.DEFAULT_CONFIG["agents"] = {}
        config.DEFAULT_CONFIG["enhancement"]["strategies"] = []
        
        result = self.manager.apply_strategies(self.mock_agent, {"input": "test"})
        self.assertEqual(result["output"], "直接执行结果")
        
    def test_apply_agent_strategy(self):
        """测试Agent特定策略"""
        self.manager.register_strategy("test", self.mock_strategy)
        
        # 设置Agent特定配置
        config.DEFAULT_CONFIG["agents"] = {
            "test_agent": {"strategies": ["test"]}
        }
        
        result = self.manager.apply_strategies(self.mock_agent, {"input": "test"})
        self.assertEqual(result["output"], "策略增强结果")
        self.mock_strategy.enhance.assert_called_once()

if __name__ == '__main__':
    unittest.main()

