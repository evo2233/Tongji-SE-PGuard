"""
本文件用于管理员操作的API实现
"""
import uuid
from fastapi import APIRouter, Body, HTTPException
from models.models import Package, Plant, Plot
from typing import List

admin = APIRouter()


@admin.post('/package/add')
async def add_package(
        packageName: str = Body(...),
        price: float = Body(...),
        sumNum: int = Body(...)
):
    try:
        # 验证输入
        if price <= 0:
            raise ValueError("价格必须大于0")
        if sumNum <= 0:
            raise ValueError("次数必须大于0")

        package = await Package.create(
            packageName=packageName,
            price=price,
            sumNum=sumNum,
        )
        return {
            "packageId": str(package.packageId),
            "packageName": package.packageName,
            "price": package.price,
            "sumNum": package.sumNum,
            "message": "套餐创建成功"
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"创建套餐失败: {str(e)}")


@admin.delete('/package/{packageId}')
async def delete_package(packageId: str):
    try:
        package = await Package.get(packageId=uuid.UUID(packageId))
        if not package:
            raise HTTPException(status_code=404, detail="套餐不存在")
        
        await package.delete()
        return {"message": "套餐删除成功"}
    except ValueError:
        raise HTTPException(status_code=400, detail="无效的套餐ID格式")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"删除套餐失败: {str(e)}")


@admin.post('/plant/add')
async def add_plant(
        plantName: str = Body(...),
        plantFeature: str = Body(...),
        plantIconURL: str = Body(...)
):
    try:
        # 检查植物名是否已存在
        existing_plant = await Plant.filter(plantName=plantName).first()
        if existing_plant:
            raise HTTPException(status_code=400, detail="植物名称已存在")

        plant = await Plant.create(
            plantName=plantName,
            plantFeature=plantFeature,
            plantIconURL=plantIconURL
        )

        return {
            "plantId": str(plant.plantId),
            "plantName": plant.plantName,
            "plantFeature": plant.plantFeature,
            "plantIconURL": plant.plantIconURL,  # eg: XXX.jpg
            "message": "植物添加成功"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"添加植物失败: {str(e)}")


@admin.delete('/plant/{plantId}')
async def delete_plant(plantId: str):
    try:
        # 检查植物是否存在
        plant = await Plant.get(plantId=uuid.UUID(plantId))
        if not plant:
            raise HTTPException(status_code=404, detail="植物不存在")
            
        await plant.delete()
        return {"message": "植物删除成功"}
    except ValueError:
        raise HTTPException(status_code=400, detail="无效的植物ID格式")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"删除植物失败: {str(e)}")


@admin.get('/plant', response_model=List[dict])
async def get_all_plants():
    try:
        plants = await Plant.all()
        return [
            {
                "plantId": str(plant.plantId),
                "plantName": plant.plantName,
                "plantFeature": plant.plantFeature,
                "plantIconURL": plant.plantIconURL
            }
            for plant in plants
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取植物列表失败: {str(e)}")
