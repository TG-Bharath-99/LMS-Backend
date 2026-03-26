from fastapi import APIRouter, HTTPException, Depends
from Backend.database import SessionLocal
from Backend.models import User, Course, Enrollment, CourseTopic, TopicProgress, LoginStreak
from Backend.schemas import Signup, Login
from Backend.security import hash_password, verify_password
from Backend.auth import create_access_token, get_current_user
from datetime import date

router = APIRouter()

# ─── Auth ────────────────────────────────────────────────────

@router.post("/signup")
def signup(user: Signup):
    db = SessionLocal()
    try:
        existing = db.query(User).filter(User.email == user.email).first()
        if existing:
            raise HTTPException(status_code=400, detail="Email already exists")
        new_user = User(
            name=user.name,
            email=user.email,
            password=hash_password(user.password)
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        return {
            "name": new_user.name,
            "email": new_user.email,
            "message": "Signup successfully completed"
        }
    finally:
        db.close()

@router.post("/login")
def login(user: Login):
    db = SessionLocal()
    try:
        db_user = db.query(User).filter(User.email == user.email).first()
        if not db_user:
            raise HTTPException(status_code=404, detail="User not found")
        if not verify_password(user.password, db_user.password):
            raise HTTPException(status_code=401, detail="Invalid password")
        token = create_access_token({"sub": db_user.email})
        return {"access_token": token, "token_type": "bearer"}
    finally:
        db.close()

@router.get("/me")
def get_my_profile(current_user: str = Depends(get_current_user)):
    return {"logged_in_as": current_user}

# ─── Users ───────────────────────────────────────────────────

@router.get("/users")
def get_users(current_user: str = Depends(get_current_user)):
    db = SessionLocal()
    try:
        users = db.query(User).all()
        return [{"id": u.id, "name": u.name, "email": u.email} for u in users]
    finally:
        db.close()

@router.get("/users/{user_email}")
def get_user_by_email(user_email: str, current_user: str = Depends(get_current_user)):
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.email == user_email).first()
        if not user:
            raise HTTPException(status_code=404, detail="Not found")
        return {"id": user.id, "name": user.name, "email": user.email}
    finally:
        db.close()

@router.put("/users/{user_email}")
def update_user(user_email: str, user: Signup, current_user: str = Depends(get_current_user)):
    if current_user != user_email:
        raise HTTPException(status_code=403, detail="Not allowed")
    db = SessionLocal()
    try:
        db_user = db.query(User).filter(User.email == user_email).first()
        if not db_user:
            raise HTTPException(status_code=404, detail="User not found")
        db_user.name = user.name
        db_user.password = hash_password(user.password)
        db.commit()
        db.refresh(db_user)
        return {
            "message": "User updated",
            "user": {"id": db_user.id, "name": db_user.name, "email": db_user.email}
        }
    finally:
        db.close()

@router.delete("/users/{user_email}")
def delete_user(user_email: str, current_user: str = Depends(get_current_user)):
    if current_user != user_email:
        raise HTTPException(status_code=403, detail="Not allowed")
    db = SessionLocal()
    try:
        db_user = db.query(User).filter(User.email == user_email).first()
        if not db_user:
            raise HTTPException(status_code=404, detail="User not found")
        db.delete(db_user)
        db.commit()
        return {"message": "User deleted successfully"}
    finally:
        db.close()

# ─── Courses ─────────────────────────────────────────────────

@router.get("/courses")
def get_courses():
    db = SessionLocal()
    try:
        courses = db.query(Course).all()
        if not courses:
            return {"message": "No courses available"}
        return [{"id": c.id, "title": c.title} for c in courses]
    finally:
        db.close()

