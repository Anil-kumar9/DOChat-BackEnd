from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List

class UserSchema(BaseModel):
    username: str
    full_name: str
    password: str
class UserDto(BaseModel):
    username: str
    id: int
    full_name: str

class LoginDto(BaseModel):
    username: str
    password: str

class FileUploadDto(BaseModel):
    file_id: int
    file_name: str

class ChatDto(BaseModel):
    file_id: int
    message: str

class ChatRequestDto(BaseModel):
    question: str

class ChatHistoryDto(BaseModel):
    id: int
    message: str
    response: Optional[str]
    created_at: datetime

    class Config:
        orm_mode = True
