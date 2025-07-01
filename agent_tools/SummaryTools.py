from langchain_core.prompts import ChatPromptTemplate
from agent_tools.Prompts import PROMPT_SUMMARIZE
from langchain_core.output_parsers import StrOutputParser
from agent_tools.InputModels import SummaryInput
from langchain.tools import StructuredTool


def summarize_literature(llm, text: str, language: str = "Chinese", detail_level: str = "standard") -> str:
    """学术文献总结工具"""
    prompt = ChatPromptTemplate.from_messages([
        ("system", PROMPT_SUMMARIZE),
        ("human", "请总结以下文献内容，使用{language}输出，详细程度为{detail_level}:\n\n{text}")
    ])

    chain = prompt | llm | StrOutputParser()
    response = chain.invoke({
        "text": text,
        "language": language,
        "detail_level": detail_level
    })
    return response
