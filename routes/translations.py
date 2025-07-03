from fastapi import APIRouter, Depends
from tools import *
from models import *
from dotenv import load_dotenv
from Translate_RAG_Chain import TranslateChatBot
from config import FILE_PATH
from .auth import get_current_user
import os



load_dotenv()

# 实例化AI
chatbot = TranslateChatBot()

# 翻译相关路由
translations = APIRouter()


# 根据文件名翻译相应文件，生成翻译后的文件
@translations.post('/file')
async def translate_file(translation_file_in:TranslationFileIn,current_user: User = Depends(get_current_user)):
    # 检查用户目录是否存在
    user_dir = os.path.join(FILE_PATH, str(current_user.id))
    if not os.path.exists(user_dir):
        return create_response("error", 404, "用户目录不存在，请先上传文件！")

    filename = translation_file_in.filename
    filepath = os.path.join(user_dir, filename)

    # 检查文件是否存在
    if not os.path.exists(filepath):
        return create_response("error", 404, f"{filename}不存在！")

    # 验证文件属于当前用户
    if not await File.filter(file_name=filename, user_id=current_user.id).exists():
        return create_response("error", 403, "无权访问此文件！")

    try:
        # 统一读取文件内容
        content = read_file_content(filepath)

        # 调用翻译接口
        translated_content = await chatbot.translate(
            text=content,
            source_language=translation_file_in.source_language,
            translated_language=translation_file_in.translated_language,
            style=translation_file_in.style
        )

        # 保存翻译后的文件
        translated_filename, translated_filepath = await save_translated_file(
            translated_content["text"],
            filename,
            user_dir
        )

        # 创建文件记录
        await File.create(
            file_name=translated_filename,
            file_path=translated_filepath,
            file_type = detect_file_type(filepath),
            file_size=os.path.getsize(translated_filepath),
            user_id=current_user.id,
        )

        return create_response("success", 200, {
            "original_file": filename,
            "translated_file": translated_filename
        })

    except ValueError as e:
        return create_response("error", 400, str(e))
    except Exception as e:
        return create_response("error", 500, f"文件翻译失败: {str(e)}")



# 翻译文本内容的接口（有RAG-通用风格、学术风格）
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




