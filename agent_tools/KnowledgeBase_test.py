# from AcademicKnowledgeBase import AcademicKnowledgeBase
from agent_tools.AcademicKnowledgeBase_FAISS import AcademicKnowledgeBase

def knowledge_base_test():
    # 初始化知识库 - 这会自动加载或创建向量库
    kb = AcademicKnowledgeBase()

    # 测试检索功能
    query = "p值"  # 使用与你PDF内容相关的查询词
    results = kb.retrieve_relevant_info(query, k=1)

    print("\n检索结果:")
    for i, result in enumerate(results, 1):
        print(f"\n结果 {i}:")
        print(result)


if __name__ == "__main__":
    knowledge_base_test()