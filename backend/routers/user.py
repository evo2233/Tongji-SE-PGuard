from fastapi import APIRouter, Depends, Body
from typing import List

from core.dependency import get_current_user, oauth2_scheme

from schemas.form import SignUpForm, SignInForm
from models.models import User

import service.user as u
import service.package as pk
import service.city as c


user_api = APIRouter()


@user_api.get('/city/{keyword}')
async def search_city(keyword: str):
    return await c.search_city(keyword)


@user_api.get('/city')
async def get_user_city(user: User = Depends(get_current_user)):
    return await c.get_city_by_name(user)


@user_api.post("/signup")
async def signup(form: SignUpForm):
    return await u.create_user(form)


@user_api.post("/signin")
async def signin(form: SignInForm):
    return await u.get_token(form)


@user_api.post("/refresh")
async def refresh_token(current_token: str = Depends(oauth2_scheme), refresh_token: str = Body(...)):
    return await u.refresh_token(current_token, refresh_token)


@user_api.get("/me")
async def get_user(current_user: User = Depends(get_current_user)):
    return await u.get_user(current_user)


@user_api.patch("/update")
async def update_user(form: SignUpForm, user: User = Depends(get_current_user)):
    return await u.update_user(form, user)


@user_api.post("/logout")
async def logout(current_token: str = Depends(oauth2_scheme)):
    return await u.logout(current_token)


@user_api.get('/package', response_model=List[dict])
async def get_all_packages():
    return await pk.get_all_packages()


@user_api.post("/recharge/{package_id}")
async def purchase(package_id: str, user: User = Depends(get_current_user)):
    return await pk.purchase(package_id, user)
