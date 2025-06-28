from fastapi import APIRouter, Depends
from tools import *
from models import *
from .auth import get_current_user

# 文献搜索相关的路由
search = APIRouter()


# 搜索文献记录
@search.post("/crossref")
async def crossref_api_search(search_in: SearchIn, current_user: User = Depends(get_current_user)):
    response = await search_crossref(**search_in.model_dump())  # 调用异步函数，需要await
    if "error" in response.values():  # Crossref API请求出错
        return response
    return create_response("success", 200, process_response(response))


# 根据doi查找对应文献
@search.get("/crossref")
async def get(doi_in: DOIIn, current_user: User = Depends(get_current_user)):
    search_in = SearchIn(query="", rows=1, offset=0, filter=f"doi:{doi_in.doi}")
    response = await search_crossref(**search_in.model_dump())  # 调用异步函数，需要await
    if "error" in response.values():  # Crossref API请求出错
        return response
    response = process_response(response)
    if not response:
        return create_response("error", 404, "该doi不存在！")
    return create_response("success", 200, response)
