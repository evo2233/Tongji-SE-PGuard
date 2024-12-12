from fastapi import APIRouter, HTTPException
from Models.User import SignUpForm, SignInForm
from Models.models import User

user_api = APIRouter()

@user_api.post("/")
async def add_user(form: SignUpForm):
    try:
        # 先进行表单验证
        await form.name_must_be_unique(form.userName)
        
        # 创建新用户
        user = await User.create(
            userName=form.userName,
            password=form.password,
            location=form.location,
            sumCount=0,
        )
        return {"message": "用户创建成功", "user_id": user.userId}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@user_api.post("/login")
async def user_login(form: SignInForm):
    try:
        user = await User.get(userName=form.userName)
        if user.password == form.password:
            return {"message": "登录成功"}
        else:
            raise HTTPException(status_code=400, detail="密码错误")
    except Exception as e:
        raise HTTPException(status_code=400, detail="用户名或密码错误")