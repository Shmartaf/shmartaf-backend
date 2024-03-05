from uuid import uuid4

from sqlalchemy import (
    Column,
    Date,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    Time,
    Uuid,
)
from sqlalchemy.orm import relationship

from backend.database.database import Database

db = Database()
Base = db.Base


class User(Base):
    __tablename__ = "users"

    id = Column(
        Uuid,
        primary_key=True,
        default=uuid4().hex,
        unique=True,
        nullable=False,
    )
    name = Column(String(255))
    gender = Column(String(10))
    email = Column(String(255))
    password = Column(String(255))
    registrationdate = Column(Date)
    city = Column(String(255))
    street = Column(String(255))
    phone = Column(String(30))
    userType = Column(String(255))
    parent = relationship("Parent", uselist=False, back_populates="user")
    babysitter = relationship("Babysitter", uselist=False, back_populates="user")


class Babysitter(Base):
    __tablename__ = "babysitter"

    id = Column(
        Uuid,
        ForeignKey("users.id"),
        primary_key=True,
        unique=True,
        nullable=False,
    )
    pictureid = Column(Integer)
    description = Column(Text)
    user = relationship("User", back_populates="babysitter")
    skills = relationship("BabysitterSkill", back_populates="babysitter")
    contacted = relationship("Contacted", back_populates="babysitter")
    schedules = relationship(
        "Scheduler",
        back_populates="babysitter",
        order_by="Scheduler.dayinweek, Scheduler.starttime",
    )
    favorites = relationship("Favorite", back_populates="babysitter")


class Parent(Base):
    __tablename__ = "parent"
    id = Column(Uuid, ForeignKey("users.id"), primary_key=True)
    description = Column(Text)
    user = relationship("User", back_populates="parent")
    childrens = relationship("Children", secondary="parents_childrens", back_populates="parents")
    favorites = relationship("Favorite", back_populates="parent")
    contacted = relationship("Contacted", back_populates="parent")


class Children(Base):
    __tablename__ = "children"
    id = Column(Uuid, primary_key=True)
    name = Column(String(255))
    birthdate = Column(Date)
    gender = Column(String(10))
    parents = relationship("Parent", secondary="parents_childrens", back_populates="childrens")
    needs = relationship("ChildrensNeeds", back_populates="child")


class ParentsChildrens(Base):
    __tablename__ = "parents_childrens"

    childid = Column(Uuid, ForeignKey("children.id"), primary_key=True)
    parentid = Column(Uuid, ForeignKey("parent.id"), primary_key=True)


class Review(Base):
    __tablename__ = "reviews"

    id = Column(Uuid, primary_key=True, default=uuid4().hex)
    reviewerid = Column(Uuid, ForeignKey("users.id"))
    reviewedid = Column(Uuid, ForeignKey("users.id"))
    rating = Column(Float)
    flexibilityrating = Column(Float)
    reliabilityrating = Column(Float)
    interpersonalrating = Column(Float)
    comment = Column(Text)
    registrationdate = Column(Date)
    reviewer = relationship("User", foreign_keys=[reviewerid])
    reviewed = relationship("User", foreign_keys=[reviewedid])


class SpecialNeed(Base):
    __tablename__ = "specialneed"

    id = Column(Uuid, primary_key=True, default=uuid4().hex)
    needname = Column(String(255))
    children_needs = relationship("ChildrensNeeds", back_populates="need")
    need_skills = relationship("NeedSkill", back_populates="need")


class SpecialSkill(Base):
    __tablename__ = "specialskill"

    id = Column(Uuid, primary_key=True, default=uuid4().hex)
    skillname = Column(String(255))
    skill_needs = relationship("NeedSkill", back_populates="skill")


class ChildrensNeeds(Base):
    __tablename__ = "childrens_needs"

    childid = Column(Uuid, ForeignKey("children.id"), primary_key=True)
    needid = Column(Uuid, ForeignKey("specialneed.id"), primary_key=True)
    needrank = Column(Integer)
    child = relationship("Children", back_populates="needs")
    need = relationship("SpecialNeed", back_populates="children_needs")
    # need = relationship("SpecialNeed", back_populates="need")


class BabysitterSkill(Base):
    __tablename__ = "babysitterskill"

    id = Column(Uuid, ForeignKey("specialskill.id"), primary_key=True)
    babysitterid = Column(Uuid, ForeignKey("babysitter.id"), primary_key=True)
    skillrank = Column(Integer)
    skill = relationship("SpecialSkill")
    babysitter = relationship("Babysitter", back_populates="skills")


class NeedSkill(Base):
    __tablename__ = "need_skill"

    needid = Column(Uuid, ForeignKey("specialneed.id"), primary_key=True)
    skillid = Column(Uuid, ForeignKey("specialskill.id"), primary_key=True)
    need = relationship("SpecialNeed", back_populates="need_skills")
    skill = relationship("SpecialSkill", back_populates="skill_needs")


class Favorite(Base):
    __tablename__ = "favorites"

    parentid = Column(Uuid, ForeignKey("parent.id"), primary_key=True)
    babysitterid = Column(Uuid, ForeignKey("babysitter.id"), primary_key=True)
    parent = relationship("Parent", back_populates="favorites")
    babysitter = relationship("Babysitter", back_populates="favorites")


class Contacted(Base):
    __tablename__ = "contacted"

    id = Column(Uuid, primary_key=True, default=uuid4().hex)
    parentid = Column(Uuid, ForeignKey("parent.id"))
    babysitterid = Column(Uuid, ForeignKey("babysitter.id"))
    date = Column(Date)
    parent = relationship("Parent", back_populates="contacted")
    babysitter = relationship("Babysitter", back_populates="contacted")


class Scheduler(Base):
    __tablename__ = "scheduler"

    babysitterid = Column(Uuid, ForeignKey("babysitter.id"), primary_key=True)
    dayinweek = Column(String(10), primary_key=True)
    starttime = Column(Time, primary_key=True)
    endtime = Column(Time)
    babysitter = relationship("Babysitter", back_populates="schedules")
