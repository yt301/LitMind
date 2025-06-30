from agent_tools.TranslationAgent import TranslationAgent
import asyncio


async def main():
    agent = TranslationAgent()

    # # 测试通用翻译工具
    # general_translation= await agent.agent_executor.ainvoke({
    #     "input":"请你用通用风格翻译工具翻译如下文本，从中文到英文：我的呼吸在灯光的波纹里，遥遥地望着村庄边畔的断崖，断崖仍然在它的世界里。断崖的形象在我的意念里。我为它在我的思维里安排了一个位置，支撑起我的信念，滤得我的目光越来越纯净。",
    # })
    # print(general_translation)
    #
    # # 测试学术翻译工具
    # academic_translation= await agent.agent_executor.ainvoke({
    #     "input":"请你用学术风格翻译工具翻译如下文本，从中文到英文：我的呼吸在灯光的波纹里，遥遥地望着村庄边畔的断崖，断崖仍然在它的世界里。断崖的形象在我的意念里。我为它在我的思维里安排了一个位置，支撑起我的信念，滤得我的目光越来越纯净。",
    # })
    # print(academic_translation)
    #
    # # 测试文学翻译工具
    # literary_translation = await agent.agent_executor.ainvoke({
    #     "input": "请你用文学风格翻译工具翻译如下文本，从中文到英文：我的呼吸在灯光的波纹里，遥遥地望着村庄边畔的断崖，断崖仍然在它的世界里。断崖的形象在我的意念里。我为它在我的思维里安排了一个位置，支撑起我的信念，滤得我的目光越来越纯净。",
    # })
    # print(literary_translation)

    # 测试翻译工具入口方法函数
    general_translation = await agent.translate(
        text="纳米复合材料",
        source_language="Chinese",
        translated_language="English",
        style="general"
    )
    print("翻译内容：", general_translation)

    # academic_translation = await agent.translate(
    #     text="纳米复合材料",
    #     source_language="Chinese",
    #     translated_language="English",
    #     style="academic"
    # )
    # print("翻译内容：",academic_translation)

    # literary_translation = await agent.translate(
    #     text="Most of us compare ourselves with anyone we think is happier — a relative, someone we know a lot, or someone we hardly know. As a result, what we do remember is anything that makes others happy, anything that makes ourselves unhappy, totally forgetting that there is something happy in our own life.",
    #     source_language="English",
    #     translated_language="Chinese",
    #     style="literary"
    # )
    # print("翻译内容：",literary_translation)


# 运行异步函数
asyncio.run(main())
