import uuid
from fastapi import HTTPException, Depends

from core.dependency import get_current_user

from models.models import Package, User


async def get_all_packages():
    try:
        packages = await Package.all()
        return [
            {
                "packageId": str(package.packageId),
                "packageName": package.packageName,
                "price": package.price,
                "sumNum": package.sumNum
            }
            for package in packages
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取套餐列表失败: {str(e)}")


async def purchase(package_id: str, user: User = Depends(get_current_user)):
    try:
        package = await Package.get(packageId=uuid.UUID(package_id))
        user.sumCount += package.sumNum
        await user.save()
        return {"packageId": package_id, "sumCount": user.sumCount}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
