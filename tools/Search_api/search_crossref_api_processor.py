import json
from typing import Dict, List, Any
import matplotlib.pyplot as plt
import pandas as pd


class LiteratureProcessor:
    def __init__(self, api_response: Dict):
        self.raw_data = api_response
        self.processed_items = []

    def _extract_basic_info(self, item: Dict) -> Dict:
        """提取文献基础信息
        Args:
            item: 从Crossref API获取的单个文献原始数据字典

        Returns:
            结构化后的文献信息字典，包含核心元数据
        """
        return {
            # 数字对象标识符(Digital Object Identifier)，文献的唯一标识
            "doi": item.get("DOI"),

            # 文献标题，get方法安全获取，默认空列表取第一个元素，避免KeyError
            "title": item.get("title", [""])[0],  # 取第一个标题

            # 作者列表，格式化每个作者为"名+姓"的字符串
            # 使用get安全获取author字段，默认空列表
            # strip()移除前后空格，避免空名/姓导致的格式问题
            "authors": [
                f"{author.get('given', '')} {author.get('family', '')}".strip()
                for author in item.get("author", [])
            ],

            # 出版物信息字典
            "publication": {
                # 期刊/会议名称，取container-title第一个值
                "journal": item.get("container-title", [""])[0],

                # 卷号(Volume)
                "volume": item.get("volume"),

                # 期号(Issue)
                "issue": item.get("issue"),

                # 页码范围(如"63-106")
                "pages": item.get("page"),

                # 出版商名称
                "publisher": item.get("publisher"),

                # 出版年份，从嵌套的date-parts中提取第一部分的第一个元素
                # 多层get避免嵌套KeyError，最终格式如2009
                "year": item.get("published", {}).get("date-parts", [[None]])[0][0]
            },

            # 文献的官方URL链接(通常是DOI解析链接)
            "url": item.get("URL"),

            # 清理后的摘要文本，移除HTML/JATS标签
            "abstract": self._clean_abstract(item.get("abstract")),

            # 被引用次数，默认0防止KeyError
            "citations": item.get("is-referenced-by-count", 0),

            # 参考文献数量，默认0防止KeyError
            "references": item.get("references-count", 0),

            # 文献语言，默认为英语
            "language": item.get("language", "en")
        }

    def _clean_abstract(self, abstract: str) -> str:
        """清理摘要中的HTML/JATS标签"""
        if not abstract:
            return ""
        # 简单去除常见标签（实际应用可能需要更复杂的处理）
        for tag in ["<jats:p>", "</jats:p>", "<p>", "</p>"]:
            abstract = abstract.replace(tag, "")
        return abstract.strip()

    def process(self) -> List[Dict]:
        """处理原始API响应"""
        if not self.raw_data.get("message", {}).get("items"):
            return []

        self.processed_items = [
            self._extract_basic_info(item) for item in self.raw_data["message"]["items"]
        ]
        return self.processed_items

    # # ----------------- 智能体功能支持方法 -----------------
    # def generate_translation_input(self) -> List[Dict]:
    #     """生成待翻译内容结构（标题+摘要）"""
    #     return [{
    #         "doi": item["doi"],
    #         "title": item["title"],
    #         "abstract": item["abstract"]
    #     } for item in self.processed_items]
    #
    # def get_statistics(self) -> Dict:
    #     """生成文献统计信息"""
    #     if not self.processed_items:
    #         return {}
    #
    #     df = pd.DataFrame(self.processed_items)
    #     return {
    #         "total_papers": len(df),
    #         "year_distribution": df["publication"].apply(lambda x: x["year"]).value_counts().to_dict(),
    #         "citation_stats": {
    #             "mean": df["citations"].mean(),
    #             "max": df["citations"].max(),
    #             "min": df["citations"].min()
    #         },
    #         "top_journals": df["publication"].apply(lambda x: x["journal"]).value_counts().head(5).to_dict()
    #     }
    #
    # def visualize_statistics(self):
    #     """可视化统计结果"""
    #     stats = self.get_statistics()
    #     if not stats:
    #         return
    #
    #     # 年份分布图
    #     plt.figure(figsize=(12, 5))
    #     pd.Series(stats["year_distribution"]).sort_index().plot(kind="bar")
    #     plt.title("Publication Year Distribution")
    #     plt.show()
    #
    #     # 期刊分布图
    #     pd.Series(stats["top_journals"]).plot(kind="pie", autopct="%1.1f%%")
    #     plt.title("Top 5 Journals")
    #     plt.show()
    #
    # def format_for_agent(self) -> List[Dict]:
    #     """生成智能体所需的标准化格式"""
    #     return [{
    #         "source": "Crossref",
    #         "metadata": item,
    #         "content": f"Title: {item['title']}\nAuthors: {', '.join(item['authors'])}\nAbstract: {item['abstract']}",
    #         "citations": item["citations"]
    #     } for item in self.processed_items]