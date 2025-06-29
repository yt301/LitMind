from langchain.agents import tool, create_openai_tools_agent, AgentExecutor, Tool
from langchain_openai import ChatOpenAI
from langchain import hub
from dotenv import load_dotenv

load_dotenv()

# 定义工具
@tool
def get_word_length(word: str) -> int:
    """计算单词的长度"""
    return len(word)

@tool
def add(tool_input: dict) -> int:
    """计算两个数的和"""
    a = tool_input["a"]
    b = tool_input["b"]
    return a + b

math_tool = Tool(
    name="MathTool",
    func=lambda x: eval(x),
    description="计算数学表达式"
)

add_tool = Tool(name="AddTool", func=add, description="加法计算")
# 初始化 LLM 和 Agent
llm = ChatOpenAI(model="gpt-3.5-turbo")
tools = [get_word_length, math_tool,add_tool]
agent_prompt = hub.pull("hwchase17/openai-tools-agent")
agent = create_openai_tools_agent(llm, tools, agent_prompt)
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

# 运行 Agent
result = agent_executor.invoke({"input": "计算 'hello' 的长度加上 5 的平方"})
print(result["output"])  # 输出: 30 (5 + 25)