from fastapi import APIRouter, Depends
from tools import *
from models import *
from .auth import get_current_user
from fastapi.responses import FileResponse  # 用于下载文件
from fastapi.responses import RedirectResponse
# 文献搜索相关的路由
search = APIRouter()


# 搜索文献记录
@search.post("/crossref")
async def crossref_api_search(search_in: SearchIn):
    response = await search_crossref(**search_in.model_dump())  # 调用异步函数，需要await
    if "error" in response.values():  # Crossref API请求出错
        return response
    return create_response("success", 200, process_response(response))


# 根据doi查找对应文献
@search.post("/doi")
async def doi_search(doi_in: DOIIn):
    search_in = SearchIn(query="", rows=1, offset=0, filter=f"doi:{doi_in.doi}")
    response = await search_crossref(**search_in.model_dump())  # 调用异步函数，需要await
    if "error" in response.values():  # Crossref API请求出错
        return response
    response = process_response(response)
    if not response:
        return create_response("error", 404, "该doi不存在！")
    return create_response("success", 200, response)

# 根据url获取文献pdf_url
@search.get("/pdf_url")
async def get_pdf_url(url: str):
    response = await search_gain_pdf(url)
    return response

# 根据url获取文献xml_url
@search.get("/xml_url")
async def get_xml_url(url: str):
    response = await search_gain_xml(url)
    return response

