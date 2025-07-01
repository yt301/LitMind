from LiteratureAgent import LiteratureAgent
import asyncio


async def main():
    agent = LiteratureAgent()

    # 测试与Agent交互
    # user_input = "请你翻译：我的呼吸在灯光的波纹里，遥遥地望着村庄边畔的断崖，断崖仍然在它的世界里。断崖的形象在我的意念里。我为它在我的思维里安排了一个位置，支撑起我的信念，滤得我的目光越来越纯净。"
    user_input = "请你帮我找2个2021年之前的有关多元回归模型的文献。"
    response = await agent.agent_executor.ainvoke({"input": user_input})
    print(response["output"])


    # # 测试通用翻译工具
    # general_translation= await agent.agent_executor.ainvoke({
    #     "input":"请你用通用风格翻译工具翻译如下文本，从中文到英文：我的呼吸在灯光的波纹里，遥遥地望着村庄边畔的断崖，断崖仍然在它的世界里。断崖的形象在我的意念里。我为它在我的思维里安排了一个位置，支撑起我的信念，滤得我的目光越来越纯净。",
    # })
    # print(general_translation)

    # 测试翻译工具入口方法函数
    # general_translation = await agent.translate(
    #     text="p值",
    #     source_language="Chinese",
    #     translated_language="English",
    #     style="academic"
    # )
    # print("翻译内容：", general_translation)

    # academic_translation = await agent.translate(
    #     text="纳米复合材料",
    #     source_language="Chinese",
    #     translated_language="English",
    #     style="academic"
    # )
    # print("翻译内容：",academic_translation)



# 运行异步函数
asyncio.run(main())
