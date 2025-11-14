"""
Flask主应用 - 使用可扩展的Agent架构（重构版）
支持多Agent类型、服务层分离、可扩展架构
"""
import os, sys
sys.path.insert(0, os.path.dirname(__file__))
from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
from core.agent_service import agent_service
from core.agent_factory import AgentFactory
import config

app = Flask(__name__)
CORS(app)

# ========== 向后兼容：全局Agent实例（懒加载） ==========
# 保留此代码以支持旧版本的直接调用
_legacy_agent = None

def get_legacy_agent():
    """获取传统Agent实例（向后兼容）"""
    global _legacy_agent
    if _legacy_agent is None:
        try:
            _legacy_agent = AgentFactory.create_legacy_agent()
            print(f"✅ 传统Agent创建成功，使用模型: {config.DEFAULT_CONFIG['model_type']}")
        except Exception as e:
            print(f"❌ 传统Agent创建失败: {e}")
            raise
    return _legacy_agent
# ====================================================

@app.route('/')
def index():
    """返回H5页面"""
    return render_template('index.html')

# ========== 新版本API（使用服务层） ==========
@app.route('/api/agent/invoke', methods=['POST'])
def invoke_agent():
    """调用Agent处理请求（新版本API）"""
    try:
        data = request.json or {}
        agent_name = data.get('agent_name')
        user_input = data.get('input', '')
        
        # 从配置读取是否显示简要信息
        log_config = config.DEFAULT_CONFIG.get("logging", {})
        show_brief = log_config.get("llm_console_output", False)
        
        if show_brief:
            print(f"\n🎯 用户输入: {user_input}")
            print(f"🤖 使用Agent: {agent_name or '默认'}")
            print("🚀 开始Agent处理...\n")
        
        # 使用服务层调用Agent
        result = agent_service.invoke_agent(
            agent_name=agent_name,
            user_input=user_input
        )
        
        if result['success']:
            return jsonify(result)
        else:
            return jsonify(result), 500
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
        return jsonify({
            'success': True,
            'agents': agents
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# ========== 向后兼容：旧版本API ==========
@app.route('/api/joke', methods=['POST'])
def get_joke():
    """获取笑话API（向后兼容）"""
    try:
        data = request.json or {}
        user_input = data.get('input', '讲个笑话')
        
        # 使用服务层（指定使用joke agent）
        result = agent_service.invoke_agent(
            agent_name='joke',
            user_input=user_input
        )
        
        if result['success']:
            return jsonify({
                'success': True,
                'joke': result['output'],
                'model_type': result.get('model_type', config.DEFAULT_CONFIG['model_type'])
            })
        else:
            return jsonify({
                'success': False,
                'joke': result.get('output', '错误'),
                'error': result.get('error')
            }), 500
    except Exception as e:
        return jsonify({
            'success': False,
            'joke': f'错误: {str(e)}',
            'error': str(e)
        }), 500
# =========================================

@app.route('/api/config', methods=['GET'])
def get_config():
    """获取当前配置"""
    try:
        config_data = agent_service.get_config()
        return jsonify(config_data)
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/ollama/models', methods=['GET'])
def get_ollama_models():
    """获取Ollama本地可用模型列表"""
    try:
        import requests
        base_url = config.DEFAULT_CONFIG.get('ollama', {}).get('base_url', 'http://localhost:11434')
        response = requests.get(f"{base_url}/api/tags", timeout=2)
        if response.status_code == 200:
            data = response.json()
            models = [model['name'] for model in data.get('models', [])]
            return jsonify({
                'success': True,
                'models': models
            })
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
        return jsonify({
            'success': False,
            'error': str(e),
            'models': []
        }), 500

@app.route('/api/config', methods=['POST'])
def update_config():
    """更新配置（动态切换模型、模型名称、API key等）"""
    try:
        data = request.json or {}
        
        # 使用服务层更新配置
        result = agent_service.update_config(data)
        
        if result['success']:
            return jsonify(result)
        else:
            return jsonify(result), 400
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

if __name__ == '__main__':
    print("🎭 Agent服务启动中...")
    print(f"📦 当前模型: {config.DEFAULT_CONFIG.get('model_type', 'ollama')}")
    print(f"🤖 默认Agent: {config.DEFAULT_CONFIG.get('default_agent', 'joke')}")
    print("💡 可以通过 /api/config 接口切换模型和Agent")
    print("📱 打开浏览器访问: http://localhost:5000")
    
    # 自动打开浏览器（只在主进程中打开，避免reloader重复打开）
    import webbrowser
    import threading
    
    # Flask debug模式会启动两个进程：主进程和reloader监控进程
    # 通过环境变量检测是否是reloader进程，只在主进程中打开浏览器
    is_reloader = os.environ.get('WERKZEUG_RUN_MAIN') != 'true'
    
    if not is_reloader:  # 只在主进程中打开浏览器
        def open_browser():
            import time
            time.sleep(1.5)  # 等待服务启动
            webbrowser.open('http://localhost:5000')
        
        threading.Thread(target=open_browser, daemon=True).start()
    
    app.run(debug=True, host='0.0.0.0', port=5000)
