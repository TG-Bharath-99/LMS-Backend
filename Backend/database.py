from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv
import os

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError(
        "ERROR: DATABASE_URL environment variable is not set. "
        "Please set it in your .env file before running the application. "
        "Example: DATABASE_URL=postgresql://user:password@localhost/dbname"
    )

try:
    engine = create_engine(DATABASE_URL)
except Exception as e:
    raise ValueError(
        f"ERROR: Failed to create database engine. "
        f"Check your DATABASE_URL format. Error: {str(e)}"
    )

SessionLocal = sessionmaker(bind=engine)

Base = declarative_base()