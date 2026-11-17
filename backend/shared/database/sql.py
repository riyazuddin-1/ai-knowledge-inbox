import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# 1. Ensure the database directory exists before SQLite tries to write to it
os.makedirs("database", exist_ok=True)

# 2. Use a standard SQLite file path with an extension
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./database/app.sqlite")

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()

def database():
    session = SessionLocal()
    try:
        yield session
    finally:
      session.close()
