#from sqlalchemy import create_engine
#from db import Database
from argparse import ArgumentParser
from cli import admin_setup
from config import PROD_DB, TEST_DB
from sqlalchemy import create_engine
from db import Database

def main():
    argparser = ArgumentParser(description="OPEXIO Incident Management CLI")
    
    #argparser.add_argument('--setup', action="store_true", help="Setup the database schema")
    #argparser.add_argument('--populate', action="store_true", help="Populate the database")
    argparser.add_argument("--test", action="store_true", help="Use the test database instead of production")
    parser_group = argparser.add_mutually_exclusive_group()
    parser_group.add_argument('--admin', action="store_true", help="Use the CLI as administrator")
    parser_group.add_argument('--op', action="store_true", help="Use the CLI as an operator")
    
    args = argparser.parse_args()
    database = ""
    if args.test:
        database = str(TEST_DB)
    else:
        database = str(PROD_DB)
   
    
    #if args.setup:
    #    print("Setup mode")
    #    db.setup_database(db)
    #if args.populate:
    #    print("Populate mode")
    if args.admin:
        print(f"main.py - {database}")
        admin_setup(database)
    if args.op:
        print("Operator mode")
    
    
    
    
if __name__ == "__main__":
    main()  