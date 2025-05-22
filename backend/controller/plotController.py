from fastapi import APIRouter, Depends, Body
from models.models import User
from core.auth import get_current_user
from typing import List
from models.form import PlotDetails
from service.plotService import all_plant_name, all_plot, create_plot, make_plot_detail, change_plot_name, del_plot

plot_api = APIRouter()


@plot_api.get('/plant', response_model=List[str])
async def get_all_plant_types():
    return await all_plant_name()


@plot_api.get("")
async def get_all_plots(user: User = Depends(get_current_user)):
    return await all_plot(user)


@plot_api.post("/add")
async def add_plot(
    plotName: str = Body(...),
    plantName: str = Body(...),
    user: User = Depends(get_current_user)
):
    return await create_plot(plotName, plantName, user)


@plot_api.get("/{plotId}", response_model=PlotDetails)
async def get_plot_detail(plotId: str, user: User = Depends(get_current_user)):
    return await make_plot_detail(plotId, user)


@plot_api.patch("/{plotId}")
async def update_plot_name(
    plotId: str,
    plotName: str = Body(...),
    user: User = Depends(get_current_user)
):
    return await change_plot_name(plotId, plotName, user)


@plot_api.delete("/{plotId}")
async def delete_plot(plotId: str, user: User = Depends(get_current_user)):
    return await del_plot(plotId, user)
