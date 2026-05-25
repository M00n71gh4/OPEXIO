from db import Database, tblIGroups
from utils import menu_map

    
def admin_setup(database_URL: str):
    try:
        print("Starting admin mode")
        options = {
                "Exit": "0",
                "Setup database": "1",
                "Create new groups and machines": "2",
                "Create new machine for existing group": "3",
                "Create new resolved status": "4",
                "Populate resolved statuses with default values": "5",
                "Delete groups": "6",
                "Delete machine": "7",
                "Delete resolved status": "8",
                }
        print(f"cli.py - {database_URL}")
        db = Database(database_URL)
        choice = ""

        while True:
            print("\nAdmin Menu:\n")
            for keys in options:
                print(f"Press {options[keys]} for {keys}")
            choice = input("Enter your choise: ").strip()    

            match choice:
                case "0": #Exit
                    print("Exiting admin menu")
                    break
                case "1": # Setup database
                    print(f"Setup database {db.setup_database()}")

                case "2": # Create groups and machines
                    new_group = input("The name of the new group: ").strip()
                    group_ID = db.insert_group(new_group)
                    print(f"Group {new_group} created with ID {group_ID}")
                    
                    while True:
                        create_machine = input("Do you want to create a machine for this group? (y/n): ").strip().lower()
                        if create_machine == 'y':
                            new_machine = input("The name of the new machine: ").strip()
                            db.insert_machine(new_machine, group_ID)
                            print(f"Machine {new_machine} created")
                        elif create_machine == 'n':
                            break
                        else:
                            print("Invalid choice, try again")

                case "3": # Create new machine for existing group
                    groups = db.list_groups()
                    
                    
                    while True:
                        print("\nPress 0 to go back")
                        for items in menu["map"]:
                            print(f"Press {items} for group {menu['map'][items]['groupName']}")

                        group_choice = input("Enter: ").strip()
                        
                        if group_choice.isdigit() and 1 <= int(group_choice) <= menu["length"]:
                            new_machine = input("The name of the new machine: ").strip()
                            print(f"Machine with ID {db.insert_machine(new_machine, int(group_choice))} created")
                        elif group_choice == '0':
                            break
                        else:
                            print("\nInvalid group selected")
                            
                case "4": # Create new resolved status
                    new_status = input("Insert an 'Resolved status' option: ").strip()
                    print(f"Insert resolved status {db.insert_resolved(new_status)}")
                    
                case "5": #Populate default resolved statuses
                    print(f"Populate: {db.populate_standard_resolved_statuses()}")
                            
                case "6": # Delete groups
                    while True:
                        groups = db.list_groups()    
                        print(f"Existing groups: {groups}") 
                        menu = menu_map(groups)
                        
                        # Creates a menu of available groups to delete
                        print("\nPress 0 to go back")
                        for key in menu:
                            print(f"Press {key} to delete {menu[key]['groupName']}")
                        
                        group_choice = input("\nEnter group number to delete group: ").strip()
                        
                        # Validates the input as integer and within range of group choices
                        if group_choice.isdigit():
                            group_choice = int(group_choice)
                        else: 
                            group_choice = -1
                            
                        # Deletes the group if valid choice
                        if 1 <= group_choice <= len(menu):
                            result = db.delete_rows(table= tblIGroups, condition= [tblIGroups.columns.id == menu[group_choice]['id']])
                            if result > 0:
                                print(f"Deleted rows: {result}")
                                print(f"Choice {group_choice} for group {menu[group_choice]['groupName']} deleted with ID {menu[group_choice]['id']}.")
                                
                        elif group_choice == 0:
                            break
                        else:
                            print("\nInvalid group selected")
                            

                case "7": # Delete machine from existing group
                    print("DELETE MACHINE!!!!!!!!!!!!!!!")
                    machines = db.list_machines()
                    print(f"Existing machines: {machines}")
                    menu = menu_map(machines)
                    # Creates a menu of available groups to delete
                    
                    print("\nPress 0 to go back")
                    for key in menu:
                        print(f"Press {key} to delete {menu[key]['machineName']}")
                    
                    group_choice = input("\nEnter group number to delete group: ").strip()
                    
                    #db.delete_rows()

                case "8": #Delete resolved status
                    pass
                case "X": #Delete all tables
                    print("Delete all tables - Feature disabled")
                    #print(f"Delete tables {db.delete_tables()}")
                case _:
                    print("Invalid choice, try again")
    except Exception as e:
        print(f"An error occurred in admin_setup: {e}")
                

def operator_module(database_URL: str):
    print("Starting operator mode")
    options = {
            "Exit": "0",
            "New incident": "1",
            "List incidents last 24h": "2",
            "List all incidents": "3",
            "List unresolved incidents": "4",
            #"Set as resolved": "5",
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
                print("Exit operator menu")
                break
            case "1":
                print("New incident")
                print(db.list_machines())
            case "2":
                print("List incidents last 24h")
                print(db.list_incidents())
            case "3":
                print("List all incidents")
                print(db.list_incidents())
            case "4":
                print("List unresolved incidents")
                print(db.list_incidents())
            case _:
                print("Invalid choice, try again")