@router.get("/courses/{course_id}/topics")
def get_course_topics(course_id: int, current_user: str = Depends(get_current_user)):
    db = SessionLocal()
    try:
        course = db.query(Course).filter(Course.id == course_id).first()
        if not course:
            raise HTTPException(status_code=404, detail="Course not found")
        topics = db.query(CourseTopic).filter(CourseTopic.course_id == course_id).all()
        if not topics:
            return {"topics": []}
        return {
            "topics": [
                {"id": t.id, "title": t.title, "link": t.link}
                for t in topics
            ]
        }
    finally:
        db.close()

@router.post("/enroll/{course_id}")
def enroll_course(course_id: int, current_user: str = Depends(get_current_user)):
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.email == current_user).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        course = db.query(Course).filter(Course.id == course_id).first()
        if not course:
            raise HTTPException(status_code=404, detail="Course not found")
        existing = db.query(Enrollment).filter(
            Enrollment.user_id == user.id,
            Enrollment.course_id == course_id
        ).first()
        if existing:
            raise HTTPException(status_code=400, detail="Already enrolled")
        enrollment = Enrollment(user_id=user.id, course_id=course_id)
        db.add(enrollment)
        db.commit()
        return {"message": "Enrolled successfully"}
    finally:
        db.close()

@router.get("/my-courses")
def my_courses(current_user: str = Depends(get_current_user)):
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.email == current_user).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        enrollments = db.query(Enrollment).filter(Enrollment.user_id == user.id).all()
        course_ids = [e.course_id for e in enrollments]
        if not course_ids:
            return []
        courses = db.query(Course).filter(Course.id.in_(course_ids)).all()
        return [{"id": c.id, "title": c.title} for c in courses]
    finally:
        db.close()

# ─── Topic Progress (cross-device sync) ──────────────────────

@router.post("/progress/{topic_id}")
def mark_topic_complete(topic_id: int, current_user: str = Depends(get_current_user)):
    """Mark a topic as completed — stored in DB so it syncs across all devices"""
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.email == current_user).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        topic = db.query(CourseTopic).filter(CourseTopic.id == topic_id).first()
        if not topic:
            raise HTTPException(status_code=404, detail="Topic not found")

        existing = db.query(TopicProgress).filter(
            TopicProgress.user_id == user.id,
            TopicProgress.topic_id == topic_id
        ).first()

        if existing:
            return {"message": "Already marked complete"}

        progress = TopicProgress(
            user_id=user.id,
            topic_id=topic_id,
            course_id=topic.course_id
        )
        db.add(progress)
        db.commit()
        return {"message": "Topic marked as complete"}
    finally:
        db.close()

@router.get("/progress/{course_id}")
def get_course_progress(course_id: int, current_user: str = Depends(get_current_user)):
    """Get list of completed topic IDs for a course — works on any device"""
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.email == current_user).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        completed = db.query(TopicProgress).filter(
            TopicProgress.user_id == user.id,
            TopicProgress.course_id == course_id
        ).all()

        return {"completed_topic_ids": [p.topic_id for p in completed]}
    finally:
        db.close()

# ─── Real Login Streak ────────────────────────────────────────

@router.post("/streak")
def update_streak(current_user: str = Depends(get_current_user)):
    """
    Called on every login/dashboard load.
    - Same day: no change
    - Next day: streak + 1
    - Missed a day: streak resets to 1
    """
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.email == current_user).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        today = date.today()
        streak_record = db.query(LoginStreak).filter(LoginStreak.user_id == user.id).first()

        if not streak_record:
            streak_record = LoginStreak(user_id=user.id, streak=1, last_login=today)
            db.add(streak_record)
        else:
            if streak_record.last_login == today:
                # Already logged in today — no change
                return {"streak": streak_record.streak}
            
            from datetime import timedelta
            yesterday = today - timedelta(days=1)
            
            if streak_record.last_login == yesterday:
                # Consecutive day — increment
                streak_record.streak += 1
            else:
                # Missed one or more days — reset
                streak_record.streak = 1
            
            streak_record.last_login = today

        db.commit()
        return {"streak": streak_record.streak}
    finally:
        db.close()