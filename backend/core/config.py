import os
from typing import Set

# 允许的图片类型
ALLOWED_IMAGE_TYPES: Set[str] = {'.jpg', '.jpeg', '.png', '.gif', '.webp'}
# 获取项目根目录的resource文件夹路径
RESOURCE_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "resource")

# 确保resource目录存在
if not os.path.exists(RESOURCE_PATH):
    os.makedirs(RESOURCE_PATH)


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
