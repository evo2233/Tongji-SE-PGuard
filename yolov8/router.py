import subprocess
import os
from typing import List, Tuple

def detect( model_type: str , image_path: str):
    python_script = ""
    if(model_type=="Grape"):
        python_script = "C:\\PGuard\\yolov8\\ultralytics-main\\Grape_defect.py"
    else:
        python_script = "C:\\PGuard\\yolov8\\ultralytics-main\\Potato_defect.py"
    env_path = "C:\\PGuard\\yolov8\\ultralytics-main\\yolov8_env"

    python_exe = os.path.join(env_path, "python")  # 对于 Windows，可能是 "Scripts" 目录

    command = [python_exe, python_script, "--image_path", image_path]

    process = subprocess.Popen(
        command,
        cwd="C:\\PGuard\\yolov8\\ultralytics-main",  # 设置工作目录
        stdout=subprocess.PIPE,  # 捕获标准输出
        stderr=subprocess.PIPE,  # 捕获错误输出
        text=True,
        encoding="utf-8",  # 子进程的输出编码
        errors="replace"  # 忽略解码错误           
    )

    stdout, stderr = process.communicate()

    detection_results = []
    for line in stdout.splitlines():
        if "类别" in line and "置信度" in line:  # 根据实际输出格式调整解析规则
            parts = line.split(", ")
            cls = parts[0].split(": ")[1]
            conf = float(parts[1].split(": ")[1])
            detection_results.append((cls, conf))
    return detection_results



