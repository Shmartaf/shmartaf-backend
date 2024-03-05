from fastapi import APIRouter

from backend.database import models, schemas
from backend.database.dal import DataAccessLayer

router = APIRouter(
    prefix="/certifications",
    tags=["certifications"],
)


dal = DataAccessLayer()


@router.get("/")
def get_certifications(skip: int = 0, limit: int = 10) -> list[schemas.CertificationSchema]:
    return dal.get_all(models.SpecialSkill, skip=skip, limit=limit)


@router.post("/")
def create_certification(
    certification: schemas.CertificationSchema,
) -> schemas.CertificationSchema:
    return dal.create(models.SpecialSkill, certification)
