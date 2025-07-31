from fastapi import APIRouter, Depends
from tools import *
from models import *
from config import FILE_PATH
from Translate_RAG_Chain import TranslateChatBot
from agent_tools import LiteratureAgent
from .auth import get_current_user
import os
from dotenv import load_dotenv
load_dotenv()

# 实例化AI
chatbot = LiteratureAgent()

# agent相关路由
agent = APIRouter()

# 与agent交互
@agent.post('/talk')
async def agent_talk(talk_in:TalkIn,current_user: User = Depends(get_current_user)):
    try:
        file_paths = []
        if talk_in.filenames:
            for filename in talk_in.filenames:
                # 检查文件是否存在
                file_path = os.path.join(FILE_PATH, str(current_user.id), filename)
                if not os.path.exists(file_path):
                    return create_response("error", 404, f"{filename}不存在！")
                # 验证文件属于当前用户
                if not await File.filter(file_name=filename, user_id=current_user.id).exists():
                    return create_response("error", 403, "无权访问此文件！")
                file_paths.append(file_path)
        response = await chatbot.talk_with_memory(user_input=talk_in.text,file_paths=file_paths,session_id=current_user.id)
    except Exception as e:
        return create_response("error", 500, f"与Agent对话时发生错误: {str(e)}")
    return create_response("success", 200, response)

# 清除记忆
@agent.delete('/clear')
async def clear_memory(current_user: User = Depends(get_current_user)):
    await chatbot.clear_history(session_id=current_user.id)
    return create_response("success", 200, "记忆已清除，可以开始新对话了！")



