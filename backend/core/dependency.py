from fastapi import Depends, HTTPException, status
from jose import jwt, JWTError

from core.config import SECRET_KEY, ALGORITHM, oauth2_scheme

from models.models import User


async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        # 先检查token是否在黑名单中
        from service.user import is_token_blacklisted
        if is_token_blacklisted(token):
            raise credentials_exception

        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    try:
        # 使用 userId 查询用户
        user = await User.get(userId=user_id)
        return user
    except Exception:
        raise credentials_exception
