import uuid

from fastapi import HTTPException

from core.config import validate_city_file
from models.models import Package, Plant, City, Disease
from models.Map import PLANT_NAME_MAP


async def create_package(packageName, price, sumNum):
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


async def del_package(packageId):
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


async def create_plant(plantName, plantFeature, plantIconURL):
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


async def del_plant(plantId):
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


async def all_plant():
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


async def bulk_create_city(csvURL):
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


async def create_disease(diseaseName, plantName, advice):
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
