from fastapi import APIRouter, Depends

from app import schemas
from app.ai.category_classifier import predict_category, load_model
from app.deps import get_current_user
from app import models

router = APIRouter(prefix="/ai", tags=["ai"])


@router.post("/predict_category", response_model=schemas.PredictCategoryResponse)
def predict_category_endpoint(
    payload: schemas.PredictCategoryRequest,
    user: models.User = Depends(get_current_user),  # noqa: ARG001
):
    model = load_model()
    result = predict_category(payload.description, model=model)
    return schemas.PredictCategoryResponse(
        category_id=result.category_id,
        confidence=result.confidence,
        model_version=result.model_version,
        top_k=[schemas.CategoryScore(label=lbl, score=score) for lbl, score in result.top_k],
    )
