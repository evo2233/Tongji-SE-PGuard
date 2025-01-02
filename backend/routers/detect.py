import os
import uuid
from core.yolov8 import detect
from core.config import UPLOAD_PATH
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from dependencies.auth import get_current_user
from models.models import Plot, User, Plant

detect_api = APIRouter()


async def get_plot_by_id(plotId: str):
    try:
        # 同时预加载 userId 和 plantId 的关联数据
        plot = await Plot.get(plotId=plotId).select_related("userId", "plantId")
        if plot:
            return plot
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))


PLANT_NAME_MAP = {
    "葡萄": "Grape",
    "马铃薯": "Potato"
}


# async def set_log():


@detect_api.post("/plot/{plotId}/detect")
async def do_detect(
        plotId: str,
        file: UploadFile,
        user: User = Depends(get_current_user)
):
    try:
        plot = await get_plot_by_id(plotId)
        if plot.userId.userId != user.userId:
            raise HTTPException(status_code=500, detail=f"未授权的地块访问")

        # 处理图片
        file_extension = os.path.splitext(file.filename)[1]
        if file_extension not in [".jpg", ".jpeg"]:
            raise HTTPException(status_code=500, detail="请上传.jpg图片")
        unique_filename = f"{uuid.uuid4()}{file_extension}"

        # 直接使用预加载的 plantId 关联数据
        plant_name = PLANT_NAME_MAP.get(plot.plantId.plantName)
        if not plant_name:
            raise HTTPException(status_code=404, detail="未收录的植物")

        # 最后保存图片
        save_path = os.path.join(UPLOAD_PATH, str(plot.plotId), unique_filename)
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        with open(save_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)

        # 调用检测函数
        results = detect(plant_name, save_path)

        return results

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"检测失败: {str(e)}")
