from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain.agents import initialize_agent, Tool
from langchain import hub
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
from langchain.agents import tool
from models_in import TranslateInput
from TranslationTools import general_translate
from langchain.tools import StructuredTool

load_dotenv()

# 与agent交互的方法
# response = await self.agent_executor.ainvoke("input": {user_input})


class TranslationAgent:
    def __init__(self):
        self.llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)
        self.tools = [
            StructuredTool.from_function(
                func=lambda text, source_language, translated_language: general_translate(
                    self.llm, text, source_language, translated_language
                ),
                name="GeneralTranslator",
                description="适合日常对话、非正式文本的流畅翻译",
                args_schema=TranslateInput  # 定义参数的结构化输入
            )
        ]
        # 加载 Agent 的 Prompt（LangChain Hub 或自定义）
        self.agent_prompt = hub.pull("hwchase17/openai-tools-agent")

        # 创建 Agent
        self.agent = create_openai_tools_agent(
            llm=self.llm,
            tools=self.tools,
            prompt=self.agent_prompt
        )
        self.agent_executor = AgentExecutor(agent=self.agent, tools=self.tools, verbose=True)  # verbose=True 可用于调试，输出详细日志

    async def run(self, input_text: str, source_language: str, translated_language: str) -> str:
        """Agent 执行入口"""
        response = await self.agent_executor.ainvoke({
            "input": {
                "text": input_text,
                "source_language": source_language,
                "translated_language": translated_language
            }
        })
        return response["output"]
