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
