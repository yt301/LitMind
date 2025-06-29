# 方式 1：通过字典传递参数
def add(tool_input: dict) -> int:
    a = tool_input["a"]
    b = tool_input["b"]
    return a + b

tool = Tool(name="AddTool", func=add, description="加法计算")