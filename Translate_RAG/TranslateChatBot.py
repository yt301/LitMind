import os
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from Translate_RAG.tools import gain_userinput
from dotenv import load_dotenv
from Translate_RAG.TranslatePrompts import PROMPT_GENERAL_TRANSLATE, PROMPT_ACADEMIC_TRANSLATE
from Translate_RAG.AcademicKnowledgeBase_FAISS import AcademicKnowledgeBase

load_dotenv()

# chroma向量知识库
academic_kb = AcademicKnowledgeBase()

# 定义类 TranslateChatBot，用于处理文献翻译
class TranslateChatBot:
    # 初始化方法（创建实例时，自动初始化）
    def __init__(self):
        self._init_environment()
        self._init_model()
        self.create_general_chain()
        self.create_academic_chain()

    def _init_environment(self):
        if "OPENAI_API_KEY" not in os.environ:
            raise ValueError("请设置OPENAI_API_KEY环境变量")

    def _init_model(self):
        self.llm = ChatOpenAI(
            temperature=0.1,
            model="gpt-3.5-turbo",
            frequency_penalty=0.7,
            presence_penalty=0.4,
            streaming=True  # 添加 streaming 支持，支持更好的异步处理
        )

    # 创建通用风格翻译链（无RAG）
    def create_general_chain(self):
        prompt = ChatPromptTemplate.from_messages([
            ("system", PROMPT_GENERAL_TRANSLATE),
            ("human", "{input}"),
        ])
        self.general_chain = prompt | self.llm | StrOutputParser()

    # 创建学术风格翻译链（有RAG）
    def create_academic_chain(self):
        prompt = ChatPromptTemplate.from_messages([
            ("system", PROMPT_ACADEMIC_TRANSLATE),
            ("human", "{input}"),
            ("system", "{context}"),
        ])  # 添加 context 占位符用于RAG
        self.academic_chain = prompt | self.llm | StrOutputParser()

    async def translate(self, text: str, source_language: str, translated_language: str, style: str) -> dict:
        processed_input = gain_userinput(userinput=text, source_language=source_language,
                                         translated_language=translated_language, style=style)
        if style == "general":
            response = await self.general_chain.ainvoke({"input": processed_input})  # 改用异步请求
        elif style == "academic":
            # 在知识库中检索相关知识，并加入提示词
            relevant_info = academic_kb.retrieve_relevant_info(text, k=1)
            context = "\n\n此外，翻译文本时可以参照如下相关学术背景知识:\n" + "\n".join(
                relevant_info) if relevant_info else ""
            # print("检索到的相关学术背景知识:", context)
            response = await self.academic_chain.ainvoke({"input": processed_input,"context":context})  # 改用异步请求
        else:
            raise ValueError(f"Unsupported style: {style}. Supported styles are: general, academic.")
        processed_input["text"] = str(response).strip('"\\\'')  # 移除文本前后的 ", \, '
        return processed_input
