from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from dotenv import load_dotenv

load_dotenv()

PROMPT_THEME = """
    你是一个专业的主题选择助手，请根据以下要求为文献选择对应的主题：
    1.可供选择的主题包括这11个主题：数学、物理、化学、生物、计算机科学、人工智能、经济学、心理学、社会学、医学、其它主题。
    另外，当无法确定主题或不属于上述主题时，请选择“其它主题”。
    2.输入为一个文献的标题，输出为一个主题名称。
    3.你的回答格式为一个最合适的主题名称，主题名称必须来自可供选择的主题中，且不需要任何解释或额外信息，不得包含任何多余的文本或标点符号。
    4.示例：

    输入：
    {{
        "title": "Evaluation Model of Diabetes Therapeutic Effect Based on Multiple Linear Regression",
    }}
    输出：
    "医学"
    
    输入：
    {{
        "title": "圆形区域对偶二次多项式回归模型的 D 最优设计",
    }}
    输出：
    "数学"
    """

class ThemeSelector:
    def __init__(self):
        self._init_model()
        self.create_chain()

    def _init_model(self):
        self.llm = ChatOpenAI(
            temperature=0,
            model="gpt-3.5-turbo",
            streaming=True  # 添加 streaming 支持，支持更好的异步处理
        )

    def create_chain(self):
        prompt = ChatPromptTemplate.from_messages([
            ("system", PROMPT_THEME),
            ("human", "{input}")
        ])
        self.chain = prompt | self.llm | StrOutputParser()
    async def choose_theme(self, user_input: str):
        """
        根据文献标题选择主题
        :param user_input: 文献标题
        :return: 主题名称
        """
        response = self.chain.invoke({"input": user_input})
        return response.strip('"\\\'')

# 示例调用
# import asyncio
# theme_selector = ThemeSelector()
# async def main():
#     query = """{ "title": "D-Optimal Design for Duality Quadratic Polynomial Regression Models in Circle Region"}"""
#     response = await theme_selector.choose_theme(query)
#     print(response)
#
#
# # 运行异步函数
# asyncio.run(main())
