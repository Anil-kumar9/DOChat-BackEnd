from sqlalchemy import Column, Integer, String, ForeignKey, Text, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
from sqlalchemy.sql import func

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    password = Column(String, index=True)
    full_name = Column(String, index=True)
    files = relationship("File", back_populates="user")

class File(Base):
    __tablename__ = "files"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    file_name = Column(String)
    context = Column(String)
    uploaded_at = Column(DateTime(timezone=True), server_default=func.now())
    
    user = relationship("User", back_populates="files")
    chats = relationship("Chat", back_populates="file", cascade="all, delete-orphan")

class Chat(Base):
    __tablename__ = "chats"
    
    id = Column(Integer, primary_key=True, index=True)
    file_id = Column(Integer, ForeignKey("files.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    message = Column(Text)
    response = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    file = relationship("File", back_populates="chats")
