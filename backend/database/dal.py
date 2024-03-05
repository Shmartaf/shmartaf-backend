# from backend.database import models, schemas

from pydantic import UUID4

from backend.database.database import Database
from backend.logger import ColorLogger


class DataAccessLayer:
    def __init__(self):
        self.db = next(Database().get_db())
        self.logger = ColorLogger()

    def get(self, model, id: UUID4):
        try:
            result = self.db.query(model).filter(model.id == id).first()
            self.logger.log(message=f"Get {model.__name__} with id {id}", level="INFO", data=result)
            return result
        except Exception as e:
            self.logger.log(
                message=f"Get {model.__name__} with id {id} failed",
                level="ERROR",
                data=str(e),
            )
            self.db.rollback()
            return None

    def get_all(self, model, skip: int = 0, limit: int = 100):
        try:
            result = self.db.query(model).offset(skip).limit(limit).all()
            self.logger.log(message=f"Get all {model.__name__}", level="INFO", data=result)
            return result
        except Exception as e:
            self.logger.log(
                message=f"Get all {model.__name__} failed",
                level="ERROR",
                data=str(e),
            )
            self.db.rollback()
            return None

    def create(self, model, schema):
        try:
            db_model = model(**schema.dict())
            self.db.add(db_model)
            self.db.commit()
            self.db.refresh(db_model)
            self.logger.log(
                message=f"Create {model.__name__} with id {db_model.id}",
                level="INFO",
                data=db_model,
            )
            return db_model
        except Exception as e:
            self.logger.log(
                message=f"Create {model.__name__} failed",
                level="ERROR",
                data=str(e),
            )
            self.db.rollback()
            return None

    def update(self, model, id: int, schema):
        try:
            db_model = self.get(model, id)
            for var, value in schema.dict().items():
                setattr(db_model, var, value)
            self.db.commit()
            self.db.refresh(db_model)
            self.logger.log(
                message=f"Update {model.__name__} with id {id}",
                level="INFO",
                data=db_model,
            )
            return db_model
        except Exception as e:
            self.logger.log(
                message=f"Update {model.__name__} with id {id} failed",
                level="ERROR",
                data=str(e),
            )
            self.db.rollback()
            return None

    def delete(self, model, id: int):
        try:
            db_model = self.get(model, id)
            self.db.delete(db_model)
            self.db.commit()
            self.logger.log(
                message=f"Delete {model.__name__} with id {id}",
                level="INFO",
                data=db_model,
            )
            return db_model
        except Exception as e:
            self.logger.log(
                message=f"Delete {model.__name__} with id {id} failed",
                level="ERROR",
                data=str(e),
            )
            self.db.rollback()
            return None

    def aggregate(self, model, id: int, field: str):
        try:
            result = self.db.query(model).filter(getattr(model, field) == id).all()
            self.logger.log(
                message=f"Get {model.__name__} with {field} {id}",
                level="INFO",
                data=result,
            )
            return result
        except Exception as e:
            self.logger.log(
                message=f"Get {model.__name__} with {field} {id} failed",
                level="ERROR",
                data=str(e),
            )
            self.db.rollback()
            return None
