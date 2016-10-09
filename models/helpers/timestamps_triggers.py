from sqlalchemy.schema import DDL
from sqlalchemy import event

def timestamps_triggers(table):
    update_ddl = DDL('''\
    CREATE TRIGGER update_updated_at_on_%s BEFORE UPDATE ON %s
      BEGIN
        new.updated_at = now()
      END;''' % (table.__tablename__, table.__tablename__))
    event.listen(table.__table__, 'after_create', update_ddl)
    
    create_ddl = DDL('''\
    CREATE TRIGGER set_created_at_on_%s BEFORE INSERT ON %s
      BEGIN
        new.created_at = now()
      END;''' % (table.__tablename__, table.__tablename__))
    event.listen(table.__table__, 'after_create', create_ddl)