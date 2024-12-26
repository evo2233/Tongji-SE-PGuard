import uuid
from fastapi import APIRouter, Depends, HTTPException, Body
from models.models import User, Plot, Plant
from dependencies.auth import get_current_user
from typing import List

plot_api = APIRouter()


@plot_api.get("", response_model=List[dict])
async def get_all_plots(user: User = Depends(get_current_user)):
    try:
        # 获取地块并同时获取关联的植物信息
        plots = await Plot.filter(userId=user.userId).prefetch_related('plantId').all()
        
        # 构建响应数据
        result = []
        for plot in plots:
            result.append({
                "plotId": str(plot.plotId),
                "plotName": plot.plotName,
                "plantId": str(plot.plantId.plantId),
                "plantName": plot.plantId.plantName,
                "plantFeature": plot.plantId.plantFeature,
                "plantIconURL": plot.plantId.plantIconURL
            })
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取地块失败: {str(e)}")


@plot_api.post("/add")
async def add_plot(
    plotName: str = Body(...),
    plantId: str = Body(...),
    user: User = Depends(get_current_user)
):
    try:
        # 验证植物是否存在
        plant = await Plant.get(plantId=uuid.UUID(plantId))
        if not plant:
            raise HTTPException(status_code=404, detail="未找到指定植物")

        # 创建新地块
        plot = await Plot.create(
            plotName=plotName,
            userId=user.userId,
            plantId=plant.plantId
        )
        
        # 构建响应数据
        return {
            "plotId": str(plot.plotId),
            "plotName": plot.plotName,
            "plantId": str(plot.plantId),
            "message": "地块创建成功"
        }
    except ValueError:
        raise HTTPException(status_code=400, detail="无效的植物ID格式")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"创建地块失败: {str(e)}")


@plot_api.get("/{plotId}")
async def get_plot_by_id(plotId: str, user: User = Depends(get_current_user)):
    try:
        # 获取地块并验证所有权
        plot = await Plot.filter(
            plotId=uuid.UUID(plotId),
            userId=user.userId
        ).prefetch_related('plantId').first()
        
        if not plot:
            raise HTTPException(status_code=404, detail="未找到地块或无权访问")
            
        # 构建响应数据
        return {
            "plotId": str(plot.plotId),
            "plotName": plot.plotName,
            "plantId": str(plot.plantId.plantId),
            "plantName": plot.plantId.plantName,
            "plantFeature": plot.plantId.plantFeature,
            "plantIconURL": plot.plantId.plantIconURL
        }
    except ValueError:
        raise HTTPException(status_code=400, detail="无效的地块ID格式")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取地块详情失败: {str(e)}")


@plot_api.patch("/{plotId}")
async def update_plot(
    plotId: str,
    plotName: str = Body(...),
    user: User = Depends(get_current_user)
):
    """更新地块信息"""
    try:
        # 获取并验证地块
        plot = await Plot.get(plotId=uuid.UUID(plotId), userId=user.userId)
        if not plot:
            raise HTTPException(status_code=404, detail="未找到地块或无权访问")
            
        # 更新地块信息
        plot.plotName = plotName
        await plot.save()
        
        return {
            "plotId": str(plot.plotId),
            "plotName": plot.plotName,
            "message": "地块更新成功"
        }
    except ValueError:
        raise HTTPException(status_code=400, detail="无效的地块ID格式")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"更新地块失败: {str(e)}")


@plot_api.delete("/{plotId}")
async def delete_plot(plotId: str, user: User = Depends(get_current_user)):
    try:
        # 获取并验证地块
        plot = await Plot.get(plotId=uuid.UUID(plotId), userId=user.userId)
        if not plot:
            raise HTTPException(status_code=404, detail="未找到地块或无权访问")
            
        # 删除地块
        await plot.delete()
        return {"message": "地块删除成功"}
    except ValueError:
        raise HTTPException(status_code=400, detail="无效的地块ID格式")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"删除地块失败: {str(e)}")
