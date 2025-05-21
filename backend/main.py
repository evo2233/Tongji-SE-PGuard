import uvicorn
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from tortoise.contrib.fastapi import register_tortoise
from database.settings import TORTOISE_ORM
from fastapi.middleware.cors import CORSMiddleware
from core.config import RESOURCE_PATH

from controller.adminController import admin
from controller.userController import user_api
from controller.plotController import plot_api
from controller.detectController import detect_api
from controller.logController import log_api

app = FastAPI(
    title="PGuard API",
    description="PGuard 系统的 API 文档",
    version="1.0.0"
)

# 挂载静态文件目录
app.mount("/resource", StaticFiles(directory=RESOURCE_PATH), name="resource")

app.include_router(admin, prefix="/admin", tags=["AdminService"])
app.include_router(user_api, prefix="/user", tags=["UserService"])
app.include_router(plot_api, prefix="/plot", tags=["PlotService"])
app.include_router(detect_api, tags=["DetectService"])
app.include_router(log_api, prefix="/log", tags=["LogService"])

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
