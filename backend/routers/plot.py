import uuid
from fastapi import APIRouter, Depends, HTTPException, Body
from fastapi.responses import FileResponse
from tortoise.exceptions import DoesNotExist
from models.models import User, Plot, Plant, Log
from dependencies.auth import get_current_user
from core.config import validate_image_file
from typing import List
from schemas.form import PlotDetails, LogDetail
from datetime import datetime
from tortoise.query_utils import Prefetch
from tortoise.queryset import Prefetch

plot_api = APIRouter()


@plot_api.get('/plant', response_model=List[str])
async def get_all_plant_types():
    try:
        plants = await Plant.all()
        return [
            plant.plantName
            for plant in plants
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取植物名称失败: {str(e)}")


@plot_api.get("")
async def get_all_plots(user: User = Depends(get_current_user)):
    try:
        plots = await Plot.filter(userId=user.userId).prefetch_related('plantId').all()
        
        result = []
        for plot in plots:
            # 验证图片是否合法
            icon_url = validate_image_file(plot.plantId.plantIconURL)
            
            result.append({
                "plotId": str(plot.plotId),
                "plotName": plot.plotName,
                "plantName": plot.plantId.plantName,
                "plantIconURL": icon_url
            })
        if not result:
            return {"message": "当前地块列表为空"}
        else:
            return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取地块失败: {str(e)}")


@plot_api.post("/add")
async def add_plot(
    plotName: str = Body(...),
    plantName: str = Body(...),
    user: User = Depends(get_current_user)
):
    try:
        # 验证植物是否存在
        plant = await Plant.get(plantName=plantName)

        # 创建新地块
        plot = await Plot.create(
            plotName=plotName,
            userId=user,    # 这里外键不能传user.userId，而是直接传user
            plantId=plant
        )
        
        # 构建响应数据
        return {
            "plotId": str(plot.plotId),
            "plotName": plot.plotName,
            "plantId": str(plot.plantId.plantId),
            "plantName": plant.plantName,
            "message": "地块创建成功"
        }
    except ValueError:
        raise HTTPException(status_code=400, detail="无效的植物ID格式")
    except DoesNotExist:
        raise HTTPException(status_code=404, detail="未找到指定植物")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"创建地块失败: {str(e)}")


@plot_api.get("/{plotId}", response_model=PlotDetails)
async def get_plot_by_id(plotId: str, user: User = Depends(get_current_user)):
    try:
        # 获取地块信息，同时预加载植物信息和日志信息
        plot = await Plot.filter(
            plotId=uuid.UUID(plotId),
            userId=user.userId
        ).prefetch_related(
            'plantId',
            Prefetch('log', queryset=Log.all().order_by('timeStamp'))  # 按时间正序排序
        ).first()
        
        if not plot:
            raise HTTPException(status_code=404, detail="未找到地块或无权访问")

        # 验证图片是否合法
        icon_url = validate_image_file(plot.plantId.plantIconURL)
        
        # 构建日志列表
        logs = [
            LogDetail(
                logId=str(log.logId),
                timeStamp=log.timeStamp.strftime("%Y-%m-%d %H:%M:%S"),
                content=log.content,
                imagesURL=log.imagesURL
            )
            for log in plot.log
        ]
            
        return PlotDetails(
            plotId=str(plot.plotId),
            plotName=plot.plotName,
            plantId=str(plot.plantId.plantId),
            plantName=plot.plantId.plantName,
            plantFeature=plot.plantId.plantFeature,
            plantIconURL=icon_url,
            logs=logs
        )
    except ValueError:
        raise HTTPException(status_code=400, detail="无效的地块ID格式")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取地块详情失败: {str(e)}")


@plot_api.patch("/{plotId}")
async def update_plot_name(
    plotId: str,
    plotName: str = Body(...),
    user: User = Depends(get_current_user)
):
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
            "message": "地块改名成功"
        }
    except ValueError:
        raise HTTPException(status_code=400, detail="无效的地块ID格式")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"地块改名失败: {str(e)}")


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
