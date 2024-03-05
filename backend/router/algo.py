from fastapi import APIRouter

from backend.database import schemas
from backend.database.dal import DataAccessLayer
from backend.send_parent_id import get_recommendations_for_parent

router = APIRouter(
    prefix="/algo",
    tags=["algo"],
)


dal = DataAccessLayer()


@router.get("/{user_id}")
def getBabysitterFromAlgo(user_id, skip: int = 0, limit: int = 1000) -> list[schemas.Recommendation]:
    return get_recommendations_for_parent(user_id).to_dict(orient="records")
