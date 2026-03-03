from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from Backend.database import Base

class User(Base):
    __tablename__="users"

    id=Column(Integer, primary_key=True, index=True)
    name=Column(String)
    email=Column(String, unique=True,index=True,nullable=False)
    password=Column(String,nullable=False)
    enrollments=relationship("Enrollment",back_populates="user")


class Course(Base):
    __tablename__="courses"

    id=Column(Integer, primary_key=True,index=True)
    title=Column(String, unique=True)
    enrollments=relationship(
        "Enrollment",
        back_populates="course",
        cascade="all, delete"
    )
    topics=relationship(
        "CourseTopic",
        back_populates="course",
        cascade="all, delete"
    )


class CourseTopic(Base):
    __tablename__="course_topics"

    id=Column(Integer, primary_key=True,index=True)
    title=Column(String)
    link=Column(String)
    course_id=Column(Integer, ForeignKey("courses.id"))
    course=relationship("Course",back_populates="topics")


class Enrollment(Base):
    __tablename__="enrollments"

    id=Column(Integer,primary_key=True,index=True)
    user_id=Column(Integer,ForeignKey("users.id"))
    course_id=Column(Integer,ForeignKey("courses.id"))
    user=relationship("User",back_populates="enrollments")
    course=relationship("Course",back_populates="enrollments")
    __table_args__ = (
        UniqueConstraint('user_id','course_id'),
    )