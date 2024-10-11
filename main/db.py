from sqlalchemy import  create_engine
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "sqlite:///./chatbot.db"

engine = create_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

async def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
