import uvicorn
from fastapi import FastAPI, Request,status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from routes import auth, literatures, search
from tortoise.contrib.fastapi import register_tortoise
from tools import *
from config import CONFIG
app = FastAPI()
app.include_router(auth, prefix='/auth', tags=['登录相关接口'])  # 注册路由
app.include_router(literatures, prefix='/literatures', tags=['文献记录管理相关接口'])  # 注册路由
app.include_router(search, prefix='/search', tags=['文献搜索相关接口'])

# 连接数据库
register_tortoise(
    app=app,
    config=CONFIG,
    # generate_schemas=True,  # 是否自动生成数据库表结构
    # add_exception_handlers=True,  # 是否添加异常处理
)


# 自定义校验错误处理器
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = exc.errors()
    first_error = errors[0]  # 取第一个错误信息
    error_field = first_error["loc"][-1]  # 出错字段名
    error_msg = first_error["msg"]  # 原始错误消息

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=create_response(
            status="error",
            code=422,
            data=f"参数校验失败: {error_field} - {error_msg}"
        )
    )




if __name__ == '__main__':
    uvicorn.run('main:app', host='127.0.0.1', port=8080, reload=True, workers=1)
    # ip为0.0.0.0时，运行在局域网中，可通过ipconfig查看在局域网中的ip。
