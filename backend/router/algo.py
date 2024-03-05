from fastapi import APIRouter

from backend.database.dal import DataAccessLayer
from backend.database.faker_db import (
    mock_contacted,
    mock_db,
    mock_needs_skills,
    schemas,
)
from backend.send_parent_id import get_recommendations_for_parent

router = APIRouter(
    prefix="/algo",
    tags=["algo"],
)


dal = DataAccessLayer()


@router.get("/{user_id}")
async def getBabysitterFromAlgo(user_id, skip: int = 0, limit: int = 1000) -> list[schemas.Recommendation]:
    return await get_recommendations_for_parent(user_id).to_dict(orient="records")


@router.get("/babysitter/{user_id}")
def getParentsFromAlgo(user_id, skip: int = 0, limit: int = 1000) -> list[schemas.Recommendation]:
    return get_recommendations_for_parent(user_id).to_dict(orient="records")


@router.get("/train")
def train():
    return "train"


@router.get("/faker")
def faker(amount: int = 100):
    mock_db(amount)
    mock_needs_skills()
    mock_contacted()
    return "faker complete successfully"
