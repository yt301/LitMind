from fastapi import APIRouter, Depends, File, UploadFile
from fastapi.responses import FileResponse  # 用于下载文件
from tools import *
from models import *
from .auth import get_current_user
from typing import List
from config import FILE_PATH
from urllib.parse import unquote  # 用于解码文件名（处理中文乱码）
import os  # 检查文件夹是否存在，如果不存在则创建

# 文件管理相关接口
files = APIRouter()


# 查询用户的上传文件
@files.get("/")
async def get_files(current_user: User = Depends(get_current_user)):
    file=await File.filter(user_id=current_user.id).values("id","file_name","file_type","file_size","file_path","upload_time")
    return create_response("success", 200, file)


# 可支持多个大文件的上传
@files.post("/")
async def upload_files(file_list: List[UploadFile], current_user: User = Depends(get_current_user)):
    # 创建文件夹
    folder_path = fr"{FILE_PATH}\{current_user.id}"  # 拼接文件夹路径
    result = {
        "success": [],
        "error": [],
        "total": len(file_list)  # 统计上传文件总数
    }
    if not os.path.exists(folder_path):  # 文件夹不存在则创建
        os.makedirs(folder_path)

    # 保存文件
    for file in file_list:
        filepath = fr"{FILE_PATH}\{current_user.id}\{file.filename}"  # 拼接文件路径
        # 检查文件是否已存在
        if os.path.exists(filepath):
            result["error"].append({"filename": file.filename, "filetype": file.content_type, "size": file.size,
                                    "reason": "同名文件已存在！"})
            continue
        try:
            # 保存文件
            with open(filepath, "wb") as f:
                for line in file.file:  # 逐行读取文件内容，省内存
                    f.write(line)
            # 创建文件记录
            await File.create(
                file_name=file.filename,
                file_path=filepath,
                file_type=file.content_type,
                file_size=file.size,
                user_id=current_user.id,
            )
            result["success"].append({"filename": file.filename, "filetype": file.content_type, "size": file.size})
        except Exception as e:
            result["error"].append(
                {"filename": file.filename, "filetype": file.content_type, "size": file.size, "reason": str(e)})
    return create_response("success", 200, result)


# 修改文件
@files.put("/")
async def update_files(file_list: List[UploadFile], current_user: User = Depends(get_current_user)):
    result = {
        "success": [],
        "error": [],
        "total": len(file_list)  # 统计修改上传文件总数
    }
    for file in file_list:
        filepath = fr"{FILE_PATH}\{current_user.id}\{file.filename}"  # 拼接文件路径
        if not os.path.exists(filepath):
            result["error"].append(
                {"filename": file.filename, "filetype": file.content_type, "size": file.size, "reason": "文件不存在！"})
            continue
        try:
            # 修改文件
            with open(filepath, "wb") as f:
                for line in file.file:  # 逐行读取文件内容，省内存
                    f.write(line)
            # 修改文件记录
            await File.filter(file_name=file.filename, user_id=current_user.id).update(file_size=file.size)
            result["success"].append({"filename": file.filename, "filetype": file.content_type, "size": file.size})
        except Exception as e:
            result["error"].append(
                {"filename": file.filename, "filetype": file.content_type, "size": file.size, "reason": str(e)})
    return create_response("success", 200, result)


# 删除文件
@files.delete("/")
async def delete_files(filename_in:FilenameIn, current_user: User = Depends(get_current_user)):
    result = {
        "success": [],
        "error": [],
        "total": len(filename_in.filename)  # 统计删除文件总数
    }
    for file in filename_in.filename:
        filepath = fr"{FILE_PATH}\{current_user.id}\{file}"  # 拼接文件路径，解码文件名
        if not os.path.exists(filepath):
            result["error"].append({"filename": file, "reason": "文件不存在！"})
            continue
        try:
            # 删除文件
            os.remove(filepath)
            # 删除文件记录
            await File.filter(file_name=file, user_id=current_user.id).delete()
            result["success"].append({"filename": file})
        except Exception as e:
            result["error"].append({"filename": file, "reason": str(e)})
    return create_response("success", 200, result)


# 下载文件
@files.post("/download")
async def download_files(filename_in:FilenameIn, current_user: User = Depends(get_current_user)):
    # result = {
    #     "success": [],
    #     "error": [],
    #     "total": len(filename_in.filename)
    # }

    # 检查用户目录是否存在
    user_dir = os.path.join(FILE_PATH, str(current_user.id))
    if not os.path.exists(user_dir):
        return create_response("error", 404,"用户目录不存在")
    # 处理单个文件下载
    if len(filename_in.filename) == 1:
        file = filename_in.filename[0]
        filepath = os.path.join(user_dir, file)

        if not os.path.exists(filepath):
            return create_response("error", 404,f"文件{file}不存在！")

        # 验证文件属于当前用户
        if not await File.filter(file_name=file, user_id=current_user.id).exists():
            return create_response("error", 403,"无权访问此文件！")

        return FileResponse(
            filepath,
            filename=file,  # 下载时显示的文件名
            media_type="application/octet-stream"  # 通用二进制流类型
        )
    else:
        return create_response("error", 405,"暂不支持多个文件同时下载！")
    # # 处理多个文件下载（打包为ZIP）
    # else:
    #     import zipfile
    #     from io import BytesIO
    #
    #     zip_buffer = BytesIO()
    #     with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
    #         for file in filename_in.filename:
    #             filepath = os.path.join(user_dir, file)
    #
    #             try:
    #                 # 验证文件存在且属于用户
    #                 if not os.path.exists(filepath):
    #                     result["error"].append({"filename": file, "reason": "文件不存在"})
    #                     continue
    #
    #                 if not await File.filter(file_name=file, user_id=current_user.id).exists():
    #                     result["error"].append({"filename": file, "reason": "无权访问"})
    #                     continue
    #
    #                 # 将文件添加到ZIP
    #                 zip_file.write(filepath, arcname=file)
    #                 result["success"].append({"filename": file})
    #
    #             except Exception as e:
    #                 result["error"].append({"filename": file, "reason": str(e)})
    #
    #     # 如果没有成功文件则报错
    #     if not result["success"]:
    #         raise HTTPException(
    #             status_code=400,
    #             detail={"message": "所有文件下载失败", "details": result}
    #         )
    #
    #     # 返回ZIP文件
    #     zip_buffer.seek(0)
    #     return FileResponse(
    #         zip_buffer,
    #         media_type="application/zip",
    #         filename="downloads.zip",
    #         headers={
    #             "Content-Disposition": "attachment; filename=downloads.zip",
    #             "Access-Control-Expose-Headers": "Content-Disposition"
    #         }
    #     )
