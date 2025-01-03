from fastapi import APIRouter, Depends, Body
from typing import List

from core.dependency import get_current_user

from schemas.form import PlotDetails
from models.models import User

import service.plot as p
import service.plant as pl


plot_api = APIRouter()


@plot_api.get('/plant', response_model=List[str])
async def get_all_plant_types():
    return await pl.get_all_plant_types()


@plot_api.get("")
async def get_all_plots(user: User = Depends(get_current_user)):
    return await p.get_all_plots(user)


@plot_api.post("/add")
async def add_plot(
    plotName: str = Body(...),
    plantName: str = Body(...),
    user: User = Depends(get_current_user)
):
    return await p.add_plot(plotName, plantName, user)


@plot_api.get("/{plotId}", response_model=PlotDetails)
async def get_plot_detail(plotId: str, user: User = Depends(get_current_user)):
    return await p.get_plot_detail(plotId, user)


@plot_api.patch("/{plotId}")
async def update_plot_name(
    plotId: str,
    plotName: str = Body(...),
    user: User = Depends(get_current_user)
):
    return await p.update_plot_name(plotId, plotName, user)


@plot_api.delete("/{plotId}")
async def delete_plot(plotId: str, user: User = Depends(get_current_user)):
    return await p.delete_plot(plotId, user)
