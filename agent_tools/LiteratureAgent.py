from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain.agents import initialize_agent, Tool
from langchain import hub
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from agent_tools.InputModels import TranslateInput, SummaryInput
from agent_tools.TranslationTools import general_translate, academic_translate
from agent_tools.SearchTools import search_tool, literature_search
from agent_tools.SummaryTools import summarize_literature
from langchain.tools import StructuredTool
from agent_tools.Prompts import PROMPT_AGENT_SYSTEM
from dotenv import load_dotenv

load_dotenv()


# 与agent交互的方法（异步）
# response = await self.agent_executor.ainvoke({"input": user_input})
# 与agent交互的方法（同步）
# response = self.agent_executor.invoke({"input": user_input})


class LiteratureAgent:
    def __init__(self):
        self.llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)
        self.tools = [
            StructuredTool.from_function(
                func=lambda text, source_language, translated_language, style: general_translate(
                    self.llm, text, source_language, translated_language, style
                ),
                name="GeneralTranslator",
                description="适合日常对话、非正式文本的流畅翻译（general风格翻译）",
                args_schema=TranslateInput,  # 定义参数的结构化输入
                return_direct=False  # 绕过Agent的结果处理，直接返回工具调用结果
            ),

            StructuredTool.from_function(
                func=lambda text, source_language, translated_language, style: academic_translate(
                    self.llm, text, source_language, translated_language, style
                ),
                name="AcademicTranslator",
                description="适合论文、技术文档等严谨场景的学术翻译（academic风格翻译）",
                args_schema=TranslateInput,  # 定义参数的结构化输入
                return_direct=False  # True:绕过Agent的结果处理，直接返回工具调用结果
            ),

            StructuredTool.from_function(
                func=lambda text, language, detail_level: summarize_literature(
                    self.llm, text, language, detail_level
                ),
                name="LiteratureSummarizer",
                description="学术文献总结工具，能够从文献内容中提取关键信息并生成结构化总结",
                args_schema=SummaryInput,
                return_direct=False
            ),
            literature_search,

        ]
        # self.agent_prompt = hub.pull("hwchase17/openai-tools-agent")
        # 加载 Agent 的 Prompt（LangChain Hub 或自定义）
        self.agent_prompt = ChatPromptTemplate.from_messages([
            ("system", PROMPT_AGENT_SYSTEM),  # 系统指令（固定）
            MessagesPlaceholder("chat_history", optional=True),  # 对话历史（动态）
            ("human", "{input}"),  # 当前用户输入（动态）
            MessagesPlaceholder("agent_scratchpad")  # Agent执行过程记录（自动填充）
        ])

        # 创建 Agent
        self.agent = create_openai_tools_agent(
            llm=self.llm,
            tools=self.tools,
            prompt=self.agent_prompt
        )
        self.agent_executor = AgentExecutor(agent=self.agent,
                                            tools=self.tools,
                                            verbose=True,  # verbose=True 可用于调试，输出详细日志
                                            # max_iterations=1,  # 限制只使用一次工具函数
                                            return_intermediate_steps=True  # 启用中间步骤捕获，能直接获取工具调用结果
                                            )

    async def translate(self, text: str, source_language: str, translated_language: str, style: str) -> str:
        """文献翻译入口方法，根据style选择不同的翻译工具"""
        response = await self.agent_executor.ainvoke({
            "input": {
                "text": text,
                "source_language": source_language,
                "translated_language": translated_language,
                "style": style  # 确保style参数显式传递
            }
        })

        # 提取最后一次工具调用的原始结果
        if response.get("intermediate_steps"):
            last_action, last_result = response["intermediate_steps"][-1]
            if last_action.tool == "GeneralTranslator" or last_action.tool == "AcademicTranslator":
                return last_result  # 直接返回翻译结果
        # 如果没有中间步骤或未调用工具，回退到默认输出
        return response["output"]

    async def summary(self, text: str, language: str, detail_level: str) -> str:
        """文献总结工具入口方法"""
        response = await self.agent_executor.ainvoke({
            "input": {
                "text": text,
                "language": language,
                "detail_level": detail_level  # 确保detail_level参数显式传递
            },
            "return_intermediate_steps": True  # 启用中间步骤捕获，能直接获取工具调用结果
        })

        # 提取最后一次工具调用的原始结果
        if response.get("intermediate_steps"):
            last_action, last_result = response["intermediate_steps"][-1]
            if last_action.tool == "LiteratureSummarizer":
                return last_result  # 直接返回文献总结结果
        # 如果没有中间步骤或未调用工具，回退到默认输出
        return response["output"]

    async def talk(self, user_input: str) -> str:
        """与Agent进行对话"""
        response = await self.agent_executor.ainvoke({
            "input": user_input,
        })
        # print("Response:", response)  # 打印完整的响应内容

        literature_summary=""
        # 如果是文献总结工具，记录工具返回结果
        if response.get("intermediate_steps"):
            for action,result in response["intermediate_steps"]:
                if action.tool== "LiteratureSummarizer":
                    literature_summary += str(result)
        # print("文献总结结果：", literature_summary)
        final_response = literature_summary+"\n\n" + response["output"]  # 将总结结果和最终输出合并
        # print("最终输出：",final_response)
        return final_response

    async def gain_all_tools_result(self, user_input: str) -> str:
        """与Agent进行对话，并返回所有工具调用的结果"""
        response = await self.agent_executor.ainvoke({
            "input": user_input
        })
        # print(response)
        # 收集所有工具调用的结果
        tool_results = []
        if response.get("intermediate_steps"):
            for action, observation in response["intermediate_steps"]:
                tool_name = action.tool
                tool_input = action.tool_input
                tool_output = observation  # 这是工具的直接返回结果
                tool_results.append(
                    f"🔧 工具调用: {tool_name}\n"
                    f"📌 输入参数: {tool_input}\n"
                    f"📢 返回结果: {tool_output}\n"
                    "----------------------------------------\n"
                )

        # 构建最终输出
        final_response = ""
        if tool_results:
            final_response += "=== 工具调用记录 ===\n" + "\n".join(tool_results) + "\n\n"
        final_response += "=== Agent 最终输出 ===\n" + response["output"]
        # print(final_response)
        return final_response
