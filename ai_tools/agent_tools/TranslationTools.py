from langchain.agents import tool
from langchain_core.prompts import ChatPromptTemplate
from ai_tools.Prompts import PROMPT_ACADEMIC_TRANSLATE, PROMPT_GENERAL_TRANSLATE
from langchain_core.output_parsers import StrOutputParser
from ai_tools.tools import gain_userinput
from models_in import TranslateInput
from functools import partial

# agent工具函数


def general_translate(llm,text: str, source_language: str, translated_language: str) -> str:
    """通用风格翻译工具，适合日常对话、非正式文本"""
    prompt = ChatPromptTemplate.from_messages([
        ("system", PROMPT_GENERAL_TRANSLATE),
        ("human", "{input}")
    ])
    chain = prompt | llm | StrOutputParser()
    processed_text = gain_userinput(text, source_language=source_language, translated_language=translated_language, style="general")
    response = chain.invoke({"input": processed_text})
    return str(response).strip('"\\\'')

def academic_translate(self, text: str, source_language: str, translated_language: str) -> str:
    """学术风格翻译工具，适合论文、技术文档等严谨场景"""
    prompt = ChatPromptTemplate.from_messages([
        ("system", PROMPT_ACADEMIC_TRANSLATE),
        ("human", "{input}")
    ])
    chain = prompt | self.llm | StrOutputParser()
    text = gain_userinput(text, source_language=source_language, translated_language=translated_language, style="general")
    response = chain.invoke({"input": text})
    return str(response).strip('"\\\'')

