from fastapi import APIRouter, Depends
from tools import *
from models import *
from .auth import get_current_user
from ai_tools import *
from dotenv import load_dotenv

load_dotenv()
chatbot = ChatBotTranslate()

# 翻译相关路由
translations = APIRouter()


# 翻译传入文件：翻译文件的内容
@translations.post('/file')
async def translate_file():
    return create_response("success", 200, "返回翻译文件")


# 翻译文本内容的接口
@translations.post('/text')
async def translate_text(translation_in: TranslationIn):
    try:
        response = await chatbot.gain_response(
            user_input=translation_in.content,
            source_language=translation_in.source_language,
            translated_language=translation_in.translated_language,
            style=translation_in.style
        )
        return create_response("success", 200, response)
    except Exception as e:
        return create_response("error", 500, str(e))
