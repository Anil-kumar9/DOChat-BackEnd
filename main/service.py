from sqlalchemy import insert, select, update
import cohere
from fastapi import FastAPI, UploadFile, File, HTTPException,Depends
import io
from PyPDF2 import PdfReader
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from .models import User, File as FileModel, Chat as ChatModel, Base
from .db import get_db, engine
from .schemas import UserDto, ChatDto, FileUploadDto, ChatHistoryDto, UserSchema
import json

co = cohere.ClientV2("Xg5u8PnioXF2pC1YZIUawByjpUcQFSwsIbbFzrOQ")

async def create_user(user, db):
    user = User(
        username=user.username,
        password=user.password, 
        full_name=user.full_name,
    )
    db.add(user)
    try:
        db.commit()
        db.refresh(user)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Username already exists")
    response = UserDto(id= user.id, username= user.username, full_name= user.full_name)
    return response


# def get_user(id, db):
#     query = select(db.users).where(db.users.c.id == id)
#     user = db.database.fetch_one(query)
#     if user is None:
#         raise HTTPException(status_code=404, detail="User not found")
#     return user

async def save_file_to_database(file, user_id, db):
    if file.content_type not in ["application/pdf"]:
        raise HTTPException(status_code=400, detail="Unsupported file type.")
    try:
        extracted_text = extract_text_from_file(file)
        db_file = FileModel(file_name=file.filename, context=extracted_text, user_id=user_id)
        db.add(db_file)
        db.commit()
        db.refresh(db_file)

        return FileUploadDto(file_id=db_file.id, file_name=db_file.file_name)
    except:
        return None

def extract_text_from_file(file: UploadFile):
    try:
        reader = PdfReader(io.BytesIO(file.file.read()))
        text = ""
        print(str(reader), reader.pages)
        for page in reader.pages:
            text += page.extract_text()
        print("text",text)
        return text
    except Exception as e:
        raise HTTPException(status_code=400, detail="Error processing image file." + str(e))


def answer_question(text: str, question: str, chat_history: str):
    prompt = f"Prompt:don't go out of provided document text, just give ansswers for the questions related to Doucument text, use UserPreviousChatHistory for better user experience, for unrelated questions just respond with a aproprite answer .\n\nUserPreviousChatHistory: {chat_history}\n\nDocument text:\n{text}\n\nQuestion: {question}\nAnswer:"
    response = co.chat(
        model="command-r-plus",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )
    for event in response:
        if event[0] == "message":
            return event[1].content[0].text

async def reply_to_question(file_id, question, db):
    try:
        db_file = db.query(FileModel).filter(FileModel.id == file_id).first()
        chat_history = await get_chat_history(file_id,db)
        chat_history = [{chat.message: chat.response} for chat in chat_history ]
        print(chat_history)
        answer = answer_question(db_file.context, question, chat_history)
        db_chat = ChatModel(file_id=file_id, user_id=db_file.user_id, message=question, response=answer)
        db.add(db_chat)
        db.commit()
        return answer
    except Exception as e:
        print(e)
        return None

async def user_login(dto, db):
    db_user = db.query(User).filter(User.username == dto.username).first()
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    print("passsowrd",db_user.password, dto.password)
    if db_user.password == dto.password:
        response = UserDto(id= db_user.id, username= db_user.username, full_name= db_user.full_name)
        return response
    else:
        raise HTTPException(status_code=401, detail="password not matched")

async def get_chat_history(file_id, db):
    chats = db.query(ChatModel).filter(ChatModel.file_id == file_id).all() 
    return chats

async def get_all_files_of_user(user_id, db):
    files = db.query(FileModel).filter(FileModel.user_id == user_id).all()
    files = [FileUploadDto(file_id=file.id, file_name=file.file_name) for file in files]
    return files[::-1]

async def delete_file(file_id, db):
    file_to_delete = db.query(FileModel).filter(FileModel.id == file_id).first()
    db.delete(file_to_delete)
    db.commit()
    return "file deleted successfully!"