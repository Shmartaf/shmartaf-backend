from fastapi import APIRouter, HTTPException
from pydantic import UUID4

from backend.database import models, schemas
from backend.database.dal import DataAccessLayer

router = APIRouter(
    prefix="/parents",
    tags=["parents"],
)


dal = DataAccessLayer()


@router.get("/")
def get_parents(skip: int = 0, limit: int = 10) -> list[schemas.ParentResponseSchema]:
    return dal.get_all(models.Parent, skip=skip, limit=limit)


@router.get("/{parent_id}")
def get_parent(parent_id: UUID4) -> schemas.ParentResponseSchema:
    if parent := dal.get(models.Parent, parent_id):
        return parent
    raise HTTPException(status_code=404, detail="Parent not found")


@router.post("/")
def create_parent(parent: schemas.ParentSchema) -> schemas.ParentResponseSchema:
    return dal.create(models.Parent, parent)


@router.put("/{parent_id}")
def update_parent(parent_id: UUID4, parent: schemas.ParentSchema) -> schemas.ParentResponseSchema:
    db_parent = dal.get(model=models.Parent, id=parent_id)
    if db_parent is None:
        raise HTTPException(status_code=404, detail="Parent not found")
    return dal.update(models.Parent, parent_id, parent)


@router.delete("/{parent_id}")
def delete_parent(parent_id: UUID4):
    db_parent = dal.get(model=models.Parent, id=parent_id)
    if db_parent is None:
        raise HTTPException(status_code=404, detail="Parent not found")
    return dal.delete(models.Parent, parent_id)


@router.post("/{parent_id}/children")
def create_child(parent_id: UUID4, child: schemas.ChildrenRequestSchema):
    child = dal.create(models.Children, child)
    scheme = schemas.ParentChildrenRequestSchema(parentid=parent_id, childid=child.id)
    parentChildren = dal.create(models.ParentsChildrens, schema=scheme)
    return parentChildren


@router.put("/{parent_id}/children/{child_id}")
def assign_child_to_parent(parent_id: UUID4, child_id: UUID4):
    schem = schemas.ParentChildrenRequestSchema(parentid=parent_id, childid=child_id)
    parent_children = dal.create(models.ParentsChildrens, schema=schem)
    return parent_children


@router.post("/{parent_id}/contacted")
def create_contacted(parent_id: UUID4, contacted: schemas.ContactedRequestSchema):
    return dal.create(models.Contacted, contacted)


@router.post("/{parent_id}/favorites")
def create_favorite(parent_id: UUID4, favorite: schemas.FavoriteRequestSchema):
    return dal.create(models.Favorite, favorite)


@router.post("/{parent_id}/requirements/{child_id}/{requirements.id}")
def create_requirements(parent_id: UUID4, child_id: UUID4, requirements_id: UUID4, needrank: int):
    get_req = dal.get(models.SpecialNeed, requirements_id)
    if get_req is None:
        raise HTTPException(status_code=404, detail="Requirements not found")
    schema = schemas.ChildrenRequirementsSchema(
        needid=requirements_id,
        childid=child_id,
        needrank=needrank,
    )
    return dal.create(model=models.ChildrensNeeds, schema=schema)
