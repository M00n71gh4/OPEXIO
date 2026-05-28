# This filr handles the command line interface for the application. It is responsible for handling user like arguments/flags and different user submenus 
# for admin and operator. It calls the appropriate functions in the cli_handlers.py file based on user input.

from db import Database #, tblIGroups, tblIMachines, tblIResolved
import cli_handlers
# from datetime import datetime, timezone, timedelta

    
    
def admin_module(database_URL: str):
    handler = cli_handlers.AdminHandler(database_URL)
    
    # Menu options for admin mode as dictionary
    options = {
            "Exit": "0",
            "Setup database (DEPRECATED, Setup in project.py)": "1",
            "Create new groups and machines": "2", 
            "Create new machine for existing group": "3", 
            "Create new resolved status": "4", 
            "Delete groups": "5", 
            "Delete machine": "6", 
            "Delete resolved status": "7", 
            }
    
    choice = ""

    try:
        while True:
            print("\nAdmin Menu:\n")
            for keys in options:
                print(f"Press {options[keys]} for {keys}")
            choice = input("Enter your choise: ").strip()    

            match choice:
                case "0": # Exit
                    print("Exiting admin menu")
                    break
                case "1": # Setup database
                    handler.handle_setup_database()
                case "2": # Create groups and machines
                    handler.create_groups_and_machines_handler()
                case "3": # Create new machine for existing group
                    handler.create_new_machine_for_existing_group_handler()
                case "4": # Create new resolved status
                    handler.create_new_resolved_status_handler()
                case "5": # Delete groups
                    handler.delete_groups_handler()
                case "6": # Delete machine from existing group
                    handler.delete_machine_handler()
                case "7": # Delete resolved status
                    handler.delete_resolved_status()
                case _:
                    print("Invalid choice, try again")
    except Exception as e:
        print(f"An error occurred in admin_setup: {e}")
                

def operator_module(database_URL: str):
    
    op_handler = cli_handlers.OperatorHandler(database_URL)
    options = {
            "Exit": "0",
            "New incident": "1",
            "List incidents": "2",
            "Update incident status to resolved": "3",
            }
    db = Database(database_URL)
    choice = ""
    
    while True:
        print("\nOperator menu\n")
        for keys in options:
            print(f"Press {options[keys]} for {keys}")
        choice = input("Enter your choise: ").strip()    

        match choice:
            case "0":
                print("\nExit operator menu")
                break
            case "1":
                print("\nregister new incident")
                op_handler.new_incident_handler()
            case "2":
                print("\nList incidents")
                op_handler.new_list_incidents_handler()
            case "3": 
                print("\nUpdate incident status fromunresolved to resolved")
                op_handler.update_incident_status_handler()
            case _:
                print("\nInvalid choice, try again")
