import datetime
import uuid
from collections import defaultdict
from typing import List
from fastapi import HTTPException
from tortoise.query_utils import Prefetch
from models.models import Plot, Log
from routers.detectController import get_prediction_by_name
from schemas.form import LogDetail, PlotDetails
from schemas.Map import DISEASE_NAME_RMAP


async def set_log(
        plotId: str,
        diseaseName: str,
        advice: str,
        imageURL: str
):
    try:
        plot = await Plot.get(plotId=plotId)
        content = f"检测到{diseaseName}，建议：{advice}"

        await Log.create(
            plotId=plot,
            diseaseName=diseaseName,
            content=content,
            imagesURL=imageURL
        )

        return "创建日志成功"
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"创建日志失败: {str(e)}")


async def get_logs(plotId: str):
    # 获取地块，同时预加载日志信息（按时间正序排列）
    plot = await (Plot.filter(plotId=uuid.UUID(plotId))
                  .prefetch_related(Prefetch('log', queryset=Log.all().order_by('timeStamp'))).first())
    # 构建日志列表
    logs = [
        LogDetail(
            logId=str(log.logId),
            timeStamp=log.timeStamp.strftime("%Y-%m-%d %H:%M:%S"),
            diseaseName=log.diseaseName,
            content=log.content,
            imagesURL=log.imagesURL
        )
        for log in plot.log
    ]
    return logs


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
    prediction = await get_prediction_by_name(diseaseName)

    return {
        "plot_count": plot_count,
        "plant_plot_count": plant_plot_count,
        "monthly_disease_count": monthly_disease_count,
        "plant_disease_count": dict(plant_disease_count),
        "disease_count": dict(disease_count),
        "prediction": prediction
    }
