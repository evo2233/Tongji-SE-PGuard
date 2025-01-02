import subprocess
import os
from core.config import ULTRALYTICS_PATH


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
