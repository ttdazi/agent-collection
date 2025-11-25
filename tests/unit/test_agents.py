"""
测试Agent
"""
import unittest
from unittest.mock import MagicMock
from agents.joke_agent import JokeAgent
from langchain_core.messages import AIMessage

class TestAgents(unittest.TestCase):
    
    def setUp(self):
        self.mock_llm = MagicMock()
        self.mock_tools = []
        
    def test_joke_agent_init(self):
        """测试JokeAgent初始化"""
        agent = JokeAgent("joke", self.mock_tools, self.mock_llm)
        self.assertEqual(agent.name, "joke")
        
    def test_agent_description(self):
        """测试Agent描述"""
        config = {"description": "测试描述"}
        agent = JokeAgent("joke", self.mock_tools, self.mock_llm, config)
        self.assertEqual(agent.get_description(), "测试描述")

if __name__ == '__main__':
    unittest.main()

