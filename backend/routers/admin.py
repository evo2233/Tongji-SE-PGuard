"""
本文件用于数据库测试数据的添加
"""
from fastapi import APIRouter, Body, HTTPException
from models.models import Package

admin = APIRouter()


@admin.post('/addpackage')
async def add_package(
        packageName: str = Body(..., embed=True),
        price: float = Body(..., embed=True),
        sumNum: int = Body(..., embed=True),
):
    try:
        package = await Package.create(
            packageName=packageName,
            price=price,
            sumNum=sumNum,
        )
        return package
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
