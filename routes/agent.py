from fastapi import APIRouter, Depends
from tools import *
from models import *
from dotenv import load_dotenv
from Translate_RAG_Chain import TranslateChatBot
from agent_tools import LiteratureAgent
load_dotenv()

# 实例化AI
chatbot = LiteratureAgent()

# agent相关路由
agent = APIRouter()

# 与agent交互
@agent.post('/talk')
async def agent_talk(talk_in:TalkIn):
    response = await chatbot.talk(talk_in.text)
    return create_response("success", 200, response)




