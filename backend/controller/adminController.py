"""
本文件用于管理员操作的API实现
"""
from fastapi import APIRouter, Query
from typing import List
from service.adminService import create_package, del_package, del_plant, create_plant, all_plant, bulk_create_city, \
    create_disease

admin = APIRouter()


@admin.post('/package/add')
async def add_package(
        packageName: str = Query(...),
        price: float = Query(...),
        sumNum: int = Query(...)
):
    return await create_package(packageName, price, sumNum)


@admin.delete('/package/{packageId}')
async def delete_package(packageId: str):
    return await del_plant(packageId)


@admin.post('/plant/add')
async def add_plant(
        plantName: str = Query(...),
        plantFeature: str = Query(...),
        plantIconURL: str = Query(...)
):
    return await create_plant(plantName, plantFeature, plantIconURL)


@admin.delete('/plant/{plantId}')
async def delete_plant(plantId: str):
    return await del_package(plantId)


@admin.get('/plant', response_model=List[dict])
async def get_all_plants():
    return await all_plant()


@admin.post('/weather/city_input')
async def city_input(csvURL: str = Query(...)):
    return await bulk_create_city(csvURL)


@admin.post('/disease/add')
async def add_disease(
        diseaseName: str = Query(...),
        plantName: str = Query(...),
        advice: str = Query(...)
):
    return await create_disease(diseaseName, plantName, advice)
