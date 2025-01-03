from fastapi import HTTPException, Depends

from core.userController import get_current_user
from models.models import City, User


async def search_city(keyword: str):
    """根据关键字搜索城市"""
    try:
        cities = await City.filter(cityName__contains=keyword).all()
        if not cities:
            return {"message": "未找到匹配的城市"}
        return [
            {
                "cityName": city.cityName,
                "cityCode": city.cityCode
            }
            for city in cities
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"搜索城市失败: {str(e)}")


async def get_city_by_name(user: User = Depends(get_current_user)):
    try:
        city = await City.get(cityName=user.location)
        if not city:
            return {"message": "未找到匹配的城市"}
        return {
            "cityName": city.cityName,
            "cityCode": city.cityCode
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取城市码失败: {str(e)}")