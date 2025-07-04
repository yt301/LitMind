from fastapi import APIRouter, Depends
from tools import *
from models import *
from .auth import get_current_user

# 文献记录管理相关的路由
literatures = APIRouter()
theme_selector = ThemeSelector()  # 实例化主题选择器

# 请求文献接口时，请求头中必须带上Authorization:"Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ1c2VyMiIsImV4cCI6MTc1MDg1ODE5MH0.GCiVVzsv92MD38gNYbiOj-OYW6tDOnd41HBD5stOsGs"

# 查询指定用户的文献记录
@literatures.get("/")
async def get_literatures(current_user: User = Depends(
    get_current_user)):
    # 通过中间表查询用户关联的文献id
    literature_ids = await LiteratureUser.filter(
        user_id=current_user.id
    ).values_list("literature_id", flat=True)
    # 查询该用户的文献记录
    literatures_data = await Literature.filter(
        id__in=literature_ids
    ).values(
        "id", "title", "author", "publication_date", "doi", "url",
        "reference_count", "reference_doi", "is_referenced_by_count",
        "score", "theme_auto"
    )
    if not literatures_data:
        return create_response("error", 404, "没有找到该用户的文献记录！")
    return create_response('success', 200, literatures_data)


# 添加指定用户的文献记录
@literatures.post("/")
async def add_literatures(literature_in: LiteratureIn, current_user: User = Depends(get_current_user)):
    literatures_existing = await Literature.filter(doi=literature_in.doi).first()
    if literatures_existing:
        # 检查当前用户是否已关联该文献
        is_associated = await LiteratureUser.filter(literature_id=literatures_existing.id,user_id=current_user.id).exists()
        if is_associated:
            return create_response("error", 409, "文献记录已存在！")
        else:
            # 关联当前用户到该文献
            await LiteratureUser.create(
                literature=literatures_existing,  # 外键可直接填实例对象
                user=current_user,
                theme_tags=[]
            )
            return create_response("success", 200, "由于文献记录存在，故将已存在文献记录关联此用户！")
    else:
        theme = await theme_selector.choose_theme("{title:"+f"{literature_in.title}"+"}")
        # 创建文献记录
        literature = await Literature.create(
            title=literature_in.title,
            author=literature_in.author,
            publication_date=literature_in.publication_date,
            doi=literature_in.doi,
            url=literature_in.url,
            reference_count=literature_in.reference_count,
            reference_doi=literature_in.reference_doi,
            is_referenced_by_count=literature_in.is_referenced_by_count,
            score=literature_in.score,
            theme_auto=theme  # 自动生成的主题标签
        )
        # 关联用户
        await LiteratureUser.create(
            literature=literature,  # 外键可直接填实例对象
            user=current_user,
            theme_tags=[]
        )
        return create_response("success", 200, literature)


# 更新指定用户的文献记录
@literatures.put("/")
async def update_literatures(literature_in: LiteratureIn,
                             current_user: User = Depends(get_current_user)):
    # 检查文献记录是否存在，并获取文献记录
    literatures_existing = await Literature.filter(doi=literature_in.doi).first()
    if literatures_existing:
        # 检查当前用户是否关联了这篇文献
        is_associated = await LiteratureUser.filter(
            literature_id=literatures_existing.id,
            user_id=current_user.id
        ).exists()
        if not is_associated:
            return create_response("error", 404, "该用户没有关联这条文献记录！")
        # 检查是否有多个用户关联了这篇文献
        is_associated_count = await LiteratureUser.filter(literature_id=literatures_existing.id).count()
        if is_associated_count>1:
            return create_response("error", 409, "该文献记录已被多个用户关联，无法修改！")
    else:
        return create_response("error", 404, "文献记录不存在！")
    # 检查当前用户是否修改了这篇文献
    if is_equal(literatures_existing, literature_in):
        return create_response("error", 400, "修改后的文献记录与原先一致！")
    # 更新文献记录
    literature_changed =literature_in.model_dump()
    # 判断是否需要更新主题标签
    if literatures_existing.title != literature_in.title:
        theme = await theme_selector.choose_theme("{title:"+f"{literature_in.title}"+"}")
        literature_changed["theme_auto"] = theme
    else:
        literature_changed["theme_auto"] = literatures_existing.theme_auto

    await Literature.filter(id=literatures_existing.id).update(**literature_changed)
    return create_response("success", 200, literature_changed)


