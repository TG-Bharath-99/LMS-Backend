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

# Allow all origins — required for Vercel serverless + Netlify frontend
# If you want to restrict later, replace "*" with your Netlify URL:
# "https://effervescent-dragon-b7f49f.netlify.app"
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,   # Must be False when allow_origins=["*"]
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix="/api")

@app.get("/")
async def root():
    return {"status": "CoursePortal API is running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}