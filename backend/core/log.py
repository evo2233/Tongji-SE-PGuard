import datetime
from collections import defaultdict
from typing import List
from fastapi import HTTPException, Depends

from core.logController import call_get_prediction, call_get_user_plots, get_logs, minus
from core.userController import get_current_user
from models.models import User
from schemas.Map import DISEASE_NAME_RMAP
from schemas.form import PlotDetails


async def analyze_plot_details(plot_details: List[PlotDetails]):
    year = datetime.datetime.now().year
    plot_count = len(set(plot.plotId for plot in plot_details))

    # 统计每种植物占用的地块数量
    plant_plot_count = defaultdict(set)
    for plot in plot_details:
        plant_plot_count[plot.plantName].add(plot.plotId)
    plant_plot_count = {plant: len(plots) for plant, plots in plant_plot_count.items()}

    # Initialize counters
    monthly_disease_count = [0] * 12
    plant_disease_count = defaultdict(int)
    disease_count = defaultdict(int)

    for plot in plot_details:
        for log in plot.logs:
            try:
                # 跳过"健康"的检测记录
                if log.diseaseName in ["健康"]:
                    continue

                # 修改时间戳解析方式
                log_date = datetime.datetime.strptime(log.timeStamp.split('.')[0], "%Y-%m-%d %H:%M:%S")
                if log_date.year == year:
                    # Increment monthly count
                    monthly_disease_count[log_date.month - 1] += 1

                    # Increment plant-specific disease count
                    plant_disease_count[plot.plantName] += 1

                    # 统计每种疾病的发生次数
                    if log.diseaseName:  # 确保diseaseName不为空
                        disease_count[log.diseaseName] += 1

            except Exception as e:
                print(f"日期解析错误: {log.timeStamp}, 错误: {str(e)}")
                continue

    # 找出发生次数最多的病害
    most_common_disease = None
    max_count = 0
    for disease, count in disease_count.items():
        if count > max_count:
            max_count = count
            most_common_disease = disease

    diseaseName = DISEASE_NAME_RMAP.get(most_common_disease)
    prediction = await call_get_prediction(diseaseName)

    return {
        "plot_count": plot_count,
        "plant_plot_count": plant_plot_count,
        "monthly_disease_count": monthly_disease_count,
        "plant_disease_count": dict(plant_disease_count),
        "disease_count": dict(disease_count),
        "prediction": prediction
    }


async def get_summary(user: User = Depends(get_current_user)):
    try:
        if not minus(user):
            raise HTTPException(status_code=400, detail="余额不足，请充值")
        # 获取用户所有地块
        plots = await call_get_user_plots(user)
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
