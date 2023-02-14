import pytest

from cag.utils.config import configuration


@pytest.fixture(scope="session", autouse=True)
def database_cleanup():
    conn = configuration(database="_system")
    yield conn
    dbs = conn.arango_db.databases()
    for db in dbs:
        if "test" in db:
            print("Deleting db", db)
            conn.arango_db.delete_database(db)
