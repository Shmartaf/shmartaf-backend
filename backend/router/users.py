from datetime import datetime
from uuid import uuid4

from fastapi import APIRouter, HTTPException
from pydantic import UUID4

from backend.database import models, schemas
from backend.database.dal import DataAccessLayer
from backend.logger import ColorLogger

router = APIRouter(
    prefix="/users",
    tags=["users"],
)
logger = ColorLogger()

dal = DataAccessLayer()


@router.get("/")
def get_users(skip: int = 0, limit: int = 10) -> list[schemas.UserSchema]:
    return dal.get_all(models.User, skip=skip, limit=limit)


@router.get("/{user_id}")
def get_user(user_id: UUID4) -> schemas.UserSchema:
    if user := dal.get(model=models.User, id=user_id):
        return user
    raise HTTPException(status_code=404, detail="User not found")


@router.post("/")
def create_user(user: schemas.UserSchema) -> schemas.UserSchema:
    return dal.create(models.User, user)


@router.put("/{user_id}")
def update_user(
    user_id: UUID4,
    user: schemas.UserSchema,
) -> schemas.UserSchema:
    return dal.update(models.User, user_id, user)


@router.delete("/{user_id}")
def delete_user(user_id: UUID4) -> schemas.UserSchema:
    return dal.delete(models.User, user_id)


@router.post("/signup")
def signup(formData: schemas.SignUpSchema):
    # Create User
    user_schema = schemas.UserSchema(
        id=formData.id,
        name=formData.fullName,
        gender=formData.gender,
        email=formData.email,
        password=formData.password,
        registrationdate=datetime.now().date(),
        city=formData.city,
        street=formData.street,
        phone=formData.phone,
        userType=formData.userType,
    )
    user = dal.create(models.User, user_schema)

    if "parent" in formData.userType:

        # Create Parent
        parent_schema = schemas.ParentSchema(id=user.id, description=formData.parentDescription)
        parent = dal.create(models.Parent, parent_schema)
        if formData.children is None:
            # raise HTTPException(status_code=400, detail="Children are required")
            pass
        else:
            for child in formData.children:
                # Create Child
                child_schema = schemas.ChildrenRequestSchema(
                    id=uuid4().hex,
                    name=child["fullName"],
                    birthdate=child["birthdate"],
                    gender=child["gender"],
                )
                child = dal.create(models.Children, child_schema)

                # Assign Child to Parent
                # parent.childrens.append(child)
                parent_children_schema = schemas.ParentChildrenRequestSchema(childid=child.id, parentid=parent.id)
                dal.create(models.ParentsChildrens, parent_children_schema)

                # Assign Needs to Child
                for need in child.needs:

                    childrens_needs_schema = schemas.ChildReqirmentsRequestSchema(
                        childid=child.id, needid=need.id, needrank=1
                    )
                    dal.create(models.ChildrensNeeds, childrens_needs_schema)

    # Create Babysitter
    if "babysitter" in formData.userType:
        babysitter_schema = schemas.BabysitterRequestSchema(
            id=user.id, description=formData.babysitterDescription, pictureid=1
        )
        babysitter = dal.create(models.Babysitter, babysitter_schema)

        # Assign Skills to Babysitter
        for skill in enumerate(formData.babysitterSkills):
            index, (skillid, skill_name) = skill
            skill_rank = 3
            babysitter_skill_schema = schemas.BabysitterCerticationRequestSchema(
                id=skillid, babysitterid=babysitter.id, skillrank=skill_rank
            )
            dal.create(models.BabysitterSkill, babysitter_skill_schema)

    return user
