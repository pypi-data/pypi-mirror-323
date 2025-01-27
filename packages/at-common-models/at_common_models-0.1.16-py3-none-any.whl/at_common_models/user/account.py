# app/models/user.py
from sqlalchemy import Column, String, Boolean, DateTime
import uuid
from at_common_models.base import BaseModel

class UserAccount(BaseModel):
    __tablename__ = "user_accounts"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String(255), unique=True, index=True)
    name = Column(String(255))
    hashed_password = Column(String(255), nullable=True)
    profile_picture = Column(String(2083), nullable=True)
    is_active = Column(Boolean, default=False)
    verification_token = Column(String(255), nullable=True)
    verification_token_expires = Column(DateTime, nullable=True)
    reset_token = Column(String(255), nullable=True)
    reset_token_expires = Column(DateTime, nullable=True)

    def __str__(self):
        return f"<UserAccount(id={self.id}, email={self.email}, name={self.name})>"

    def __repr__(self):
        return f"<UserAccount(id={self.id}, email={self.email}, name={self.name})>"
