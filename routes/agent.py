from fastapi import APIRouter, Depends
from tools import *
from models import *
from Translate_RAG_Chain import TranslateChatBot
from agent_tools import LiteratureAgent
from .auth import get_current_user
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
        response = await chatbot.talk_with_memory(user_input=talk_in.text,session_id=current_user.id)
    except Exception as e:
        return create_response("error", 500, f"与Agent对话时发生错误: {str(e)}")
    return create_response("success", 200, response)

# 清除记忆
@agent.delete('/clear')
async def clear_memory(current_user: User = Depends(get_current_user)):
    await chatbot.clear_history(session_id=current_user.id)
    return create_response("success", 200, "记忆已清除，可以开始新对话了！")



