import uvicorn
from fastapi import FastAPI
from tortoise.contrib.fastapi import register_tortoise
from database.settings import TORTOISE_ORM
from routers.admin import admin
from routers.user import user_api
from fastapi.middleware.cors import CORSMiddleware
app = FastAPI(
    title="PGuard API",
    description="PGuard 系统的 API 文档",
    version="1.0.0"
)

app.include_router(admin, prefix="/admin", tags=["AdminService"])
app.include_router(user_api, prefix="/user", tags=["UserService"])
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
register_tortoise(
    app=app,
    config=TORTOISE_ORM,
)

if __name__ == '__main__':
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
