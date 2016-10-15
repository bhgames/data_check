from sqlalchemy.schema import DDL
from sqlalchemy import event
import models.helpers.base
metadata = models.helpers.base.Base.metadata

def timestamps_triggers(table):

    create_update_fcn_ddl = DDL('''\
        CREATE OR REPLACE FUNCTION update_updated_at() RETURNS trigger AS $$
        BEGIN
            new.updated_at = now();
            return new;
        END;
        $$ LANGUAGE 'plpgsql' IMMUTABLE CALLED ON NULL INPUT SECURITY INVOKER;
    ''')

    create_create_fcn_ddl = DDL('''\
        CREATE OR REPLACE FUNCTION set_created_at() RETURNS trigger AS $$
        BEGIN
            new.created_at = now();
            return new;
        END;
        $$ LANGUAGE 'plpgsql' IMMUTABLE CALLED ON NULL INPUT SECURITY INVOKER;
    ''')

    event.listen(
        metadata,
        'before_create',
        create_update_fcn_ddl
    )

    event.listen(
        metadata,
        'before_create',
        create_create_fcn_ddl
    )

    update_ddl = DDL('''\
        CREATE TRIGGER update_updated_at_on_%s BEFORE UPDATE ON "%s"
        FOR EACH ROW EXECUTE PROCEDURE update_updated_at()
    ''' % (table.__tablename__, table.__tablename__))
    event.listen(table.__table__, 'after_create', update_ddl)

    create_ddl = DDL('''\
        CREATE TRIGGER set_created_at_on_%s BEFORE INSERT ON "%s"
        FOR EACH ROW EXECUTE PROCEDURE set_created_at()
    ''' % (table.__tablename__, table.__tablename__))
    event.listen(table.__table__, 'after_create', create_ddl)