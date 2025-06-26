import requests
from fake_useragent import UserAgent
from .create_response import create_response

# 1.Crossref API 文献搜索工具
async def search_crossref(query, rows=10, offset=0, filter=None, select_fields=None, sort=None, order=None):
    """
       搜索Crossref文献

       参数:
       query (str): 搜索关键词
       rows (int): 返回结果数量(1-1000，默认10)
       offset (int): 分页偏移量(默认0)
       filter (str): 过滤条件字符串(格式如"from-pub-date:2023,type:journal-article")
       select_fields (list): 选择返回的字段列表
       sort (str): 排序字段(如"published", "score", "updated")
       order (str): 排序顺序("asc"或"desc")

       返回:
       dict: Crossref API的JSON响应
    """
    headers = {
        'User-Agent': UserAgent().random,
        'Accept': 'application/json',
    }
    # 代理ip
    proxies = {
        "http": "http://47.95.208.20:10986",  # 此代理ip可能失效，需要替换为可用的代理
    }
    # 基础参数
    params = {
        "query": query,  # 搜索关键词
        "rows": rows,    # 返回结果数
        "offset": offset, # 分页偏移
    }
    url = f"https://api.crossref.org/works"

    # 添加可选参数
    if filter:  # 筛选条件
        params["filter"] = filter

    if select_fields:
        params["select"] = ",".join(select_fields)
    if sort:
        params["sort"] = sort
    if order:
        params["order"] = order
    try:
        response = requests.get(url, headers=headers, params=params, proxies=proxies)
        response.raise_for_status()  # 检查HTTP错误
        return response.json()
    except requests.exceptions.RequestException as e:
        return create_response("error", 500, f"Crossref API请求出错: {e}")

# 2. Crossref API Processor 响应数据处理器
def process_response(response):
    result = []
    for item in response['message']['items']:
        # 处理作者信息
        authors = item.get('author', [])
        author_names = []
        for author in authors:
            given_name = author.get('given', '')
            family_name = author.get('family', '')
            author_name = f"{family_name}{given_name}"
            author_names.append(author_name)
        author_str = ", ".join(author_names) if author_names else ""

        # 处理出版日期
        issued_date = item.get('issued', {}).get('date-parts', [[None]])[0]
        if issued_date and len(issued_date) >= 3:
            publication_date = f"{issued_date[0]}-{issued_date[1]:02d}-{issued_date[2]:02d}"
        elif issued_date and len(issued_date) >= 1:
            publication_date = f"{issued_date[0]}-01-01"  # 只有年份时默认1月1日
        else:
            publication_date = ""

        # 处理参考文献DOI
        reference_dois = []
        for ref in item.get('reference', []):
            if 'DOI' in ref:
                reference_dois.append(ref['DOI'])
            elif 'doi-asserted-by' in ref and 'DOI' in ref:
                reference_dois.append(ref['DOI'])

        # 构建结果字典
        literature = {
            "publication_date": publication_date,
            "author": author_str,
            "url": item.get('URL', '').strip(),
            "reference_doi": reference_dois,
            "doi": item.get('DOI', ''),
            "reference_count": item.get('reference-count', 0),
            "title": item.get('title', [''])[0], # 取标题列表中的第一个
            "is_referenced_by_count": item.get('is-referenced-by-count', 0),  # 被引用次数
            "score": item.get('score', 0)  # Crossref评分
        }
        result.append(literature)

    return result


# 1.测试Crossref API
# response=search_crossref(query='多元回归分析', rows=2)
# print(response["message"]["total-results"])
# print(response["message"]['items'][0]['URL'])
# for key in response["message"]['items'][0]:
#     print(f"key:{key}")
# print(response)

# 2.测试Crossref API Processor
# response = search_crossref(query='多元回归分析', rows=2)
# print(response)
# print("-"*50)
# print(process_response(response))
