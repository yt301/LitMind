from fastapi import APIRouter, Depends
from tools import *
from models import *
from dotenv import load_dotenv
from Translate_RAG import TranslateChatBot

load_dotenv()

# 实例化AI
chatbot = TranslateChatBot()
# agent = TranslationAgent()  # agent版

# 翻译相关路由
translations = APIRouter()


# 翻译传入文件：翻译文件的内容
@translations.post('/file')
async def translate_file():
    return create_response("success", 200, "返回翻译文件")


# 翻译文本内容的接口（Agent版-有RAG-通用风格、学术风格、文学风格）
@translations.post('/text')
async def translate_text(translation_in: TranslationIn):
    try:
        response = await chatbot.translate(
            text=translation_in.text,
            source_language=translation_in.source_language,
            translated_language=translation_in.translated_language,
            style=translation_in.style
        )
        return create_response("success", 200, response)
    except Exception as e:
        return create_response("error", 500, str(e))


# # 翻译文本内容的接口（Agent版-有RAG-通用风格、学术风格、文学风格）
# @translations.post('/text')
# async def translate_text(translation_in: TranslationIn):
#     try:
#         response = await agent.translate(
#             text=translation_in.text,
#             source_language=translation_in.source_language,
#             translated_language=translation_in.translated_language,
#             style=translation_in.style
#         )
#         return create_response("success", 200, response)
#     except Exception as e:
#         return create_response("error", 500, str(e))
#


# # 翻译文本内容的接口（LLM版-无RAG-通用风格）
# @translations.post('/text')
# async def translate_text(translation_in: TranslationIn):
#     try:
#         response = await chatbot.gain_response(
#             user_input=translation_in.text,
#             source_language=translation_in.source_language,
#             translated_language=translation_in.translated_language,
#             style=translation_in.style
#         )
#         return create_response("success", 200, response)
#     except Exception as e:
#         return create_response("error", 500, str(e))



