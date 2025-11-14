"""
Flask主应用 - 可扩展的Agent架构
"""
import os
import sys

# 必须在导入其他模块之前设置路径
sys.path.insert(0, os.path.dirname(__file__))

import time
import threading
import webbrowser
from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
from core.agent_service import agent_service
from core.agent_factory import AgentFactory
import config

app = Flask(__name__)
CORS(app)


@app.route('/')
def index():
    """返回H5页面"""
    return render_template('index.html')


@app.route('/api/agent/invoke', methods=['POST'])
def invoke_agent():
    """调用Agent处理请求"""
    try:
        data = request.json or {}
        agent_name = data.get('agent_name')
        user_input = data.get('input', '')
        
        log_config = config.DEFAULT_CONFIG.get("logging", {})
        if log_config.get("llm_console_output", False):
            print(f"\n🎯 用户输入: {user_input}")
            print(f"🤖 使用Agent: {agent_name or '默认'}")
            print("🚀 开始Agent处理...\n")
        
        result = agent_service.invoke_agent(agent_name=agent_name, user_input=user_input)
        
        status_code = 200 if result['success'] else 500
        return jsonify(result), status_code
    except Exception as e:
        return jsonify({
            'success': False,
            'output': f'错误: {str(e)}',
            'error': str(e)
        }), 500


@app.route('/api/agents', methods=['GET'])
def list_agents():
    """列出所有可用的Agent"""
    try:
        agents = AgentFactory.get_available_agents()
        return jsonify({'success': True, 'agents': agents})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/config', methods=['GET'])
def get_config():
    """获取当前配置"""
    try:
        return jsonify(agent_service.get_config())
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/config', methods=['POST'])
def update_config():
    """更新配置"""
    try:
        result = agent_service.update_config(request.json or {})
        status_code = 200 if result['success'] else 400
        return jsonify(result), status_code
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/ollama/models', methods=['GET'])
def get_ollama_models():
    """获取Ollama本地可用模型列表"""
    try:
        import requests
        base_url = config.DEFAULT_CONFIG.get('ollama', {}).get('base_url', 'http://localhost:11434')
        response = requests.get(f"{base_url}/api/tags", timeout=2)
        
        if response.status_code == 200:
            models = [model['name'] for model in response.json().get('models', [])]
            return jsonify({'success': True, 'models': models})
        else:
            return jsonify({
                'success': False,
                'error': f'Ollama服务响应错误: {response.status_code}',
                'models': []
            }), 500
    except requests.exceptions.RequestException as e:
        return jsonify({
            'success': False,
            'error': f'无法连接到Ollama服务: {str(e)}',
            'models': []
        }), 500
    except Exception as e:
        return jsonify({'success': False, 'error': str(e), 'models': []}), 500


if __name__ == '__main__':
    print("🎭 Agent服务启动中...")
    print(f"📦 当前模型: {config.DEFAULT_CONFIG.get('model_type', 'ollama')}")
    print(f"🤖 默认Agent: {config.DEFAULT_CONFIG.get('default_agent', 'joke')}")
    print("💡 可以通过 /api/config 接口切换模型和Agent")
    print("📱 打开浏览器访问: http://localhost:5000")
    
    is_reloader = os.environ.get('WERKZEUG_RUN_MAIN') != 'true'
    if not is_reloader:
        def open_browser():
            time.sleep(1.5)
            webbrowser.open('http://localhost:5000')
        threading.Thread(target=open_browser, daemon=True).start()
    
    app.run(debug=True, host='0.0.0.0', port=5000)
