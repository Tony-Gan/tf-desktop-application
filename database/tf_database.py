import os
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from .models import Base

class TFDatabase:
    def __init__(self, db_url, db_path):
        self.enging = create_engine(db_url, echo=False)

        if not os.path.exists(db_path):
            Base.metadata.create_all(self.enging)
            self.initialize_data()

    def get_session(self):
        return Session(self.engine)
    
    def initialize_data(self):
        with self.get_session() as session:
            pass
            session.commit()
            