from fastapi import HTTPException, Depends

from controller.logController import set_log
from core.dependency import get_current_user

from controller.plotController import get_plot_by_id
from models.models import User, Disease


async def validate_plot_access(plotId: str, user: User = Depends(get_current_user)):
    # 验证地块访问权限
    try:
        plot = await get_plot_by_id(plotId)
        if plot.userId.userId != user.userId:
            raise HTTPException(status_code=403, detail=f"未授权的地块访问")
        return plot
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"地块验证失败: {str(e)}")


async def call_set_log(plotId: str, name: str, advice: str, save_path: str):
    return await set_log(plotId, name, advice, save_path)


async def get_prediction_by_name(diseaseName: str):
    try:
        disease = await Disease.filter(diseaseName=diseaseName).first()
        if disease:
            return disease.prediction
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))
