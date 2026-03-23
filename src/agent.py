import os
import re
from pathlib import Path
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from load_prompt import build_system_prompt

class CommandAgent:
    """基于 Langchain 的命令执行代理类"""
    
    def __init__(self, model: str, base_url: str, api_key: str):
        """
        初始化 Agent
        
        Args:
            model: 模型名称 (e.g., "gpt-3.5-turbo")
            base_url: API 基础 URL
            api_key: API 密钥
        """
        self.model = model
        self.base_url = base_url
        self.api_key = api_key
        print(f" [Agent] 初始化成功，模型: {model}，基础 URL: {base_url}，API 密钥: {api_key}")
        # 初始化 Langchain ChatOpenAI 客户端
        self.llm = ChatOpenAI(
            model_name=model,
            base_url=base_url,
            api_key=api_key,
            temperature=0.7,
        )
    
        # 使用新的系统提示词构建函数，动态加载所有 skills
        self.system_prompt = build_system_prompt(read_tool_name="read_file")
        
        # 消息历史
        self.messages = [SystemMessage(content=self.system_prompt)]
    
    def execute_command(self, command: str) -> str:
        """执行命令并返回结果"""
        try:
            result = os.popen(command).read()
            return result
        except Exception as e:
            return f"命令执行失败: {str(e)}"
    
    def chat(self, user_input: str) -> list:
        """
        与大模型交互，并执行命令
        
        Args:
            user_input: 用户输入
            
        Returns:
            步骤列表，包含 AI 回复和命令执行结果
        """
        print(f" [用户] {user_input}")
        self.messages.append(HumanMessage(content=user_input))
        print(self.messages)
        steps = []
        
        while True:
            # 调用大模型
            print(f" [Agent] 调用大模型 {self.messages}")
            response = self.llm.invoke(self.messages)
            reply = response.content
            print(f" [Agent] {reply}")
            
            # 添加 AI 消息到历史
            self.messages.append(AIMessage(content=reply))
            print(self.messages)
            steps.append({"type": "ai", "content": reply})
            
            # 检查是否完成
            if reply.strip().startswith("完成:"):
                break
            
            # 提取并执行命令
            if "命令:" in reply:
                try:
                    command = reply.strip().split("命令:")[1].strip()
                    command_result = self.execute_command(command)
                    print(f" [Agent] 执行完毕: {command_result}")
                    steps.append({"type": "cmd", "content": command_result})
                    
                    # 将执行结果添加到消息历史
                    self.messages.append(HumanMessage(content=f"执行完毕: {command_result}"))
                except Exception as e:
                    error_msg = f"命令解析失败: {str(e)}"
                    print(f" [Agent] {error_msg}")
                    steps.append({"type": "error", "content": error_msg})
                    self.messages.append(HumanMessage(content=error_msg))
        
        return steps
    
    def reset_messages(self):
        """重置消息历史"""
        self.messages = [SystemMessage(content=self.system_prompt)]
