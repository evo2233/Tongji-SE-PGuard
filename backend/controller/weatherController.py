from models.models import City


async def validate_location(location: str):
    """验证城市是否存在"""
    city = await City.filter(cityName=location).first()
    if not city:
        raise ValueError("无效的城市名称")
    return True
