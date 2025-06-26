import requests
from xml.etree import ElementTree as ET


def search_arxiv(query, max_results=5):
    url = f"http://export.arxiv.org/api/query?search_query=all:{query}&start=0&max_results={max_results}"
    response = requests.get(url)
    root = ET.fromstring(response.text)

    papers = []
    for entry in root.findall("{http://www.w3.org/2005/Atom}entry"):
        paper = {
            "title": entry.find("{http://www.w3.org/2005/Atom}title").text.strip(),
            "authors": [a.find("{http://www.w3.org/2005/Atom}name").text
                        for a in entry.findall("{http://www.w3.org/2005/Atom}author")],
            "abstract": entry.find("{http://www.w3.org/2005/Atom}summary").text.strip(),
            "pdf_url": None,
            "published": entry.find("{http://www.w3.org/2005/Atom}published").text
        }
        # 提取PDF链接（需从<link>标签中解析）
        for link in entry.findall("{http://www.w3.org/2005/Atom}link"):
            if link.attrib.get("title") == "pdf":
                paper["pdf_url"] = link.attrib["href"]
        papers.append(paper)
    return papers


# 示例：搜索"quantum machine learning"
results = search_arxiv("math")
for paper in results:
    print(f"Title: {paper['title']}\nPDF: {paper['pdf_url']}\n")