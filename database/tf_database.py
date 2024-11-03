import os
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from .models import Base
from .models.tf_system_state import TFSystemState

class TFDatabase:
    def __init__(self, db_url, db_path):
        self.engine = create_engine(db_url, echo=False)

        if not os.path.exists(db_path):
            Base.metadata.create_all(self.engine)
            self.initialize_data()
        else:
            Base.metadata.create_all(self.engine)

    def get_session(self):
        return Session(self.engine)
    
    def initialize_data(self):
        with self.get_session() as session:
            default_state = TFSystemState(dark_mode=False)
            session.add(default_state)
            session.commit()
            