"""
Flask主应用 - 使用可扩展的Agent架构
"""
import os, sys
sys.path.insert(0, os.path.dirname(__file__))
from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
from core.agent_factory import AgentFactory
import config

app = Flask(__name__)
CORS(app)

# 全局Agent实例（懒加载）
_agent = None

def get_agent():
    """获取Agent实例（单例模式）"""
    global _agent
    if _agent is None:
        try:
            _agent = AgentFactory.create_agent()
            print(f"✅ Agent创建成功，使用模型: {config.DEFAULT_CONFIG['model_type']}")
        except Exception as e:
            print(f"❌ Agent创建失败: {e}")
            raise
    return _agent

@app.route('/')
def index():
    """返回H5页面"""
    return render_template('index.html')

@app.route('/api/joke', methods=['POST'])
def get_joke():
    """获取笑话API"""
    try:
        agent = get_agent()
        data = request.json
        user_input = data.get('input', '讲个笑话')
        
        # ========== LLM调用核心部分 ==========
        # 使用Agent处理用户输入，这里会触发LLM推理
        # agent.invoke() 会：
        # 1. 将用户输入传递给LLM（Ollama或Gemini）
        # 2. LLM根据工具描述决定调用哪个工具
        # 3. 执行工具（获取笑话）
        # 4. 将工具结果返回给LLM生成最终回复
        # 5. 返回Agent的完整响应
        # 
        # 底层流程：
        # - Ollama: HTTP POST -> http://localhost:11434/api/generate
        # - Gemini: REST API -> https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent
        # ====================================
        res = agent.invoke({"input": user_input})
        response = res.get("output", res if isinstance(res, str) else str(res))
        
        return jsonify({
            'success': True,
            'joke': response,
            'model_type': config.DEFAULT_CONFIG['model_type']
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'joke': f'错误: {str(e)}',
            'error': str(e)
        }), 500

@app.route('/api/config', methods=['GET'])
def get_config():
    """获取当前配置"""
    return jsonify({
        'model_type': config.DEFAULT_CONFIG['model_type'],
        'available_models': AgentFactory.get_available_models(),
        'current_model_config': config.DEFAULT_CONFIG.get(
            config.DEFAULT_CONFIG['model_type'], {}
        )
    })

@app.route('/api/config', methods=['POST'])
def update_config():
    """更新配置（动态切换模型）"""
    global _agent
    data = request.json
    model_type = data.get('model_type')
    
    if model_type not in AgentFactory.get_available_models():
        return jsonify({
            'success': False,
            'error': f'不支持的模型类型: {model_type}'
        }), 400
    
    try:
        # 重新创建Agent
        _agent = AgentFactory.create_agent(model_type=model_type)
        config.DEFAULT_CONFIG['model_type'] = model_type
        
        return jsonify({
            'success': True,
            'message': f'已切换到 {model_type}',
            'model_type': model_type
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

if __name__ == '__main__':
    print("🎭 笑话Agent服务启动中...")
    print(f"📦 当前模型: {config.DEFAULT_CONFIG['model_type']}")
    print("💡 可以通过 /api/config 接口切换模型")
    print("📱 打开浏览器访问: http://localhost:5000")
    
    # 自动打开浏览器
    import webbrowser
    import threading
    def open_browser():
        import time
        time.sleep(1.5)  # 等待服务启动
        webbrowser.open('http://localhost:5000')
    
    threading.Thread(target=open_browser, daemon=True).start()
    
    app.run(debug=True, host='0.0.0.0', port=5000)

