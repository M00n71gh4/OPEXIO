from argparse import ArgumentParser
from cli import admin_module, operator_module
from config import PROD_DB, TEST_DB
from db import Database


def main():
    """ Main function for the OPEXIO Incident Management CLI. Parses command-line arguments, checks for database existence,
        and starts the appropriate CLI mode (admin or operator).
    """
    argparser = ArgumentParser(description="OPEXIO Incident Management CLI")
    
    argparser.add_argument("--test", action="store_true", help="Use the test database instead of production")
    
    parser_group = argparser.add_mutually_exclusive_group() # make sure only one mode is selected
    parser_group.add_argument('--admin', action="store_true", help="Use the CLI as administrator")
    parser_group.add_argument('--op', action="store_true", help="Use the CLI as an operator")
    
    args = argparser.parse_args()
    database = choose_database(test_database=args.test)
    print(f"Using database: {database}")
    db_exists = check_for_database(database)
    load_cli = False
    
    print(str(TEST_DB))
    print(str(PROD_DB))
    
    
    if not db_exists:

        print(f"Database {database} does not exist. Please set up the database first.")
        setup = input("Do you want to set up the database now? (Y to set up, C to continue with no database): ")
        if setup.lower() == 'y':
            print(f"Setting up database {setup_database(database)}...")
            
            load_cli = True
        else:
            quit = input("Press enter to continue to application with no database, or 'q' to quit.")
            if not quit.lower() == 'q':
                load_cli = True
    else:
        print(f"Database {database} found. Loading CLI...")
        load_cli = True
            
            
    # Start the appropriate CLI mode
    if args.admin and load_cli:
        admin_module(database)
    if args.op and load_cli:
        operator_module(database)
        
    
    
def choose_database(test_database: bool) -> str: 
    """Chooses the database URL based on the test_database flag.

    Args:
        test_database (bool): If True, the test database URL will be returned. If False, the production database URL will be returned.

    Returns:
        str: The URL of the chosen database.
    """
    if test_database:
        return str(TEST_DB)
    elif not test_database:
        return str(PROD_DB)

def check_for_database(database_URL: str) -> bool:
    """Checks if the database exists at the given URL.

    Args:
        database_URL (str): The URL of the database to check.

    Returns:
        bool: True if the database exists, False otherwise.
    """
    db = Database(database_URL)
    return db.check_if_database_exists()


def setup_database(database_URL: str) -> tuple[int, list]:
    """Sets up the database at the given URL.

    Args:
        database_URL (str): The URL of the database to set up.

    Returns:
        tuple[int, list]: A tuple containing the number of tables created and the list of created tables.
    """
    db = Database(database_URL)
    created = db.setup_database()
    return len(created), created


if __name__ == "__main__":
    main()  