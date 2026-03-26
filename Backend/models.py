from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, UniqueConstraint, Date
from sqlalchemy.orm import relationship
from Backend.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    password = Column(String, nullable=False)
    enrollments = relationship("Enrollment", back_populates="user", cascade="all, delete")
    topic_progress = relationship("TopicProgress", back_populates="user", cascade="all, delete")
    login_streaks = relationship("LoginStreak", back_populates="user", cascade="all, delete")


class Course(Base):
    __tablename__ = "courses"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, unique=True, nullable=False)
    enrollments = relationship("Enrollment", back_populates="course", cascade="all, delete")
    topics = relationship("CourseTopic", back_populates="course", cascade="all, delete")


class CourseTopic(Base):
    __tablename__ = "course_topics"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    link = Column(String, nullable=False)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False)
    course = relationship("Course", back_populates="topics")


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


class TopicProgress(Base):
    """Stores which topics a user has completed — synced across devices via DB"""
    __tablename__ = "topic_progress"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    topic_id = Column(Integer, ForeignKey("course_topics.id"), nullable=False)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False)
    user = relationship("User", back_populates="topic_progress")

    __table_args__ = (
        UniqueConstraint('user_id', 'topic_id', name='unique_user_topic_progress'),
    )


class LoginStreak(Base):
    """Tracks daily login streak accurately per user"""
    __tablename__ = "login_streaks"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, unique=True)
    streak = Column(Integer, default=1, nullable=False)
    last_login = Column(Date, nullable=True)
    user = relationship("User", back_populates="login_streaks")