from fastapi import APIRouter, Depends
from tools import *
from models import *
from dotenv import load_dotenv
from Translate_RAG_Chain import TranslateChatBot
from Summary_Chain import SummaryChatBot

load_dotenv()

# 实例化AI
chatbot = SummaryChatBot()

# 翻译相关路由
summary = APIRouter()


# 总结传入文件的内容，返回总结文本
@summary.post('/file')
async def summary_file():
    return create_response("success", 200, "返回总结内容")


# 总结文本内容，返回总结文本
@summary.post('/text')
async def summary_text(summary_in: SummaryIn):
    try:
        response = await chatbot.summary(
            text=summary_in.text,
            language=summary_in.language,
            detail_level=summary_in.detail_level,
        )
        return create_response("success", 200, response)
    except Exception as e:
        return create_response("error", 500, str(e))




