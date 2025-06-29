import os
from pathlib import Path
from datetime import datetime
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser
from langchain_community.chat_message_histories import FileChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory
from .Prompts import prompt_translate
from .tools import gain_userinput
from dotenv import load_dotenv
from langchain_community.llms import OpenAI

load_dotenv()


# 定义类 ChatBot，用于处理文献翻译、文献总结和文献并入功能
class ChatBotTranslate:
    # 初始化方法（创建实例时，自动初始化）
    def __init__(self):
        self.init_environment()
        self.init_model()
        self.create_chain()

    def init_environment(self):
        if "OPENAI_API_KEY" not in os.environ:
            raise ValueError("请设置OPENAI_API_KEY环境变量")

    # def init_model(self):
    #     self.llm = OpenAI(
    #         model_name="qwen-max",
    #     )

    def init_model(self):
        self.llm = ChatOpenAI(
            temperature=0,
            model="gpt-3.5-turbo",
            frequency_penalty=0.5,
            presence_penalty=0.5,
            streaming=True  # 添加 streaming 支持，支持更好的异步处理
        )

    def create_chain(self):
        # 提示词
        prompt = ChatPromptTemplate.from_messages([
            ("system", prompt_translate),
            ("human", "{input}")
        ])
        self.chain = prompt | self.llm | StrOutputParser()

    # 文本翻译（通用风格）
    async def gain_response(self, user_input: str, source_language: str, translated_language: str, style: str):
        text = gain_userinput(user_input, source_language, translated_language, style)
        # response = self.chain.invoke({"input": input})
        response = await self.chain.ainvoke({"input": text})  # 改用异步请求
        text["content"] = response.strip('"\\\'')  # 移除文本前后的 ", \, '
        return text

    # # 文本翻译（学术风格）
    # async def gain_academic_response(self, user_input: str, source_language: str, translated_language: str):
    #     input = gain_userinput(user_input, source_language, translated_language, "学术风格")
    #     # response = self.chain.invoke({"input": input})
    #     response = await self.chain.ainvoke({"input": input})  # 改用异步请求
    #     input["content"] = response.strip('"\\\'')  # 移除文本前后的 ", \, '
    #     return input