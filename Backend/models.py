from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from Backend.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    password = Column(String, nullable=False)
    enrollments = relationship("Enrollment", back_populates="user", cascade="all, delete")


class Course(Base):
    __tablename__ = "courses"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, unique=True, nullable=False)
    enrollments = relationship(
        "Enrollment",
        back_populates="course",
        cascade="all, delete"
    )
    topics = relationship(
        "CourseTopic",
        back_populates="course",
        cascade="all, delete"
    )


# ✅ FIXED: Added URL validation for YouTube links
class CourseTopic(Base):
    __tablename__ = "course_topics"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    link = Column(String, nullable=False)  # Should be a valid YouTube URL
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False)
    course = relationship("Course", back_populates="topics")
    
    def __repr__(self):
        return f"<CourseTopic(id={self.id}, title={self.title}, course_id={self.course_id})>"


class Enrollment(Base):
    __tablename__ = "enrollments"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False)
    user = relationship("User", back_populates="enrollments")
    course = relationship("Course", back_populates="enrollments")
    
    __table_args__ = (
        UniqueConstraint('user_id', 'course_id', name='unique_user_course_enrollment'),
    )
    
    def __repr__(self):
        return f"<Enrollment(user_id={self.user_id}, course_id={self.course_id})>"