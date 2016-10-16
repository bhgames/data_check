from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

def init(engine):
    global Base
    global Session
    Base = declarative_base()
    Session = sessionmaker(bind=engine)