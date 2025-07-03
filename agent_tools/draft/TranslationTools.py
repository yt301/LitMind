from langchain_core.prompts import ChatPromptTemplate
from ai_tools.Prompts import PROMPT_ACADEMIC_TRANSLATE, PROMPT_GENERAL_TRANSLATE
from langchain_core.output_parsers import StrOutputParser
from ai_tools.input_tools import gain_userinput
from models_in import TranslateInput

def general_translate(llm, text: str, source_language: str, translated_language: str) -> str:
    """将文本从源语言翻译到目标语言，将返回翻译后的文本。"""
    prompt = ChatPromptTemplate.from_messages([
        ("system", PROMPT_GENERAL_TRANSLATE),
        ("human", "{input}")
    ])
    chain = prompt | llm | StrOutputParser()
    processed_text = gain_userinput(text,
                                  source_language=source_language,
                                  translated_language=translated_language,
                                  style="general")
    response = chain.invoke({"input": processed_text})
    return str(response).strip('"\\\'')

# TranslationTools.py (新增函数)
def text_length_counter(text: str) -> int:
    """统计输入文本的字符长度（包含空格）"""
    return len(text)