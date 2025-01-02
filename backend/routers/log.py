from fastapi import APIRouter, HTTPException, Depends
from routers.logController import analyze_plot_details, get_logs
from routers.plotController import get_plot_by_user
from schemas.form import PlotDetails
from dependencies.auth import get_current_user
from models.models import User


log_api = APIRouter()


@log_api.get('/summary')
async def get_summary(user: User = Depends(get_current_user)):
    try:
        # 获取用户所有地块
        plots = await get_plot_by_user(user)
        if not plots:
            return {
                "plot_count": 0,
                "plant_plot_count": {},
                "monthly_disease_count": [0] * 12,
                "plant_disease_count": {}
            }

        # 构建PlotDetails列表
        plot_details = []
        for plot in plots:
            # 获取地块的所有日志
            logs = await get_logs(str(plot.plotId))
            
            plot_details.append(PlotDetails(
                plotId=str(plot.plotId),
                plotName=plot.plotName,
                plantId=str(plot.plantId.plantId),
                plantName=plot.plantId.plantName,
                plantFeature=plot.plantId.plantFeature,
                plantIconURL=plot.plantId.plantIconURL,
                logs=logs
            ))

        # 分析所有地块的统计信息
        summary = await analyze_plot_details(plot_details)
        return summary

    except Exception as e:
        print(f"获取统计信息失败: {str(e)}")  # 调试输出
        raise HTTPException(status_code=500, detail=f"获取统计信息失败: {str(e)}")
