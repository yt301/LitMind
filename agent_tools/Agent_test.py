from LiteratureAgent import LiteratureAgent
import asyncio

summary_need_text = """请你帮我总结一下文献的内容：发病率呈现出逐年增高的趋势。根据国际糖尿病联盟(IDF)预测到2040年，中国糖尿病患者数量将达到1.51亿人，相比于2015年糖尿病患者数量增加近50%，因此控制并降低糖尿病的患病率十分必要 [1] ，中南大学谢玉秀 [2] 通过分析住院2型糖尿病患者各项数据，采用Logistic逐步回归分析筛选相关危险因素，得到对于2型糖尿病，不应只是单纯的控制血糖或追求其他单个指标的控制，而应该注重在降糖、降压、降脂方面的综合治疗；王珍 [3] 等人通过分析糖尿病患者3种不同的血糖状态在TG、胰岛素抵抗指数(HOMA-IR)、胰岛素分泌指数(HOMA-β)、血清总免疫球蛋白E(IgE)和C-RP的分布，得到结论HOMA-IR与HOMA-β是公认的糖尿病的危险因子，为糖尿病的治疗提供了理论方向；徐秀菊 [4] 通过对糖尿病患者进行药物注射治疗，比较其腹血糖、体重指数、糖化血红蛋白等各项指标，得到格列美脲与胰岛素联合使用医治2型糖尿病的效果明显，能够有效减少餐后2 h血糖含量、空腹血糖含量、糖化血红蛋白含量，降低胰岛素的使用量，对体重指数影响很小，值得在临床上推广应用；John Doupis [5] 等人提出二肽基肽酶-IV (DPP4)的抑制导致胰高血糖素样肽-1 (GLP-1)和胃抑制性多肽(GIP)的血液浓度增加，这导致胰岛素分泌的葡萄糖依赖性刺激增加，从而导致血糖水平降低，为糖尿病的治疗提供了高效性药物以及具有临床疗效的最新药物；Knowler WC [6] 等人通过比较注射metformin和改善生活方式下血液中葡萄糖浓度，得到生活方式的改变与metformin均能降低糖尿病发病率高危人群，但生活方式干预是比metformin更有效，为糖尿病患者提供除药物治疗外的其它不产生副作用的治疗方式；朱彩蓉 [7] 等人通过Markov状态转移决策树模型对新药罗格列酮钠治疗糖尿病的长期效果进行评价，发现Markov状态转移决策树模型是评价药物治疗长期效果的有效模型，为糖尿病的药物治疗效果提供模型支持。"""


async def main():
    agent = LiteratureAgent()

    # 一、不带记忆的函数方法测试
    # 1.测试与Agent交互
    # （1）测试翻译工具
    # user_input = "请你翻译：我的呼吸在灯光的波纹里，遥遥地望着村庄边畔的断崖，断崖仍然在它的世界里。断崖的形象在我的意念里。我为它在我的思维里安排了一个位置，支撑起我的信念，滤得我的目光越来越纯净。"
    # （2）测试文献搜索工具
    # user_input = "请你帮我找2个2021年之前的有关多元回归模型的文献。"
    # （3）测试文献内容总结工具
    # user_input= summary_need_text
    # response = await agent.agent_executor.ainvoke({"input": user_input,"urn_intermediate_steps": True})# 启用中间步骤捕获，能直接获取工具调用结果
    # print(response)

    # 2.测试通用翻译工具
    # general_translation= await agent.agent_executor.ainvoke({
    #     "input":"请你用通用风格翻译工具翻译如下文本，从中文到英文：我的呼吸在灯光的波纹里，遥遥地望着村庄边畔的断崖，断崖仍然在它的世界里。断崖的形象在我的意念里。我为它在我的思维里安排了一个位置，支撑起我的信念，滤得我的目光越来越纯净。",
    # })
    # print(general_translation)

    # 3.测试翻译工具入口方法函数
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

    # 4.测试文献总结工具入口方法函数
    # summary = await agent.summary(
    #     text=summary_need_text,
    #     language="Chinese",
    #     detail_level="high"
    # )
    # print("文献总结内容：", summary)  # 输出总结的文本内容

    # 5.测试与Agent对话
    # response = await agent.talk(user_input)
    # print("与Agent对话的响应：", response)  # 输出与Agent对话的响应内容

    # 二、带记忆的函数方法测试
    # 1.测试与Agent对话
    response = await agent.talk_with_memory(
        session_id="1",  # 使用唯一的会话ID来维持对话历史
        user_input="hello？"
    )
    # print("与带记忆的Agent对话的响应：", response)  # 输出与Agent对话的响应内容
    # 2，测试清除对话历史
    # await agent.clear_history(session_id="1")
    # print("对话历史已清除。")

# 运行异步函数
asyncio.run(main())
