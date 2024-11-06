from sqlalchemy import Column, Integer, Boolean, String
from . import Base

class TFSystemState(Base):
    __tablename__ = 'tf_system_state'

    id = Column(Integer, primary_key=True)
    dark_mode = Column(Boolean, default=False)
    language = Column(String, default='en')
    window_width = Column(Integer, default=960)
    window_height = Column(Integer, default=600)
