import requests
from fake_useragent import UserAgent
# 输入关键字query
def search_crossref(query, rows=10, offset=0, filters=None, select_fields=None, sort=None, order=None):
    """
       搜索Crossref文献

       参数:
       query (str): 搜索关键词
       rows (int): 返回结果数量(1-1000，默认10)
       offset (int): 分页偏移量(默认0)
       filters (dict): 过滤条件字典
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
        "http": "http://47.95.208.20:10986",
    }
    # 基础参数
    params = {
        "query": query,  # 搜索关键词
        "rows": rows,    # 返回结果数
        "offset": offset, # 分页偏移
    }
    url = f"https://api.crossref.org/works"

    # 添加可选参数
    if filters:  # 筛选条件
        for key, value in filters.items():
            params[f"filter.{key}"] = value

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
        print(f"请求出错: {e}")
        return None

# 测试
# response=search_crossref(query='math')
# print(response["message"]["total-results"])
# print(response["message"]['items'][0]['URL'])
# for key in response["message"]['items'][0]:
#     print(f"key:{key}")
# print(response)