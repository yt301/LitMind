from TranslationAgent import TranslationAgent
import asyncio

async def main():
    agent = TranslationAgent()
    # 添加 await 关键字
    result = await agent.run("你好", "Chinese", "English")  # 注意这里的await
    print("翻译结果:", result)

# 运行异步函数
asyncio.run(main())

