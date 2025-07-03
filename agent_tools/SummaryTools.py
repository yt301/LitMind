from langchain_core.prompts import ChatPromptTemplate
from agent_tools.Prompts import PROMPT_SUMMARY
from langchain_core.output_parsers import StrOutputParser
from agent_tools.InputModels import SummaryInput
from langchain.tools import StructuredTool,tool

def summarize_literature(llm, text: str, language: str = "Chinese", detail_level: str = "medium") -> str:
    """学术文献总结工具"""
    prompt = ChatPromptTemplate.from_messages([
        ("system", PROMPT_SUMMARY),
        ("human", "请总结以下文献内容，使用{language}输出，详细程度为{detail_level}:\n\n{text}")
    ])

    chain = prompt | llm | StrOutputParser()
    response = chain.invoke({
        "text": text,
        "language": language,
        "detail_level": detail_level
    })
    return response
