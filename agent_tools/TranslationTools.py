from langchain_core.prompts import ChatPromptTemplate
from agent_tools.Prompts import PROMPT_ACADEMIC_TRANSLATE, PROMPT_GENERAL_TRANSLATE, PROMPT_LITERARY_TRANSLATE
from langchain_core.output_parsers import StrOutputParser
from agent_tools.tools import gain_userinput
from agent_tools.AcademicKnowledgeBase_FAISS import AcademicKnowledgeBase

# chroma向量知识库
academic_kb = AcademicKnowledgeBase()


# agent工具函数


def general_translate(llm, text: str, source_language: str, translated_language: str, style: str) -> str:
    """通用风格翻译工具，适合日常对话、非正式文本"""
    prompt = ChatPromptTemplate.from_messages([
        ("system", PROMPT_GENERAL_TRANSLATE),
        ("human", "{input}")
    ])
    chain = prompt | llm | StrOutputParser()
    processed_input = gain_userinput(userinput=text, source_language=source_language,
                                     translated_language=translated_language, style="general")
    response = chain.invoke({"input": processed_input})
    return str(response).strip('"\\\'')


def academic_translate(llm, text: str, source_language: str, translated_language: str, style: str) -> str:
    """学术风格翻译工具，适合论文、技术文档等严谨场景"""
    # 在知识库中检索相关知识，并加入提示词
    relevant_info = academic_kb.retrieve_relevant_info(text,k=1)
    context = "\n\n此外，翻译文本时可以参照如下相关学术背景知识:\n" + "\n".join(relevant_info) if relevant_info else ""
    # print("检索到的相关学术背景知识:", context)
    prompt = ChatPromptTemplate.from_messages([
        ("system", PROMPT_ACADEMIC_TRANSLATE + context),
        ("human", "{input}")
    ])
    chain = prompt | llm | StrOutputParser()
    processed_input = gain_userinput(userinput=text, source_language=source_language,
                                     translated_language=translated_language, style="academic")
    response = chain.invoke({"input": processed_input})
    return str(response).strip('"\\\'')


def literary_translate(llm, text: str, source_language: str, translated_language: str, style: str) -> str:
    """文学风格翻译工具，适合小说、散文等文学作品"""
    prompt = ChatPromptTemplate.from_messages([
        ("system", PROMPT_LITERARY_TRANSLATE),
        ("human", "{input}")
    ])
    chain = prompt | llm | StrOutputParser()
    processed_input = gain_userinput(userinput=text, source_language=source_language,
                                     translated_language=translated_language, style="literary")
    response = chain.invoke({"input": processed_input})
    return str(response).strip('"\\\'')
