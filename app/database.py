from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv
import os 

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", '"postgresql://postgres:Riahi123654@db:5432/postgres"')
# Create the database engine
engine = create_engine(DATABASE_URL, echo=True)
session_local = sessionmaker(bind=engine)
Base = declarative_base()

# Dependency to get the database session
def get_db():
    db = session_local()
    try:
        yield db
    finally:
        db.close()

