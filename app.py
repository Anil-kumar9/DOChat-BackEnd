from fastapi import FastAPI, UploadFile, File, HTTPException
import pytesseract

from main import service
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, Depends, UploadFile, File, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from main.models import User, File as FileModel, Chat as ChatModel, Base
from main.db import get_db, engine
from main.schemas import UserDto, ChatDto, FileUploadDto, ChatHistoryDto, UserSchema, LoginDto, ChatRequestDto
import os
from typing import List

pytesseract.pytesseract.tesseract_cmd = (
    r"C:\Program Files\Tesseract-OCR\tesseract.exe"
)
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4200"],  
    allow_credentials=True,
    allow_methods=["*"],  
    allow_headers=["*"],  
)

@app.post("/upload/{user_id}")
async def upload_file(user_id: int, file: UploadFile = File(...),db: Session = Depends(get_db)):
    response = await service.save_file_to_database(file, user_id, db)
    if response is None:
        return "something went wrong"
    else:
        return response

@app.post("/chat/{file_id}")
async def chat(file_id: int, chat_request: ChatRequestDto, db: Session = Depends(get_db)):
    reply = await service.reply_to_question(file_id, chat_request.question, db)
    if reply is None:
        return "connection error"
    else:
        return reply

@app.on_event("startup")
def startup():
    Base.metadata.create_all(bind=engine)
    # alembic init alembic
    # sqlalchemy.url = sqlite:///./test.db
    # target_metadata = db.metadata
    # alembic revision --autogenerate -m "Create users table"
    # alembic upgrade head


@app.on_event("shutdown")
async def shutdown():
    await db.database.disconnect()

@app.post("/save" ,response_model=UserDto)
async def create_user(user: UserSchema,db: Session = Depends(get_db)):
    try:
        return await service.create_user(user,db)
    except:
        raise Exception("something went wrong")

# @app.get("/users/{user_id}", response_model=db.UserOut)
# async def get_user(user_id: int):
#     try:
#         return await service.get_user(user_id)
#     except:
#         raise Exception("something went wrong")

@app.post("/users/login", response_model=UserDto)
async def user_login(dto: LoginDto, db: Session = Depends(get_db)):
    try:
        return await service.user_login(dto, db)
    except:
        raise Exception("something went wrong")

@app.get("/chat_history/{file_id}", response_model=List[ChatHistoryDto])
async def get_chat_history(file_id: int, db: Session = Depends(get_db)):
    return await service.get_chat_history(file_id, db)

@app.get("/files/{user_id}", response_model=List[FileUploadDto])
async def get_chat_history(user_id: int, db: Session = Depends(get_db)):
    return await service.get_all_files_of_user(user_id, db)

@app.delete("/files/{file_id}")
async def delete_file(file_id: int,db: Session = Depends(get_db) ):
    return await service.delete_file(file_id, db)