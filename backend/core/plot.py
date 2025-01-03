import os
import uuid
from fastapi import HTTPException, Depends, Body
from tortoise.exceptions import DoesNotExist

from core.config import RESOURCE_PATH, ALLOWED_IMAGE_TYPES

from models.models import Plant, Plot, User
from core.plotController import get_user_plots, call_get_logs
from core.userController import get_current_user
from schemas.form import PlotDetails


def validate_image_file(url: str):
    icon_path = os.path.join(RESOURCE_PATH, url)

    # 检查文件是否存在
    if not os.path.exists(icon_path):
        return "图片不存在"

    # 检查文件扩展名
    file_ext = os.path.splitext(icon_path)[1].lower()
    if file_ext not in ALLOWED_IMAGE_TYPES:
        return "不支持此拓展名"
    return f"/resource/{url}"


async def get_all_plots(user: User = Depends(get_current_user)):
    try:
        plots = await get_user_plots(user)

        # 检查 plots 是否为 None 或空列表
        if not plots:
            return {"message": "当前地块列表为空，尚未创建地块"}

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
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取地块失败: {str(e)}")


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
            userId=user,
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


async def get_plot_detail(plotId: str, user: User = Depends(get_current_user)):
    try:
        plot_uuid = uuid.UUID(plotId)

        # 获取地块信息，同时预加载植物信息
        plot = await Plot.filter(
            plotId=plot_uuid,
            userId=user.userId
        ).prefetch_related('plantId').first()

        if not plot:
            raise HTTPException(status_code=404, detail="未找到地块或无权访问")

        # 验证图片是否合法
        icon_url = validate_image_file(plot.plantId.plantIconURL)
        # 获取地块所有日志
        logs = await call_get_logs(plotId)

        return PlotDetails(
            plotId=str(plot.plotId),
            plotName=plot.plotName,
            plantId=str(plot.plantId.plantId),
            plantName=plot.plantId.plantName,
            plantFeature=plot.plantId.plantFeature,
            plantIconURL=icon_url,
            logs=logs
        )
    except ValueError as ve:
        print(f"ValueError异常: {str(ve)}")
        raise HTTPException(status_code=400, detail=f"无效的地块ID格式: {str(ve)}")
    except Exception as e:
        print(f"其他异常: {str(e)}, 类型: {type(e)}")
        raise HTTPException(status_code=500, detail=f"获取地块详情失败: {str(e)}")


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
