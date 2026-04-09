import enum
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy import Enum as SAEnum
from sqlalchemy.orm import relationship
from app.database import Base


class UserRole(str, enum.Enum):
    viewer  = "viewer"
    analyst = "analyst"
    admin   = "admin"


class UserStatus(str, enum.Enum):
    active   = "active"
    inactive = "inactive"


class User(Base):
    __tablename__ = "users"

    id            = Column(Integer, primary_key=True, index=True)
    name          = Column(String(100), nullable=False)
    email         = Column(String(150), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    role          = Column(SAEnum(UserRole),   default=UserRole.viewer,   nullable=False)
    status        = Column(SAEnum(UserStatus), default=UserStatus.active, nullable=False)
    created_at    = Column(DateTime, default=datetime.utcnow, nullable=False)

    transactions  = relationship("Transaction", back_populates="owner", cascade="all, delete-orphan")