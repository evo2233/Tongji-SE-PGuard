from fastapi import HTTPException
from models.models import Plot


async def get_plot_by_id(plotId: str):
    try:
        # 同时预加载 userId 和 plantId 的关联数据
        plot = await Plot.get(plotId=plotId).select_related("userId", "plantId")
        if plot:
            return plot
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))