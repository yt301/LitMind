from fastapi.responses import JSONResponse, Response
from typing import Any, Dict, Union
import json


def create_response(
        status: str,
        http_status_code: int,
        data: Any,
        is_binary: bool = False,
        media_type: str = "application/octet-stream"
) -> Union[JSONResponse, Response]:
    """
    创建符合RESTful风格的统一响应

    :param status: 业务状态 'success'/'error'
    :param http_status_code: 符合HTTP规范的状态码 (200, 404等)
    :param data: 响应数据
    :param is_binary: 是否为二进制数据
    :param media_type: 二进制数据类型
    :return: FastAPI响应对象
    """
    if is_binary:
        # 二进制响应(如图片/文件)
        return Response(
            content=data,
            status_code=http_status_code,
            media_type=media_type  # 或具体类型如"image/jpeg"
        )
    else:
        # JSON响应
        content = {
            "status": status,
            "code": http_status_code,  # 与HTTP状态码保持一致
            "data": data
        }
        return JSONResponse(
            content=content,
            status_code=http_status_code
        )


# from typing import Any, Dict
#
#
# def create_response(status: str, code: int, data: Any) -> Dict[str, Any]:
#     """
#     创建统一的响应格式
#     """
#     return {
#         "status": status,  # success / error
#         "code": code,  # 状态码
#         "data": data  # 响应数据，成功时返回json数据，失败时返回错误信息
#     }