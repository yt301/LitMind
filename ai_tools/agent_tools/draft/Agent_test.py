from TranslationAgent import TranslationAgent
import asyncio


# Agent_test.py (修改测试代码)
async def main():
    agent = TranslationAgent()

    # 测试翻译工具
    translation = await agent.run("你好", "Chinese", "English")
    print(f"翻译结果: {translation}")

    # 测试长度统计工具
    length = await agent.agent_executor.ainvoke({
        "input": {
            "text": "Hello world"  # 注意参数名需与工具定义一致
        }
    })
    print(f"文本长度: {length['output']}")


    translation_length = await agent.agent_executor.ainvoke({
        "input": "这句话有几个字：你是猪吗？",
    })
    print(translation_length)


    #测试长度统计工具（修改后）
    # length_response = await agent.agent_executor.ainvoke({
    #     "input": {"text": "Hello world"},
    #     "return_intermediate_steps": True  # 同样启用中间步骤捕获
    # })
    #
    # if length_response.get("intermediate_steps"):
    #     raw_length = length_response["intermediate_steps"][-1][1]
    #     print(f"文本长度（原始结果）: {raw_length}")  # 输出: 11
    # else:
    #     print(f"文本长度（默认输出）: {length_response['output']}")

if __name__ == "__main__":
    asyncio.run(main())