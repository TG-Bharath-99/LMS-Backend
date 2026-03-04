from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from Backend.database import engine
from Backend.models import Base
from Backend.routes import router 

Base.metadata.create_all(bind=engine)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# FIXED: Frontend folder (capital F)
app.mount("/static", StaticFiles(directory="../Frontend"), name="static")

@app.get("/", include_in_schema=False)
async def serve_frontend():
    return FileResponse("../Frontend/index.html")

app.include_router(router, prefix="/api")

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
