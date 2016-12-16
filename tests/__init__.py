from base_test import BaseTest
from connections.impala_connection import ImpalaConnection

def setup():
    with open('tests/fixtures/seed.sql') as f:
        seed = f.read()
        config = BaseTest.config()
        with ImpalaConnection(config["host"], config["port"], config["user"], config["password"]) as db:
            c = db.cursor()
            for stmt in seed.split(";"):
                if stmt.strip() == "":
                    continue
                try:
                    c.execute(stmt)
                except Exception:
                    print "Stmt " + stmt + " failed:"
                    traceback.print_exc()
                    raise

            db.commit()
