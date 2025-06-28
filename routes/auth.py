from fastapi import APIRouter
from models import *
from fastapi.security import OAuth2PasswordBearer
from datetime import timedelta

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")  # 用于保护接口

# 验证token的依赖函数
from fastapi import Depends
from tools import *
from jose import jwt
from fastapi import HTTPException
from jose.exceptions import JWTError  # 实际异常定义位置


# 该函数于从 JWT 令牌中提取当前用户信息，并验证该用户是否存在。它通常用于保护需要用户登录的路由，确保只有经过身份验证的用户才能访问这些路由。
async def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])  # 解码 JWT 令牌
        username = payload.get("sub")  # 从令牌中提取用户名
        if not username:
            raise HTTPException(status_code=401, detail="无效Token")  # 如果没有用户名，抛出未授权异常
    except JWTError:  # 捕获 JWT 解码错误
        raise HTTPException(status_code=401, detail="Token过期或无效")  # 如果令牌无效或过期，抛出未授权异常

    user = await User.filter(username=username).first()  # 从数据库中查找用户
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")  # 如果用户不存在，抛出未找到异常
    return user


# 保护接口：在路径函数参数中加上current_user: User = Depends(get_current_user)，即可确保只有经过身份验证的用户才能访问该接口。
# 请求头中需带上参数 Authorization:"Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ1c2VyMiIsImV4cCI6MTc1MDg1ODE5MH0.GCiVVzsv92MD38gNYbiOj-OYW6tDOnd41HBD5stOsGs"


# auth路由
auth = APIRouter()


@auth.post("/login")
async def login(user_in: UserLoginIn):
    user = await User.filter(username=user_in.username)
    if not user:
        user = await User.filter(email=user_in.email)
    if not user:
        return create_response("error", 404, "用户名或邮箱错误！")
    elif not verify_password(user_in.password, user[0].hashed_password):  # 哈希加密的密码验证
        return create_response("error", 401, "密码错误！")
    else:
        # 生成 Token
        access_token = create_access_token(
            data={"sub": user[0].username},  # 通常存用户唯一标识
            expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        )
        response_data = create_response("success", 200, data_out(user[0], UserOut()))
        response_data["Authorization"]= f"Bearer {access_token}"
        # response_data["access_token"] = access_token
        # response_data["token_type"] = "bearer"
        return response_data


@auth.post("/register")
async def register(user_in: UserRegisterIn):
    existing_user = await User.filter(username=user_in.username)
    if existing_user:
        return create_response("error", 400, "用户名已存在！")
    existing_email = await User.filter(email=user_in.email)
    if existing_email:
        return create_response("error", 400, "邮箱已被注册！")
    user = await User.create_user(
        username=user_in.username,
        password=user_in.password,  # 明文传入，模型内自动哈希
        email=user_in.email
    )
    return create_response("success", 200, data_out(user, UserOut()))


@auth.post("/logout")
async def logout():
    return create_response("success", 200, "已成功登出！")
