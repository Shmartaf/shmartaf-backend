from fastapi import APIRouter

from backend.database import models, schemas
from backend.database.dal import DataAccessLayer

router = APIRouter(
    prefix="/requirements",
    tags=["requirements"],
)


dal = DataAccessLayer()


@router.post("/")
def create_requirements(
    requirements: schemas.RequirementsSchema,
) -> schemas.RequirementsSchema:
    return dal.create(models.SpecialNeed, requirements)


@router.get("/")
def get_requirements(skip: int = 0, limit: int = 10) -> list[schemas.RequirementsSchema]:
    return dal.get_all(models.SpecialNeed, skip=skip, limit=limit)
