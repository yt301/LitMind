from langchain.memory import ConversationSummaryBufferMemory
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_community.chat_message_histories import FileChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.runnables.config import RunnableConfig
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
from config import AGENT_MEMORY_DIR
from pathlib import Path
import os
from typing import cast
import tiktoken

from dotenv import load_dotenv

load_dotenv()

# 初始化编码器（GPT-3.5/4的编码）
GLOBAL_ENCODER = tiktoken.get_encoding("cl100k_base")


# 重写FileChatMessageHistory的messages 属性：只取最后5条消息用于后续处理，同时限制最大token数
class LimitedHistory(FileChatMessageHistory):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.encoder = GLOBAL_ENCODER  # 引用编码器

    @property
    def messages(self):
        messages = super().messages  # 获取完整的对话历史（从父类FileChatMessageHistory）
        limited_messages = []
        total_tokens = 0
        max_tokens = 1500  # 建议值：可根据你的模型调整

        # 从最新消息开始反向遍历（优先保留最近的消息）
        for msg in reversed(messages):
            msg_tokens = len(self.encoder.encode(msg.content))  # 精确计算当前消息的token数
            # msg_tokens = len(msg.content) // 4  # 简单token估算（精确版需调用tiktoken）
            if total_tokens + msg_tokens > max_tokens:
                break
            limited_messages.append(msg)
            total_tokens += msg_tokens
            if len(limited_messages) >= 5:  # 硬性条数限制
                break

        return list(reversed(limited_messages))  # 恢复时间顺序


