import csv
import os
from typing import Set
from fastapi import HTTPException
from entities.models import City

# 允许的图片类型
ALLOWED_IMAGE_TYPES: Set[str] = {'.jpg', '.jpeg', '.png'}
# 获取项目根目录的resource文件夹路径
RESOURCE_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "resource")
# 确保resource目录存在
if not os.path.exists(RESOURCE_PATH):
    os.makedirs(RESOURCE_PATH)

# yolov8模型路径
ULTRALYTICS_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "yolov8\\ultralytics-main")

# 按地块分类存放上传检测图片的文件夹
UPLOAD_PATH: str = os.path.join(RESOURCE_PATH, "log")


def validate_image_file(url: str):
    icon_path = os.path.join(RESOURCE_PATH, url)

    # 检查文件是否存在
    if not os.path.exists(icon_path):
        return "图片不存在"

    # 检查文件扩展名
    file_ext = os.path.splitext(icon_path)[1].lower()
    if file_ext not in ALLOWED_IMAGE_TYPES:
        return "不支持此拓展名"
    return f"/resource/{url}"


def validate_city_file(url: str):
    # 验证文件是否存在
    csvURL = os.path.join(RESOURCE_PATH, url)
    if not os.path.exists(csvURL):
        raise HTTPException(status_code=404, detail="CSV文件不存在")

    # 验证文件扩展名
    file_ext = os.path.splitext(csvURL)[1].lower()
    if file_ext != '.csv':
        raise HTTPException(status_code=400, detail="文件格式必须是CSV")

    # 读取CSV文件
    try:
        file = open(csvURL, 'r', encoding='utf-8')
        csv_reader = csv.reader(file)
        return csv_reader, file  # 返回reader和file对象，以便后续关闭文件
    except UnicodeDecodeError:
        raise HTTPException(status_code=400, detail="CSV文件编码必须是UTF-8")
    except csv.Error as e:
        raise HTTPException(status_code=400, detail=f"CSV文件格式错误: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"读取CSV文件失败: {str(e)}")


async def validate_location(location: str):
    """验证城市是否存在"""
    city = await City.filter(cityName=location).first()
    if not city:
        raise ValueError("无效的城市名称")
    return True
