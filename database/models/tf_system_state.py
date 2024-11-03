from sqlalchemy import Column, Integer, Boolean
from . import Base

class TFSystemState(Base):
    __tablename__ = 'tf_system_state'

    id = Column(Integer, primary_key=True)
    dark_mode = Column(Boolean, default=False)
