import os
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from Summary_Chain.SummaryPrompts import PROMPT_SUMMARY
from dotenv import load_dotenv

load_dotenv()

# 定义类 SummaryChatBot，用于处理文献翻译
class SummaryChatBot:
    # 初始化方法（创建实例时，自动初始化）
    def __init__(self):
        self._init_environment()
        self._init_model()
        self.create_summary_chain()

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

    # 创建文献总结链（无RAG）
    def create_summary_chain(self):
        prompt = ChatPromptTemplate.from_messages([
            ("system", PROMPT_SUMMARY),
            ("human", "{input}")
        ])
        self.summary_chain = prompt | self.llm | StrOutputParser()

    async def summary(self,text: str, language: str = "Chinese", detail_level: str = "medium") -> dict:
        """学术文献总结工具"""
        processed_input = {
            "text": text,
            "language": language,
            "detail_level": detail_level
        }
        response = await self.summary_chain.ainvoke({"input": processed_input})
        processed_input["text"] = str(response).strip('"\\\'')  # 移除文本前后的 ", \, '
        return processed_input

