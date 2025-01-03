from fastapi import HTTPException

from models.models import Plant


async def get_all_plant_types():
    try:
        plants = await Plant.all()
        return [
            plant.plantName
            for plant in plants
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取植物名称失败: {str(e)}")
