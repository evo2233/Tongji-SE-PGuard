import uvicorn
from fastapi import FastAPI
from tortoise.contrib.fastapi import register_tortoise

from database.settings import TORTOISE_ORM
from routers.user import user_api

app_api = FastAPI(
    title="PGuard API",
    description="PGuard 系统的 API 文档",
    version="1.0.0"
)

app_api.include_router(user_api, prefix="/user", tags=["UserService"])

register_tortoise(
    app=app_api,
    config=TORTOISE_ORM,
)

if __name__ == '__main__':
    uvicorn.run(
        "main:app_api",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
