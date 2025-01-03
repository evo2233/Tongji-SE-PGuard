import os
import subprocess
import uuid

from fastapi import HTTPException, UploadFile, Depends
from core.config import ULTRALYTICS_PATH, UPLOAD_PATH
from core.dependency import get_current_user

from models.models import Disease, User
from controller.detectController import validate_plot_access, call_set_log
from schemas.Map import PLANT_NAME_MAP, DISEASE_NAME_MAP


def detect(model_type: str, image_path: str):
    if model_type == "Grape":
        python_script = os.path.join(ULTRALYTICS_PATH, "Grape_defect.py")
    elif model_type == "Potato":
        python_script = os.path.join(ULTRALYTICS_PATH, "Potato_defect.py")
    else:
        raise ValueError("model_type not supported")

    env_path = os.path.join(ULTRALYTICS_PATH, "yolov8_env")

    python_exe = os.path.join(env_path, "python")

    command = [python_exe, python_script, "--image_path", image_path]

    process = subprocess.Popen(
        command,
        cwd=ULTRALYTICS_PATH,  # 设置工作目录
        stdout=subprocess.PIPE,  # 捕获标准输出
        stderr=subprocess.PIPE,  # 捕获错误输出
        text=True,
        encoding="utf-8",  # 子进程的输出编码
        errors="replace"  # 忽略解码错误
    )

    stdout, stderr = process.communicate()

    detection_result = None
    for line in stdout.splitlines():
        if "类别" in line and "置信度" in line:  # 解析规则
            parts = line.split(", ")
            cls = parts[0].split(": ")[1]
            conf = float(parts[1].split(": ")[1])
            detection_result = {"disease": cls, "confidence": conf}
            break  # 找到第一个匹配结果后立即退出循环
    return detection_result


async def get_advice(diseaseName: str):
    try:
        disease = await Disease.get(diseaseName=diseaseName)
        return disease.advice
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))


async def do_detect(
        plotId: str,
        file: UploadFile,
        user: User = Depends(get_current_user)
):
    try:
        plot = await validate_plot_access(plotId, user)

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
        await call_set_log(plotId, name, advice, path)

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
