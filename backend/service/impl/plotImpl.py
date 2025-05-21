from fastapi import HTTPException, Depends
from core.auth import get_current_user
from models.models import Plot, User


async def get_plot_by_id(plotId: str):
    try:
        # 同时预加载 userId 和 plantId 的关联数据
        plot = await Plot.get(plotId=plotId).select_related("userId", "plantId")

        if plot:
            return plot

    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))


async def get_plot_by_user(user: User = Depends(get_current_user)):
    try:
        plots = await Plot.filter(userId=user.userId).prefetch_related('plantId').all()

        if plots:
            return plots

    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))
