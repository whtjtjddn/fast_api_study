from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.orm import declarative_base
from src.database import metadata

Base = declarative_base(metadata=metadata)

class Todo(Base):
    __tablename__ = "todos"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(String(1024), nullable=True)
    completed = Column(Boolean, default=False)
