import uuid
from fastapi import HTTPException, Depends
from tortoise.query_utils import Prefetch

from models.models import Plot, Log, User
from schemas.form import LogDetail
from core.userController import get_current_user, minus_sum_count
from core.plotController import get_user_plots
from core.detectController import get_prediction_by_name


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


async def call_get_user_plots(user: User = Depends(get_current_user)):
    return await get_user_plots(user)


async def call_get_prediction(diseaseName: str):
    return await get_prediction_by_name(diseaseName)


async def minus(user: User = Depends(get_current_user)):
    return await minus_sum_count(user)
