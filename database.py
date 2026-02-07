import os

from sqlalchemy import create_engine

from sqlalchemy.orm import sessionmaker, declarative_base

from fastapi import Depends

from typing import Annotated

from sqlalchemy.orm import Session

from dotenv import load_dotenv
 
# Load .env only for local development

if os.getenv("VERCEL") is None:

    load_dotenv()
 
DATABASE_URL = os.environ["POSTGRES_URL"]  # Supabase POOLER URL
 
engine = create_engine(

    DATABASE_URL,

    pool_pre_ping=True,  # detects dropped connections

    pool_size=1,         # serverless-safe

    max_overflow=0,      # no surprise connections

)
 
SessionLocal = sessionmaker(

    autocommit=False,

    autoflush=False,

    bind=engine,

)
 
Base = declarative_base()
 
 
def get_db():

    db = SessionLocal()

    try:

        yield db

    finally:

        db.close()
 
 
db_dependency = Annotated[Session, Depends(get_db)]

 
