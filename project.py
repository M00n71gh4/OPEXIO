from argparse import ArgumentParser
from cli import admin_setup, operator_module
from config import PROD_DB, TEST_DB
from sqlalchemy import create_engine
from db import Database

def main():
    argparser = ArgumentParser(description="OPEXIO Incident Management CLI")
    
    argparser.add_argument("--test", action="store_true", help="Use the test database instead of production")
    
    parser_group = argparser.add_mutually_exclusive_group() # make sure only one mode is selected
    parser_group.add_argument('--admin', action="store_true", help="Use the CLI as administrator")
    parser_group.add_argument('--op', action="store_true", help="Use the CLI as an operator")
    
    args = argparser.parse_args()
    database = choose_database(test_database=args.test)
    
    # Start the appropriate CLI mode
    if args.admin:
        start_admin_cli(database)
    if args.op:
        start_operator_cli(database)
        
    
    
def choose_database(test_database: bool) -> str:  # CS50P COMPLIANCE FUNCTION
    if test_database:
        return str(TEST_DB)
    else:
        return str(PROD_DB)

def start_admin_cli(database): # CS50P COMPLIANCE FUNCTION
    admin_setup(database)

def start_operator_cli(database): # CS50P COMPLIANCE FUNCTION
    operator_module(database)


if __name__ == "__main__":
    main()  