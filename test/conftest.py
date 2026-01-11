import pytest
from sqlalchemy import create_engine
from db import metadata
# Setup in memory SQLite database for testing
from db import (
setup_database,
insert_group,
insert_machine,
insert_resolved,
insert_incident,
insert_resolution,
insert_error
)

engine = create_engine("sqlite:///test.db", echo=True)

@pytest.fixture(scope="session", autouse=True)
def setup_db():
    metadata.drop_all(engine)
    metadata.create_all(engine)
    yield
    metadata.drop_all(engine)

@pytest.fixture()
def session():
    con = engine.connect()
    transaction = con.begin()
    try:
        yield con
    finally:
        # Rollback any changes after each test and close connection
        transaction.rollback()
        con.close()

@pytest.fixture
def ids(session):
    group_id = insert_group("test_group")
    machine_id = insert_machine("test_machine", group_id)
    error_id = insert_error("errorNumber", machine_id)
    return {
        "group_id": group_id, 
        "machine_id": machine_id, 
        "error_id": error_id
        }