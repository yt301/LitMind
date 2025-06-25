from datetime import datetime, timedelta
from jose import jwt
from passlib.context import CryptContext

# 安全配置
SECRET_KEY = "your-secret-key"  # 生产环境应从环境变量读取
ALGORITHM = "HS256"  # 生成 JWT 时使用的算法（使用 HMAC SHA-256 算法）
ACCESS_TOKEN_EXPIRE_MINUTES = 30  # 访问令牌的过期时间（分钟）

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto") # 密码哈希上下文

def verify_password(plain_password: str, hashed_password: str):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str):
    return pwd_context.hash(password)

# 生成一个 JWT（JSON Web Token）访问令牌
def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    expire = datetime.now() + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

