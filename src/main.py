import os
import uuid
from pathlib import Path
from dotenv import dotenv_values
from flask import Flask, request, jsonify, session
from agent import CommandAgent

# 直接从 .env 文件读取配置（不依赖系统环境变量）
env_path = Path(__file__).parent / ".env"
env_config = dotenv_values(env_path)

# 覆盖系统环境变量
os.environ.update(env_config)

app = Flask(__name__)
app.secret_key = env_config.get("SECRET_KEY", "your-secret-key-here")

# 调试：打印环境变量（直接从 env_config 读取）
print(f"[DEBUG] MODEL_NAME: {env_config.get('MODEL_NAME')}")
print(f"[DEBUG] BASE_URL: {env_config.get('BASE_URL')}")
print(f"[DEBUG] API_KEY: {env_config.get('API_KEY')}")

# 存储用户的 Agent 实例
user_agents = {}

HTML = open("index.html", "r").read()


def get_or_create_agent(user_id: str) -> CommandAgent:
    """获取或创建用户的 Agent 实例"""
    if user_id not in user_agents:
        user_agents[user_id] = CommandAgent(
            model=env_config.get("MODEL_NAME"),
            base_url=env_config.get("BASE_URL"),
            api_key=env_config.get("API_KEY")
        )
    return user_agents[user_id]


def get_user_id() -> str:
    """获取用户 ID，如果没有则创建新的"""
    if "user_id" not in session:
        session["user_id"] = str(uuid.uuid4())
    return session["user_id"]


@app.get("/")
def index():
    return HTML


@app.post("/chat")
def chat():
    """多轮会话接口"""
    user_id = get_user_id()
    user_input = request.json["message"]
    
    # 获取或创建该用户的 Agent
    agent = get_or_create_agent(user_id)
    
    # 执行聊天
    steps = agent.chat(user_input)
    
    return jsonify(
        steps=steps,
        user_id=user_id,
        session_id=request.cookies.get("session", "new")
    )


@app.post("/reset")
def reset():
    """重置当前用户的会话"""
    user_id = get_user_id()
    
    if user_id in user_agents:
        user_agents[user_id].reset_messages()
        return jsonify({
            "status": "success",
            "message": "当前会话已重置",
            "user_id": user_id
        })
    
    return jsonify({
        "status": "error",
        "message": "用户会话不存在"
    })


@app.post("/clear-session")
def clear_session():
    """清除当前用户的所有数据"""
    user_id = get_user_id()
    
    if user_id in user_agents:
        del user_agents[user_id]
    
    session.clear()
    
    return jsonify({
        "status": "success",
        "message": "会话已清除"
    })


@app.get("/session-info")
def session_info():
    """获取当前会话信息"""
    user_id = get_user_id()
    
    return jsonify({
        "user_id": user_id,
        "active_sessions": len(user_agents),
        "has_agent": user_id in user_agents,
        "message_count": len(user_agents[user_id].messages) if user_id in user_agents else 0
    })


if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True, port=5001)

