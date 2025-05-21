from fastapi import APIRouter, Depends, Body
from core.auth import get_current_user, oauth2_scheme
from models.models import User
from models.form import SignUpForm, SignInForm
from typing import List

from service.userService import get_city, get_city_code, add_user, generate_token, renew_token, change_user_info, \
    black_token, all_package, buy_package

user_api = APIRouter()


@user_api.get('/city/{keyword}')
async def search_city(keyword: str):
    await get_city(keyword)


@user_api.get('/city')
async def get_user_city_code(user: User = Depends(get_current_user)):
    await get_city_code(user)


@user_api.post("/signup")
async def create_user(form: SignUpForm):
    await add_user(form)


@user_api.post("/signin")
async def get_token(form: SignInForm):
    await generate_token(form)


@user_api.post("/refresh")
async def refresh_token(current_token: str = Depends(oauth2_scheme), refresh_token: str = Body(...)):
    await renew_token(current_token, refresh_token)


@user_api.get("/me")
async def get_user(current_user: User = Depends(get_current_user)):
    return {
        "userId": str(current_user.userId),
        "userName": current_user.userName,
        "location": current_user.location,
        "sumCount": current_user.sumCount
    }


@user_api.patch("/update")
async def update_user(form: SignUpForm, user: User = Depends(get_current_user)):
    await change_user_info(form, user)


@user_api.post("/logout")
async def logout(current_token: str = Depends(oauth2_scheme)):
    await black_token(current_token)


@user_api.get('/package', response_model=List[dict])
async def get_all_packages():
    await all_package()


@user_api.post("/recharge/{package_id}")
async def purchase(package_id: str, user: User = Depends(get_current_user)):
    await buy_package(package_id, user)
