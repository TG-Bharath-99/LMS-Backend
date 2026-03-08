from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from Backend.database import engine, SessionLocal
from Backend.models import Base, Course
from Backend.routes import router

def seed_courses():
    db = SessionLocal()
    try:
        if db.query(Course).count() == 0:
            sample_courses = [
                Course(title="Web Development Masterclass"),
                Course(title="Data Science Fundamentals"),
                Course(title="Python for Beginners"),
                Course(title="JavaScript Advanced")
            ]
            db.add_all(sample_courses)
            db.commit()
    finally:
        db.close()

@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    seed_courses()
    yield

app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix="/api")

@app.get("/health")
async def health_check():
    return {"status": "healthy"}