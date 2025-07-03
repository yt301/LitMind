import asyncio
from SummaryChatBot import SummaryChatBot

async def main():
    chatbot = SummaryChatBot()
    # 测试文献总结
    text = "在这项研究中，我们探讨了多元回归模型在预测经济增长中的应用。通过分析过去十年的数据，我们发现模型能够有效地捕捉到经济增长的趋势和波动。"
    user_input = {
        "text": text,
        "language": "Chinese",
        "detail_level": "high"
    }
    response = await chatbot.summary(**user_input)
    print(response)
    print(response["text"])  # 输出总结的文本内容


# 运行异步函数
asyncio.run(main())
