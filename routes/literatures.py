from Demos.win32ts_logoff_disconnected import username
from fastapi import APIRouter, Depends
from tools import *
from models import *
from .auth import get_current_user

# 文献相关的路由
literatures = APIRouter()


# 查询指定用户的文献记录
@literatures.get("/{username}")
async def get_literatures(username: str, current_user: User = Depends(
    get_current_user)):  # 请求头中需带上Authorization:"Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ1c2VyMiIsImV4cCI6MTc1MDg1ODE5MH0.GCiVVzsv92MD38gNYbiOj-OYW6tDOnd41HBD5stOsGs"
    # 确保当前用户有权访问该用户的文献记录
    if current_user.username != username:
        return create_response("error", 403, "无权访问其他用户的文献记录！")
    # 查询该用户的文献记录
    literatures_data = await Literature.filter(users__username=username).values(
        "id", "title", "author", "publication_date", "doi", "url", "reference_count", "reference_doi"
    )
    if not literatures_data:
        return create_response("error", 404, "没有找到该用户的文献记录！")
    return create_response('success', 200, literatures_data)


# 添加指定用户的文献记录
@literatures.post("/{username}")
async def add_literatures(username: str, literature_in: LiteratureIn, current_user: User = Depends(get_current_user)):
    # 确保当前用户有权访问该用户的文献记录
    if current_user.username != username:
        return create_response("error", 403, "无权访问其他用户的文献记录！")
    literatures_existing = await Literature.filter(doi=literature_in.doi, users__username=username).first()
    if literatures_existing:
        return create_response("error", 409, "文献记录已存在！")
    else:
        # 创建文献记录
        literature = await Literature.create(
            title=literature_in.title,
            author=literature_in.author,
            publication_date=literature_in.publication_date,
            doi=literature_in.doi,
            url=literature_in.url,
            reference_count=literature_in.reference_count,
            reference_doi=literature_in.reference_doi
        )
        # 关联用户
        await literature.users.add(current_user)  # 将当前用户添加到文献记录的用户列表中
        return create_response("success", 200, literature)


# 更新指定用户的文献记录
@literatures.put("/{username}")
async def update_literatures(username: str, literature_in: LiteratureIn,
                             current_user: User = Depends(get_current_user)):
    # 确保当前用户有权访问该用户的文献记录
    if current_user.username != username:
        return create_response("error", 403, "无权访问其他用户的文献记录！")
    literatures_existing = await Literature.filter(doi=literature_in.doi, users__username=username).first()
    if not literatures_existing:
        return create_response("error", 404, "文献记录不存在！")
    if is_equal(literatures_existing, literature_in):
        return create_response("error", 400, "修改后的文献记录与原先一致！")
    # 更新文献记录
    await Literature.filter(doi=literature_in.doi, users__username=username).update(**literature_in.model_dump())
    return create_response("success", 200, literatures_existing)


# 删除文献记录
@literatures.delete("/{username}")
async def delete_literatures(username: str, doi_in: str, current_user: User = Depends(get_current_user)):
    # 确保当前用户有权访问该用户的文献记录
    if current_user.username != username:
        return create_response("error", 403, "无权访问其他用户的文献记录！")
    # 先查询符合条件的文献
    literatures_delete = await Literature.filter(doi=doi_in, users__username=username)
    if not literatures_delete:
        return create_response("error", 404, "文献记录不存在！")
    delete_count = await Literature.filter(doi=doi_in).delete()  # 删除文献记录
    return create_response("success",200,{"delete_count":delete_count})



# 搜索文献记录
@literatures.get("/search")
async def get_literatures():
    return {
        "message": "搜索文献",
        "data": [
            {"id": 1, "title": "文献1", "author": "作者1"},
            {"id": 2, "title": "文献2", "author": "作者2"}
        ]
    }
