from db import Database

    
def admin_setup(database_URL: str):
    print("Starting admin")
    options = {
            "Exit": "0",
            "Setup database": "1",
            "Delete all tables": "2",
            "Insert group": "3",
            "Insert resolved status": "4",
            "Populate default resolved statuses": "5",
            }
    print(f"cli.py - {database_URL}")
    db = Database(database_URL)
    choice = ""

    while True:
        
        for keys in options:
            print(f"Press {options[keys]} for {keys}")
        choice = input("Enter your choise: ").strip()    

        match choice:
            case "0":
                print("Exiting admin menu")
                break
            case "1":
                print(f"Setup database {db.setup_database()}")
            case "2":
                print(f"Delete tables {db.delete_tables()}")
            case "3":
                new_group = input("The name of the new group: ").strip()
                print(f"Group insert: {db.insert_group(new_group)}")
            case "4":
                new_status = input("Insert an 'Resolved status' option: ").strip()
                print(f"Insert resolved status {db.insert_resolved(new_status)}")
            case "5":
                print(f"Populate: {db.populate_standard_resolved_statuses()}")
            case _:
                print("Invalid choice, try again")

                

def operator_module():
    pass

