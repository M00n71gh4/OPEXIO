from pathlib import Path
import pytest
from sqlalchemy import create_engine
from project import check_for_database, choose_database, setup_database

@pytest.fixture
def db(tmp_path: Path):
    file_name = tmp_path / "test.db"
    return f"sqlite:///{file_name}"

def test_choose_database_true():
    assert choose_database(test_database=True) == "sqlite:///test.db"

def test_choose_database_false():
    assert choose_database(test_database=False) == "sqlite:///opexio.db"
    
def test_check_if_database_SQLite_exists_false(db: str):
    print("DATABASES:")
    print(f"test_check_if_database_SQLite_exists_false: \n Database URL: {db}")
    # file_name = tmp_path / "test_setup.db"
    assert check_for_database(db) == False
    
def test_setup_database(db: str):
    print(f"test_setup_database: \n Database URL: {db}")
    # file_name = tmp_path / "test_setup.db"
    tables_result, table_list = setup_database(db)
    assert isinstance(tables_result, int) 
    assert isinstance(table_list, list)

def test_setup_tables(db: str):
    # file_name = tmp_path / "test_setup.db"
    print(f"test_setup_tables: \n Database URL: {db}")
    tables_result, table_list = setup_database(db)
    assert "tblIResolved" in table_list 
    assert "tblIncidents" in table_list 
    assert "tblErrors" in table_list 
    assert "tblIMachineError" in table_list 
    assert "tblIGroups" in table_list
    assert "tblIMachines" in table_list 

def test_check_if_database_SQLite_exists_true(db: str):
    engine = create_engine(db)
    with engine.connect():
        pass
    assert check_for_database(db) == True