# 删除指定用户的文献记录
@literatures.delete("/")
async def delete_literatures(doi_in: DOIIn, current_user: User = Depends(get_current_user)):
    # 获取文献记录
    literatures_existing = await Literature.filter(doi=doi_in.doi).first()
    # 检查文献记录是否存在
    if literatures_existing:
        # 检查当前用户是否关联了这篇文献
        is_associated = await LiteratureUser.filter(
            literature_id=literatures_existing.id,
            user_id=current_user.id
        ).exists()
        if not is_associated:
            return create_response("error", 404, "该用户没有关联这条文献记录！")
    else:
        return create_response("error", 404, "文献记录不存在！")

    # 直接操作中间表删除当前用户与文献的关联（包括 theme_tags）
    await LiteratureUser.filter(
        literature=literatures_existing,
        user=current_user
    ).delete()

    # 检查是否还有其他用户关联这篇文献
    is_associated = await LiteratureUser.filter(
        literature_id=literatures_existing.id,
    ).exists()
    if not is_associated:
        # 如果没有其他用户关联，再删除文献实体
        await literatures_existing.delete()
        return create_response("success", 200, "文献记录已完全删除！")
    return create_response("success", 200, "已从您的文献库中移除该文献！")


# 查询文献记录，以主题分类返回
@literatures.get("/theme")
async def get_literatures_by_theme(current_user: User = Depends(get_current_user)):
    # 通过中间表查询用户关联的文献id
    literature_ids = await LiteratureUser.filter(
        user_id=current_user.id
    ).values_list("literature_id", flat=True)
    # 查询该用户的文献记录
    literatures_data = await Literature.filter(
        id__in=literature_ids
    ).values(
        "id", "title", "author", "publication_date", "doi", "url",
        "reference_count", "reference_doi", "is_referenced_by_count",
        "score", "theme_auto"
    )
    if not literatures_data:
        return create_response("error", 404, "没有找到该用户的文献记录！")

    # 按主题分类文献记录
    theme_dict = {}
    for literature in literatures_data:
        theme = literature["theme_auto"]
        if theme not in theme_dict:
            theme_dict[theme] = []
        theme_dict[theme].append(literature)

    return create_response('success', 200, theme_dict)

# 对于已关联的文献，用户可以自主输入主题标签（保存在literature_user表中）
@literatures.post("/theme_tags")
async def add_theme_tags(theme_in: ThemeIn, current_user: User = Depends(get_current_user)):
    literature_ids=list(set(theme_in.literature_ids))  # 去重处理，避免重复操作同一文献id
    theme= theme_in.theme
    # 根据文献id列表查询文献记录
    if not literature_ids:
        return create_response("error", 400, "文献ID列表不能为空！")
    # 根据传入文献记录id，提取出实际存在的文献记录id
    literature_existing_ids = await Literature.filter(id__in=literature_ids).values_list("id", flat=True)
    if len(literature_existing_ids)!= len(literature_ids):
        # 如果有文献id不存在，则返回错误
        missing_ids = set(literature_ids) - set(literature_existing_ids)
        return create_response("error", 404, f"文献ID列表中含有不存在的文献ID: {missing_ids}")

    # 检查是否每个文献记录都与用户有关联
    for literature_existing_id in literature_existing_ids:
        literature_existing = await LiteratureUser.filter(
            literature_id=literature_existing_id,
            user_id=current_user.id
        ).first()
        if not literature_existing:
            # 该文献与用户没有关联，返回错误
            return create_response("error", 404, f"该用户没有关联文献ID为 {literature_existing_id} 的文献记录！")

    # 进行添加主题标签操作
    for literature_existing_id in literature_existing_ids:
        literature_existing = await LiteratureUser.filter(
            literature_id=literature_existing_id,
            user_id=current_user.id
        ).first()
        # 更新用户的主题标签
        # 这里可以考虑使用set去重，避免重复添加同一主题标签
        await LiteratureUser.filter(
            literature_id=literature_existing_id,
            user_id=current_user.id
        ).update(theme_tags=list(set(literature_existing.theme_tags + [theme])))

    # 查询更新后的文献记录
    literature_out = await LiteratureUser.filter(
            literature_id__in=literature_existing_ids,
            user_id=current_user.id
        )
    return create_response("success", 200, literature_out)

