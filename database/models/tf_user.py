from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from . import Base

class TFUser(Base):
    __tablename__ = 'tf_user'
    
    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True)
    email = Column(String, unique=True)
    password = Column(String)
    created_time = Column(DateTime, default=func.now())
    updated_time = Column(DateTime, default=func.now(), onupdate=func.now())
    last_login = Column(DateTime, nullable=True)
    login_times = Column(Integer, default=0)
    avatar = Column(String, nullable=True)