import datetime
from sqlalchemy import Column, Integer, String, DateTime
from database import Base

class APIKey(Base):
    __tablename__ = "api_keys"

    id = Column(Integer, primary_key=True, index=True)
    key_name = Column(String, index=True)
    secret_key = Column(String, unique=True, index=True)
    allowed_model = Column(String)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)