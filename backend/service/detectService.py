import os
import uuid

from fastapi import HTTPException

from core.config import UPLOAD_PATH
from core.yolov8 import detect
from models.Map import PLANT_NAME_MAP, DISEASE_NAME_MAP
from service.impl.detectImpl import get_advice
from service.impl.logImpl import set_log
from service.impl.plotImpl import get_plot_by_id


async def do_detect(plotId, file, user):
    try:
        # 验证地块访问权限
        try:
            plot = await get_plot_by_id(plotId)
            if plot.userId.userId != user.userId:
                raise HTTPException(status_code=403, detail=f"未授权的地块访问")
        except Exception as e:
            raise HTTPException(status_code=404, detail=f"地块验证失败: {str(e)}")

        # 获取植物类型并验证
        plant_name = PLANT_NAME_MAP.get(plot.plantId.plantName)
        if not plant_name:
            raise HTTPException(status_code=404, detail=f"未收录的植物: {plot.plantId.plantName}")

        # 处理图片
        file_extension = os.path.splitext(file.filename)[1]
        if file_extension not in [".jpg", ".jpeg", ".png"]:
            raise HTTPException(status_code=400, detail="请上传.jpg图片")
        unique_filename = f"{uuid.uuid4()}{file_extension}"

        # 保存图片
        save_path = os.path.join(UPLOAD_PATH, str(plot.plotId), unique_filename)
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        with open(save_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)

        # 调用检测函数
        results = detect(plant_name, save_path)
        name = DISEASE_NAME_MAP.get(results.get('disease'))
        advice = await get_advice(results.get('disease'))
        percent = results.get('confidence', 0)

        # 保存日志
        path = f"/resource/log/{str(plot.plotId)}/{unique_filename}"
        await set_log(plotId, name, advice, path)

        return {
            "diseaseName": name,
            "advice": advice,
            "percent": percent,
            "imageURL": f"/resource/log/{plot.plotId}/{unique_filename}"
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"检测过程发生未知错误: {str(e)}")