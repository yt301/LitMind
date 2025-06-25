from typing import Any, Dict


def create_response(status: str, code: int, data: Any) -> Dict[str, Any]:
    """
    创建统一的响应格式
    """
    return {
        "status": status,  # success / error
        "code": code,  # 状态码
        "data": data  # 响应数据，成功时返回json数据，失败时返回错误信息
    }
