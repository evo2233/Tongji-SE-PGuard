"""
本文件用于管理员操作的API实现
"""
import os
import csv
import uuid
from core.config import RESOURCE_PATH
from fastapi import APIRouter, HTTPException, Query
from models.models import Package, Plant, City, Disease
from typing import List
from schemas.Map import PLANT_NAME_MAP

admin = APIRouter()


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


@admin.post('/package/add')
async def add_package(
        packageName: str = Query(...),
        price: float = Query(...),
        sumNum: int = Query(...)
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
        plantName: str = Query(...),
        plantFeature: str = Query(...),
        plantIconURL: str = Query(...)
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


@admin.post('/weather/city_input')
async def city_input(csvURL: str = Query(...)):
    """导入城市数据到数据库"""
    file = None
    try:
        # 验证并获取CSV reader
        csv_reader, file = validate_city_file(csvURL)

        # 清空现有数据
        await City.all().delete()

        # 批量创建城市记录
        cities = []
        row_count = 0
        for row in csv_reader:
            row_count += 1
            if len(row) >= 2:
                city_name = row[0].strip()
                city_code = row[1].strip()

                if not city_code or not city_name:
                    raise HTTPException(
                        status_code=400,
                        detail=f"第{row_count}行数据错误：城市名或代码不能为空"
                    )

                cities.append(
                    City(
                        cityCode=city_code,
                        cityName=city_name
                    )
                )
        if not cities:
            raise HTTPException(status_code=400, detail="CSV文件中没有数据")

        # 批量保存到数据库
        await City.bulk_create(cities)

        return {
            "message": f"成功导入 {len(cities)} 个城市数据",
            "url": f"/resource/{csvURL}"
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"导入城市数据失败: {str(e)}")
    finally:
        if file:
            file.close()


@admin.post('/disease/add')
async def add_disease(
        diseaseName: str = Query(...),
        plantName: str = Query(...),
        advice: str = Query(...)
):
    plant = await Plant.get(plantName=plantName)
    plant_name = PLANT_NAME_MAP.get(plant.plantName)
    if not plant_name:
        raise HTTPException(status_code=404, detail="未收录的植物")

    try:
        existing_disease = await Disease.filter(diseaseName=diseaseName).first()
        if existing_disease:
            raise HTTPException(status_code=400, detail="病名已存在")

        disease = await Disease.create(
            diseaseName=diseaseName,
            plantId=plant,
            advice=advice
        )

        return {
            "plantId": str(plant.plantId),
            "diseaseName": disease.diseaseName,
            "message": "病害添加成功"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"添加病害失败: {str(e)}")