#  查询文献记录，以用户自定义的主题分类返回
@literatures.get("/theme_tags")
async def get_literatures_by_theme_tags(current_user: User = Depends(get_current_user)):
    # 通过中间表查询用户关联的文献id
    literature_ids = await LiteratureUser.filter(
        user_id=current_user.id
    ).values_list("literature_id", flat=True)
    # 查询该用户的文献记录
    literatures_data = await Literature.filter(
        id__in=literature_ids
    ).values(
        "id", "title", "author", "publication_date", "doi", "url",
        "reference_count", "reference_doi", "is_referenced_by_count",
        "score", "theme_auto"
    )
    if not literatures_data:
        return create_response("error", 404, "没有找到该用户的文献记录！")

    # 按主题标签分类文献记录
    theme_tags_dict = {"None":[]}
    for literature in literatures_data:
        literature_user = await LiteratureUser.filter(
            literature_id=literature["id"],
            user_id=current_user.id
        ).first()
        theme_tags = literature_user.theme_tags# 获取用户自定义的主题标签
        if not theme_tags:
            theme_tags_dict["None"].append(literature)
            continue
        else:
            for theme_tag in theme_tags:
                if theme_tag not in theme_tags_dict:
                    theme_tags_dict[theme_tag] = []
                theme_tags_dict[theme_tag].append(literature)
    return create_response('success', 200, theme_tags_dict)

# 删除用户自定义的主题标签
@literatures.delete("/theme_tags")
async def delete_theme_tags(theme_in: ThemeIn, current_user: User = Depends(get_current_user)):
    literature_ids = list(set(theme_in.literature_ids))  # 去重处理，避免重复操作同一文献id
    theme = theme_in.theme
    # 根据文献id列表查询文献记录
    if not literature_ids:
        return create_response("error", 400, "文献ID列表不能为空！")
    # 根据传入文献记录id，提取出实际存在的文献记录id
    literature_existing_ids = await Literature.filter(id__in=literature_ids).values_list("id", flat=True)
    if len(literature_existing_ids) != len(literature_ids):
        # 如果有文献id不存在，则返回错误
        missing_ids = set(literature_ids) - set(literature_existing_ids)
        return create_response("error", 404, f"文献ID列表中含有不存在的文献ID: {missing_ids}")
    # 检查是否每个文献记录都存在要删除的主题标签
    for literature_existing_id in literature_existing_ids:
        literature_existing = await LiteratureUser.filter(
            literature_id=literature_existing_id,
            user_id=current_user.id
        ).first()
        if not literature_existing:
            # 该文献与用户没有关联，返回错误
            return create_response("error", 404, f"该用户没有关联文献ID为 {literature_existing_id} 的文献记录！")
        elif theme not in literature_existing.theme_tags:
            # 该文献记录中没有要删除的主题标签
            return create_response("error", 404, f"文献ID为 {literature_existing_id} 的文献记录中没有主题标签 {theme}！")

    # 进行删除主题标签操作
    for literature_existing_id in literature_existing_ids:
        literature_existing = await LiteratureUser.filter(
            literature_id=literature_existing_id,
            user_id=current_user.id
        ).first()
        new_tags = [tag for tag in literature_existing.theme_tags if tag != theme]
        # 删除用户的主题标签
        await LiteratureUser.filter(
            literature_id=literature_existing_id,
            user_id=current_user.id
        ).update(theme_tags=new_tags)

    # 查询更新后的文献记录
    literature_out = await LiteratureUser.filter(
        literature_id__in=literature_existing_ids,
        user_id=current_user.id
    )
    return create_response("success", 200, literature_out)

# 修改用户自定义的主题标签
@literatures.put("/theme_tags")
async def update_theme_tags(theme_in:ThemeChangeIn, current_user: User = Depends(get_current_user)):
    theme_old= theme_in.theme_old
    theme_new = theme_in.theme_new
    if theme_new == theme_old:
        return create_response("error", 400, "新主题标签不能与旧主题标签相同！")
    # 获取旧主题标签的文献记录
    literature_existing_ids = await LiteratureUser.filter(
        theme_tags__contains=[theme_old],  # 检查主题标签是否包含旧主题
        user_id=current_user.id
        ).values_list("literature_id", flat=True)
    if not literature_existing_ids:
        return create_response("error", 404, f"没有找到主题标签为'{theme_old}'的文献记录！")
    # 进行修改主题标签操作
    for literature_existing_id in literature_existing_ids:
        literature_existing = await LiteratureUser.filter(
            literature_id=literature_existing_id,
            user_id=current_user.id
            ).first()
        new_tags= [tag if tag != theme_old else theme_new for tag in literature_existing.theme_tags]
        await LiteratureUser.filter(
            literature_id=literature_existing_id,
            user_id=current_user.id
        ).update(theme_tags=new_tags)
    # 查询更新后的文献记录
    literature_out = await LiteratureUser.filter(
        literature_id__in=literature_existing_ids,
        user_id=current_user.id
    )
    return create_response("success", 200, literature_out)
