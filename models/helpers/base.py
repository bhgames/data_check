from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

def init(engine):
    global Base
    global Session
    Base = declarative_base()
    Session = sessionmaker(bind=engine)


if __name__ == '__main__':
    import models.helpers.base
    from sqlalchemy import create_engine, MetaData
    engine = create_engine('postgresql://localhost:5432/data_check')
    models.helpers.base.init(engine)
    from models import *
    models.helpers.base.Base.metadata.create_all(engine)
    print "done"