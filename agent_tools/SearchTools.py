from tools import search_crossref,process_response
from langchain.tools import StructuredTool,tool
from agent_tools.InputModels import SearchInput

@tool("LiteratureSearch")  # 自动处理异步调用
async def literature_search(query: str, rows: int = 3, filter: str = None,sort:str="relevance") -> str:
    """学术文献检索工具，集成Crossref API"""
    try:
        raw_results = await search_crossref(query=query, rows=rows, filter=filter,sort=sort)
        if not raw_results or 'message' not in raw_results:
            return "未找到相关文献"

        processed = process_response(raw_results)
        if not processed:
            return "无符合条件的文献结果"

        # 完整格式化输出
        results = []
        for i, item in enumerate(processed):
            result_str = [
                f"{i + 1}. {item.get('title', '无标题')}",
                f"   作者: {item.get('author', '未知作者')}",
                f"   发表时间: {item.get('publication_date', '日期不详')}",
                f"   期刊/会议: {item.get('container_title', [''])[0] if item.get('container_title') else '未标注'}",
                f"   被引次数: {item.get('is_referenced_by_count', 0)}",
                f"   DOI: {item.get('doi', '无DOI')}",
                f"   原文链接: {item.get('url', '无可用链接')}",
                f"   参考文献数: {item.get('reference_count', 0)}"
            ]
            results.append("\n".join(result_str))

        # 添加统计信息
        total = raw_results['message'].get('total-results', len(processed))
        summary = f"\n\n=== 共找到 {min(len(processed), rows)}/{total} 篇文献 ==="

        return summary + "\n\n" + "\n\n".join(results)

    except Exception as e:
        return f"文献检索失败: {str(e)}"



# 创建 LangChain 兼容的工具实例
search_tool = StructuredTool.from_function(
    func=literature_search,
    name="LiteratureSearch",
    description="学术文献检索工具，支持从Crossref获取论文信息",
    args_schema=SearchInput,
    return_direct=False
)