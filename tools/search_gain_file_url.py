import requests
from fake_useragent import UserAgent
from tools.create_response import create_response
import asyncio
import re


# 1.获取pdf_url
async def search_gain_pdf(url):
    headers = {
        'User-Agent': UserAgent().random,
    }
    # 代理ip
    proxies = {
        "http": "http://47.95.208.20:10986",  # 此代理ip可能失效，需要替换为可用的代理
    }

    try:
        response = requests.get(url, headers=headers, proxies=proxies)
        response.raise_for_status()  # 检查HTTP错误
        if response.encoding is None or response.encoding == 'ISO-8859-1':
            response.encoding = response.apparent_encoding or 'utf-8'
        html_content = response.text  # 请求得到的HTML 内容
        # 使用正则表达式匹配 citation_pdf_url
        match_pdf = re.search(
            r'<meta\s+name="citation_pdf_url"\s+content="([^"]+)"\s*/>',
            html_content
        )
        if match_pdf:
            pdf_url = match_pdf.group(1)
            return create_response("success",200,pdf_url)
        else:
            return create_response("error",404,f"未找到{url}的pdf_url")
    except requests.exceptions.RequestException as e:
        return create_response("error", 500, f"访问{url}出错: {e}")


# 2.获取xml_url
async def search_gain_xml(url):
    headers = {
        'User-Agent': UserAgent().random,
    }
    # 代理ip
    proxies = {
        "http": "http://47.95.208.20:10986",  # 此代理ip可能失效，需要替换为可用的代理
    }
    try:
        response = requests.get(url, headers=headers, proxies=proxies)
        response.raise_for_status()  # 检查HTTP错误
        if response.encoding is None or response.encoding == 'ISO-8859-1':
            response.encoding = response.apparent_encoding or 'utf-8'
        html_content = response.text  # 请求得到的HTML 内容
        # 使用正则表达式匹配 XML 链接
        match_xml = re.search(
            r"<a\s+href=['\"]([^'\"]+)['\"][^>]*>XML</a>",
            html_content
        )
        if match_xml:
            xml_url = match_xml.group(1)
            return create_response("success",200,"https:"+xml_url)
        else:
            return create_response("error", 404, f"未找到{url}的xml_url")
    except requests.exceptions.RequestException as e:
        return create_response("error", 500, f"访问{url}出错: {e}")



# url = "https://doi.org/10.12677/aam.2020.912249"
# url = "https://doi.org/10.12677/sa.2019.83056"
# url = "https://doi.org/10.12677/aam.2019.87143"
# url ="https://doi.org/10.1210/jcem.80.3.7883856"
# result1 = asyncio.run(search_gain_pdf(url))
# print(result1)
# result2 = asyncio.run(search_gain_xml(url))
# print(result2)
