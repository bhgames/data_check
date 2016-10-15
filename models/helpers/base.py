from sqlalchemy.ext.declarative import declarative_base


def init():
    global Base
    Base = declarative_base()
