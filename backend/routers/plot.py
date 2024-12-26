import uuid

from fastapi import APIRouter, Depends, HTTPException, Body
from models.models import User, Plot, Plant
from dependencies.auth import get_current_user
from routers import user

plot_api = APIRouter()


@plot_api.get("")
async def get_all_plots(user: User = Depends(get_current_user)):
    try:
        plots = await Plot.filter(userId=user.userId).all()
        return plots
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@plot_api.post("/add")
async def add_plot(
        plotName: str,
        plantId: str,
        user: User = Depends(get_current_user)
):
    try:
        plot = await Plot.create(
            plotName=plotName,
            userId=user.userId,
            plantId=uuid.UUID(plantId)
        )
        return plot
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@plot_api.get("/{plotId}")
async def get_plot_by_id(plotId: str, user: User = Depends(get_current_user)):
    try:
        plot = await Plot.get(plotId=uuid.UUID(plotId), userId=uuid.UUID(user.userId))

    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))


@plot_api.delete("/{plotId}")
async def delete_plot(plotId: str, user: User = Depends(get_current_user)):
    try:
        plot = await Plot.get(plotId=uuid.UUID(plotId), userId=uuid.UUID(user.userId))
        if plot == None:
            raise HTTPException(status_code=404, detail="未找到地块")
        await plot.delete()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