class LiteratureAgent:
    def __init__(self):
        self.llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0, max_tokens=2000)  # 初始化LLM，设置温度和最大token数
        self.encoder = GLOBAL_ENCODER  # 引用编码器
        self._setup_memory()  # 新增记忆初始化
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
            ("system", "{history_summary}"),  # 新增对话历史总结摘要
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
        # 创建不带记忆的Agent执行器
        self.agent_executor = AgentExecutor(agent=self.agent,
                                            tools=self.tools,
                                            verbose=True,  # verbose=True 可用于调试，输出详细日志
                                            # max_iterations=1,  # 限制只使用一次工具函数
                                            return_intermediate_steps=True  # 启用中间步骤捕获，能直接获取工具调用结果
                                            )
        # 创建带记忆的Agent执行器（RunnableWithMessageHistory+FileChatMessageHistory）
        self.agent_memory_executor = RunnableWithMessageHistory(
            AgentExecutor(
                agent=self.agent,
                tools=self.tools,
                verbose=True,
                return_intermediate_steps=True
            ),
            self._get_message_history,  # 记忆获取方法，获取原始对话记录
            input_messages_key="input",
            history_messages_key="chat_history",
        )

    def _setup_memory(self):
        """初始化记忆存储目录"""
        self.MEMORY_DIR = Path(AGENT_MEMORY_DIR)
        self.MEMORY_DIR.mkdir(exist_ok=True)

    def _get_message_history(self, session_id: str):
        """获取指定会话的记忆"""
        if not session_id:
            raise ValueError("session_id不能为空")

        file_path = self.MEMORY_DIR / f"{session_id}.json"
        # 直接返回最后10条消息
        return LimitedHistory(str(file_path))
        # return FileChatMessageHistory(str(file_path))

        # return ConversationSummaryBufferMemory(
        #     llm=self.llm,
        #     max_token_limit=1000,  # 根据模型调整
        #     chat_memory=FileChatMessageHistory(str(file_path)),
        #     memory_key="chat_history",
        #     return_messages=True
        # )

    def _get_summary_memory(self, session_id: str):
        """始化摘要记忆"""
        file_path = self.MEMORY_DIR / f"{session_id}.json"
        return ConversationSummaryBufferMemory(
            llm=self.llm,
            max_token_limit=1000,  # 最多保留的token数量，根据模型调整
            chat_memory=FileChatMessageHistory(str(file_path)),
            memory_key="chat_history",
            return_messages=True
        )

    def _count_tokens(self, text: str) -> int:
        """使用tiktoken精确计算文本的token数"""
        return len(self.encoder.encode(text))

    def _truncate_by_tokens(self, text: str, max_tokens: int) -> str:
        """按token数精确截断文本，避免截断半个单词或乱码
        Args:
            text: 原始文本
            max_tokens: 允许的最大token数
        Returns:
            截断后的文本（token数 ≤ max_tokens）
        """
        tokens = self.encoder.encode(text)  # 使用类中已有的encoder（tiktoken）
        if len(tokens) <= max_tokens:
            return text
        return self.encoder.decode(tokens[:max_tokens])  # 只保留前max_tokens个token

    # 不带记忆的函数方法

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

        literature_summary = ""
        # 如果是文献总结工具，记录工具返回结果
        if response.get("intermediate_steps"):
            for action, result in response["intermediate_steps"]:
                if action.tool == "LiteratureSummarizer":
                    literature_summary += str(result)
        # print("文献总结结果：", literature_summary)
        final_response = literature_summary + "\n\n" + response["output"]  # 将总结结果和最终输出合并
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

    # 带记忆的函数方法
    async def talk_with_memory(self, user_input: str, session_id: str, file_paths: list[str] = None) -> str:
        """与Agent进行对话（新增session_id参数）"""
        # 用户输入的token验证
        input_tokens = self._count_tokens(user_input)
        input_limited_tokens = 3000  # 用户输入限制的最大token数
        if input_tokens > input_limited_tokens:
            raise ValueError(
                f"输入内容过长（{input_tokens} tokens）。"
                f"请将内容缩短至1500 tokens以内（约{input_limited_tokens * 0.8}个英文单词或{input_limited_tokens //1.5 }个中文字）。"
            )

        # 处理文件内容（使用现有的read_file_content函数）
        file_contents = []
        total_file_tokens = 0
        file_limited_tokens = 3000  # 文件内容限制的最大token数

        if file_paths:
            for file_path in file_paths:
                try:
                    from tools.translations_tools import read_file_content
                    content = read_file_content(file_path)
                    content_tokens = self._count_tokens(content)

                    # 截断超限内容
                    remaining_tokens = file_limited_tokens - total_file_tokens
                    if content_tokens > remaining_tokens:
                        content = self._truncate_by_tokens(content, remaining_tokens)
                        # print(f"文件 {os.path.basename(file_path)} 内容超出限制，已截断")

                    file_contents.append(f"文件内容({os.path.basename(file_path)}):\n{content}")
                    total_file_tokens += self._count_tokens(content)

                    if total_file_tokens >= file_limited_tokens:
                        # print(f"文件内容已达token上限（{file_limited_tokens}）")
                        break

                except Exception as e:
                    print(f"读取文件 {file_path} 失败: {str(e)}")


        # 构建完整输入
        full_input = user_input
        if file_contents:
            full_input += "\n\n=== 附加文件内容 ===\n" + "\n\n".join(file_contents)

        # 以下实现对话
        config = RunnableConfig(configurable={"session_id": session_id})  # 使用正确的配置类型（用session_id确定对话）
        memory = self._get_summary_memory(session_id)

        history_summary = memory.moving_summary_buffer  # 获取历史摘要
        # print("历史摘要：", history_summary)  # 打印历史摘要内容，便于调试
        response = await self.agent_memory_executor.ainvoke(
            {
                "input": full_input,
                "history_summary": history_summary  # 将历史摘要传入
            },
            config=config  # 传入正确类型的配置
        )
        # print("Response:", response)  # 打印完整的响应内容
        return response["output"]
        # literature_summary=""
        # # 如果是文献总结工具，记录工具返回结果
        # if response.get("intermediate_steps"):
        #     for action,result in response["intermediate_steps"]:
        #         if action.tool== "LiteratureSummarizer":
        #             literature_summary += str(result)
        # # print("文献总结结果：", literature_summary)
        # final_response = literature_summary+"\n\n" + response["output"]  # 将总结结果和最终输出合并
        # # print("最终输出：",final_response)
        # return final_response

    async def clear_history(self, session_id: str):
        """清除指定 session 的历史对话"""
        file_path = self.MEMORY_DIR / f"{session_id}.json"
        if file_path.exists():
            os.remove(file_path)
