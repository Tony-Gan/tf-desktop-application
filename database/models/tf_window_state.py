from sqlalchemy import Column, Integer, String
from . import Base

class TFWindowState(Base):
    __tablename__ = 'tf_window_state'

    id = Column(Integer, primary_key=True)
    window_class = Column(String, nullable=False)
    title = Column(String, nullable=False)
    x_position = Column(Integer, nullable=False)
    y_position = Column(Integer, nullable=False)
