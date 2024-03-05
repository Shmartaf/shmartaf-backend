from typing import List

from fastapi import APIRouter, HTTPException
from pydantic import UUID4

from backend.database import models, schemas
from backend.database.dal import DataAccessLayer

router = APIRouter(
    prefix="/babysitters",
    tags=["babysitters"],
)


dal = DataAccessLayer()


@router.get("/")
def get_babysitters(skip: int = 0, limit: int = 10) -> List[schemas.BabysitterSchema]:
    return dal.get_all(models.Babysitter, skip=skip, limit=limit)


@router.get("/{babysitter_id}")
def get_babysitter(babysitter_id: UUID4) -> schemas.BabysitterSchema:
    if babysitter := dal.get(models.Babysitter, babysitter_id):
        return babysitter
    raise HTTPException(status_code=404, detail="Babysitter not found")


@router.post("/")
def create_babysitter(
    babysitter: schemas.BabysitterRequestSchema,
) -> schemas.BabysitterSchema:
    return dal.create(models.Babysitter, babysitter)


@router.put("/{babysitter_id}")
def update_babysitter(
    babysitter_id: UUID4,
    babysitter: schemas.BabysitterSchema,
) -> schemas.BabysitterSchema:
    return dal.update(models.Babysitter, babysitter_id, babysitter)


@router.delete("/{babysitter_id}")
def delete_babysitter(babysitter_id: UUID4) -> schemas.BabysitterSchema:
    return dal.delete(models.Babysitter, babysitter_id)


@router.post("/{babysitter_id}/certifications/{certification_id}")
def create_certification(
    babysitter_id: UUID4, certification_id: UUID4, skillrank: int
) -> schemas.BabysitterCertificationSchema:
    scheme = schemas.BabysitterCertificationSchema(
        babysitterid=babysitter_id,
        id=certification_id,
        skillrank=skillrank,
    )
    if dal.get(models.SpecialSkill, certification_id) is None:
        raise HTTPException(status_code=404, detail="Certification not found")
    return dal.create(models.BabysitterSkill, scheme)
