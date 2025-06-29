from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain.agents import initialize_agent, Tool
from langchain import hub
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
from langchain.agents import tool
from models_in import TranslateInput
from TranslationTools import general_translate, academic_translate, literary_translate
from langchain.tools import StructuredTool

load_dotenv()


# 与agent交互的方法
# response = await self.agent_executor.ainvoke("input": {user_input})


class TranslationAgent:
    def __init__(self):
        self.llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)
        self.tools = [
            StructuredTool.from_function(
                func=lambda text, source_language, translated_language,style: general_translate(
                    self.llm, text, source_language, translated_language,style
                ),
                name="GeneralTranslator",
                description="适合日常对话、非正式文本的流畅翻译（general风格翻译）",
                args_schema=TranslateInput,  # 定义参数的结构化输入
                return_direct=True  # 绕过Agent的结果处理，直接返回工具调用结果

            ),
            StructuredTool.from_function(
                func=lambda text, source_language, translated_language,style: academic_translate(
                    self.llm, text, source_language, translated_language,style
                ),
                name="AcademicTranslator",
                description="适合论文、技术文档等严谨场景的学术翻译（academic风格翻译）",
                args_schema=TranslateInput,  # 定义参数的结构化输入
                return_direct=True  # 绕过Agent的结果处理，直接返回工具调用结果
            ),
            StructuredTool.from_function(
                func=lambda text, source_language, translated_language,style: literary_translate(
                    self.llm, text, source_language, translated_language,style
                ),
                name="LiteraryTranslator",
                description="适合小说、散文等文学作品的文学翻译（literary风格翻译）",
                args_schema=TranslateInput,  # 定义参数的结构化输入
                return_direct=True  # 绕过Agent的结果处理，直接返回工具调用结果
            )
        ]
        # 加载 Agent 的 Prompt（LangChain Hub 或自定义）
        self.agent_prompt = hub.pull("hwchase17/openai-tools-agent")

        # self.agent_prompt = ChatPromptTemplate.from_template("""
        # 请直接调用 {style} 翻译工具翻译以下文本，不要额外解释或验证：
        # 文本: {text}
        # 源语言: {source_language}
        # 目标语言: {translated_language}
        # """)

        # 创建 Agent
        self.agent = create_openai_tools_agent(
            llm=self.llm,
            tools=self.tools,
            prompt=self.agent_prompt
        )
        self.agent_executor = AgentExecutor(agent=self.agent,
                                            tools=self.tools,
                                            verbose=True,  # verbose=True 可用于调试，输出详细日志
                                            # max_iterations=1  # 限制只使用一次工具函数
                                            )

    async def translate(self, text: str, source_language: str, translated_language: str, style: str) -> str:
        """翻译工具入口方法，根据style选择不同的翻译工具"""
        response = await self.agent_executor.ainvoke({
            "input": {
                "text": text,
                "source_language": source_language,
                "translated_language": translated_language,
                "style": style  # 确保style参数显式传递
            },
            "return_intermediate_steps": True  # 启用中间步骤捕获，能直接获取工具调用结果
        })
        # 尝试获取工具调用结果
        if response.get("intermediate_steps"):
            return response["intermediate_steps"][-1][1]  # 最后一次工具调用的结果
        return response["output"]  # 回退到默认输出
