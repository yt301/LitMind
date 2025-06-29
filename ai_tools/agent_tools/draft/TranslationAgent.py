from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain.tools import StructuredTool
from langchain import hub
from langchain_openai import ChatOpenAI
from TranslationTools import general_translate,text_length_counter
from dotenv import load_dotenv
from models_in import TranslateInput, TextLengthInput

load_dotenv()


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
                args_schema=TranslateInput,
                return_direct=True  # 关键修改！绕过Agent的结果处理，直接返回工具调用结果
            ),
             # 新增长度统计工具
            StructuredTool.from_function(
            func=text_length_counter,
            name="TextLengthCounter",
            description="统计文本的字符长度（包含空格）",
            args_schema=TextLengthInput,  # 简单工具可不定义schema
            return_direct=True  # 关键修改！绕过Agent的结果处理
            )

        ]

        # 加载 Agent 的 Prompt
        self.agent_prompt = hub.pull("hwchase17/openai-tools-agent")

        # 创建 Agent
        self.agent = create_openai_tools_agent(
            llm=self.llm,
            tools=self.tools,
            prompt=self.agent_prompt
        )
        self.agent_executor = AgentExecutor(agent=self.agent, tools=self.tools, verbose=False)

    async def run(self, input_text: str, source_language: str, translated_language: str) -> str:
        """Agent 执行入口"""
        response = await self.agent_executor.ainvoke({
            "input": {
                "text": input_text,
                "source_language": source_language,
                "translated_language": translated_language
            },
            # 关键配置：要求 Agent 返回执行过程中的中间步骤（包括工具调用记录）
            "return_intermediate_steps": True
        })
        # 提取工具原始输出
        if response.get("intermediate_steps"):  # 检查是否存在中间步骤
            last_step = response["intermediate_steps"][-1]  # 获取最后一次工具调用
            return last_step[1]  # 提取工具的原始输出
        return response["output"]