from fastapi import HTTPException
from models.models import Disease


async def get_prediction_by_name(diseaseName: str):
    try:
        disease = await Disease.filter(diseaseName=diseaseName).first()
        if disease:
            return disease.prediction
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))
