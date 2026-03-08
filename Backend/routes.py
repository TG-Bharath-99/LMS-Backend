from fastapi import APIRouter, HTTPException, Depends
from Backend.database import SessionLocal
from Backend.models import User, Course, Enrollment, CourseTopic
from Backend.schemas import Signup, Login
from Backend.security import hash_password, verify_password
from Backend.auth import create_access_token, get_current_user

router = APIRouter()

@router.post("/signup")
def signup(user: Signup):
    db = SessionLocal()
    existing = db.query(User).filter(User.email == user.email).first()
    if existing:
        db.close()
        raise HTTPException(status_code=400, detail="Email already exists")
    new_user = User(
        name=user.name,
        email=user.email,
        password=hash_password(user.password)
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    db.close()
    return {
        "name": new_user.name,
        "email": new_user.email,
        "message": "Signup successfully completed"
    }

@router.post("/login")
def login(user: Login):
    db = SessionLocal()
    db_user = db.query(User).filter(User.email == user.email).first()
    if not db_user:
        db.close()
        raise HTTPException(status_code=404, detail="User not found")
    if not verify_password(user.password, db_user.password):
        db.close()
        raise HTTPException(status_code=401, detail="Invalid password")
    token = create_access_token({"sub": db_user.email})
    db.close()
    return {"access_token": token, "token_type": "bearer"}

@router.get("/me")
def get_my_profile(current_user: str = Depends(get_current_user)):
    return {"logged_in_as": current_user}

@router.get("/users")
def get_users(current_user: str = Depends(get_current_user)):
    db = SessionLocal()
    users = db.query(User).all()
    db.close()
    return [{"id": u.id, "name": u.name, "email": u.email} for u in users]

@router.get("/users/{user_email}")
def get_user_by_email(user_email: str, current_user: str = Depends(get_current_user)):
    db = SessionLocal()
    user = db.query(User).filter(User.email == user_email).first()
    db.close()
    if not user:
        raise HTTPException(status_code=404, detail="Not found")
    return {"id": user.id, "name": user.name, "email": user.email}

@router.put("/users/{user_email}")
def update_user(user_email: str, user: Signup, current_user: str = Depends(get_current_user)):
    if current_user != user_email:
        raise HTTPException(status_code=403, detail="Not allowed")
    db = SessionLocal()
    db_user = db.query(User).filter(User.email == user_email).first()
    if not db_user:
        db.close()
        raise HTTPException(status_code=404, detail="User not found")
    db_user.name = user.name
    db_user.password = hash_password(user.password)
    db.commit()
    db.refresh(db_user)
    db.close()
    return {
        "message": "User updated",
        "user": {"id": db_user.id, "name": db_user.name, "email": db_user.email}
    }

@router.delete("/users/{user_email}")
def delete_user(user_email: str, current_user: str = Depends(get_current_user)):
    if current_user != user_email:
        raise HTTPException(status_code=403, detail="Not allowed")
    db = SessionLocal()
    db_user = db.query(User).filter(User.email == user_email).first()
    if not db_user:
        db.close()
        raise HTTPException(status_code=404, detail="User not found")
    db.delete(db_user)
    db.commit()
    db.close()
    return {"message": "User deleted successfully"}

@router.get("/courses")
def get_courses():
    db = SessionLocal()
    courses = db.query(Course).all()
    db.close()
    if not courses:
        return {"message": "No courses available"}
    return [{"id": c.id, "title": c.title} for c in courses]

@router.post("/enroll/{course_id}")
def enroll_course(course_id: int, current_user: str = Depends(get_current_user)):
    db = SessionLocal()
    user = db.query(User).filter(User.email == current_user).first()
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        db.close()
        raise HTTPException(status_code=404, detail="Course not found")
    existing = db.query(Enrollment).filter(
        Enrollment.user_id == user.id,
        Enrollment.course_id == course_id
    ).first()
    if existing:
        db.close()
        raise HTTPException(status_code=400, detail="Already enrolled")
    enrollment = Enrollment(user_id=user.id, course_id=course_id)
    db.add(enrollment)
    db.commit()
    db.close()
    return {"message": "Enrolled successfully"}

@router.get("/my-courses")
def my_courses(current_user: str = Depends(get_current_user)):
    db = SessionLocal()
    user = db.query(User).filter(User.email == current_user).first()
    enrollments = db.query(Enrollment).filter(Enrollment.user_id == user.id).all()
    course_ids = [e.course_id for e in enrollments]
    courses = db.query(Course).filter(Course.id.in_(course_ids)).all()
    db.close()
    return [{"id": c.id, "title": c.title} for c in courses]
