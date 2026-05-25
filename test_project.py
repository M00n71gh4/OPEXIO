from project import choose_database, start_admin_cli, start_operator_cli
from pytest import capsys

def test_choose_database():
    assert choose_database(test_database=True) == str("sqlite:///test.db")
    assert choose_database(test_database=False) == str("sqlite:///opexio.db")
    
def test_start_admin_cli():
    database = "sqlite:///test.db"
    start_admin_cli(database)
    captured = capsys.readouterr()
    assert "Admin CLI setup complete" in captured.out