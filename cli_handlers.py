# This file handles communication between the core functions and the cli.
# It is responsible for calling the appropriate functions based on user input and returning the results to the cli.
# I chose to seperate this file from the cli.py file to keep the cli file clean and focused on handling main admin/operator user menus. 
# while this file focuses on handling sub menu functions and the logic of calling the core functions like the functions in the db.py file.

from zoneinfo import ZoneInfo
from db import Database, tblIGroups, tblIMachines, tblIResolved
from datetime import datetime, timedelta
from utils import menu_map, check_datetime, local_time_now

LOCAL_TIMEZONE = ZoneInfo("Europe/Oslo")     

class SetupHandler:
    def __init__(self, db_URL: str):
        self.db = Database(db_URL)
        
    def check_for_database(self) -> bool:
        """Checks if the database exists.

        Returns:
            bool: Returns True if the database exists, False if not.
        """
        return self.db.check_if_database_exists()
    
    def handle_setup_database(self):
        """Creates tables in the database
        Returns:
            Number og tables created, list of tables created.
        """
        try:
            table_list = self.db.setup_database()
            return len(table_list), table_list
        except Exception as e:
            print(f"Error setting up database: {e}")
            return 0, []

# The functions is a CLI handlers function that interacts with the user and the database, they do not return any value.
class AdminHandler:
    """ Handles admin CLI operations and coordinates interactions with the database.
        Each method corresponds to a specific admin menu action and manages
        user input and output, validation, and database calls.
    """
    def __init__(self, db_URL: str):
        self.db = Database(db_URL)
    
    def create_groups_and_machines_handler(self): # Admin menu choice 2
        """ This function allows the admin to create a new group and add machines to that group.
        """
        input_group = input("Enter group name to insert: ").strip()
        
        group_ID = self.db.insert_group(input_group)
        try:
            if not group_ID == 0:
                print(f"\nGroup {input_group} created")
            else:
                print("No group created, please try again")
                return
            
            # Loop to add machines to the group until the admin decides to stop
            while True:
                create_machine = input("Do you want to create a machine for this group? (y/n): ").strip().lower()
            
                if create_machine == 'y':
                    new_machine = input("The name of the new machine: ").strip()
                    
                    machine_ID = self.db.insert_machine(new_machine, group_ID)
                    
                    if not machine_ID == 0:
                        print(f"Machine {new_machine} created with ID {machine_ID}")
                    else:
                        print("No machine created, please try again")
                elif create_machine == 'n':
                    break
                else:
                    print("Invalid choice, try again")
                    
        except Exception as e:
            print(f"Error creating group and machines: {e}")
            
    def create_new_machine_for_existing_group_handler(self): # Admin menu choice 3
        """ This function allows the admin to create a new machine for an existing group.
        """
        menu = self.db.list_groups()
        
        print("\nPress 0 to go back")

        i = 0
        for items in menu:
            i += 1
            print(f"Press {i} for group {items['groupName']}")
            
        group_number = input("Enter group number the machine belongs to: ").strip()
        if group_number.isdigit() and 1 <= int(group_number) <= len(menu):
            new_machine = input("The name of the new machine: ").strip()
            
        print(self.db.insert_machine(new_machine, group_number))
        
    def create_new_resolved_status_handler(self): # Admin menu choice 4
        """ This function allows the admin to create a new resolved status option or populates the table with default statuses.
        """
        new_status = input("Enter a new 'Resolved status', press Enter to populate with default statuses, or q to quit: ").strip()
        if new_status.lower() == 'q':
            print("Quitting...")
        elif new_status:
            self.db.insert_resolved_statuses([{"resolvedStatus": new_status}])
            print(f"New {new_status} resolved status created")
        else:
            print(f"Populate: {self.db.insert_resolved_statuses()}") # Populate with default statuses if no input is given


    def delete_groups_handler(self): # Admin menu choice 5
        """This function deletes groups. It first lists all the groups and then allows the admin to select a group to delete. 
            The admin can also choose to go back to the previous menu.
        """
        while True:
            # Creates a menu of available groups to delete
            groups = self.db.list_groups()    
            menu = menu_map(groups)
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
                result = self.db.delete_rows(table= tblIGroups, condition= [tblIGroups.columns.id == menu[group_choice]['id']])
                if result > 0:
                    print(f"Deleted rows: {result}")
                    print(f"Choice {group_choice} for group {menu[group_choice]['groupName']} deleted with ID {menu[group_choice]['id']}.")
                    
            elif group_choice == 0:
                break
            else:
                print("\nInvalid group selected")   
                
                
    def delete_machine_handler(self): # Admin menu choice 6
        """This function deletes machines. It first lists all the machines and then allows the admin to select a machine to delete.|
        """
        machines = self.db.list_machines()
        menu = menu_map(machines)
        
        print("\nPress 0 to go back")
        for key in menu:
            print(f"Press {key} to delete {menu[key]['machineName']}")
        
        machine_choice = input("\nEnter machine number to delete machine: ").strip()
        
        if machine_choice.isdigit():
            machine_choice = int(machine_choice)
        else:
            machine_choice = -1
            
        if 1 <= machine_choice <= len(menu):
            result = self.db.delete_rows(table= tblIMachines, condition= [tblIMachines.columns.id == menu[machine_choice]['id']])
            if result > 0:
                print(f"Deleted rows: {result}")
                print(f"Choice {machine_choice} for machine {menu[machine_choice]['machineName']} deleted with ID {menu[machine_choice]['id']}.")
                
    def delete_resolved_status(self): # Admin menu choice 7
        """This function deletes resolved status options. It first lists all the resolved status options and then allows the admin to select a status to delete.
        """
        status = self.db.list_resolved_statuses()
        menu = menu_map(status)
        print("\nPress 0 to go back")
        for key in menu:
            print(f"Press {key} to delete {menu[key]['resolvedStatus']}")
            
        status_choice = input("\nEnter number to delete resolved status: ").strip()
        if status_choice.isdigit():
            status_choice = int(status_choice)
        else:
            status_choice = -1
            
        if 1 <= status_choice <= len(menu):
            result = self.db.delete_rows(table= tblIResolved, condition= [tblIResolved.columns.id == menu[status_choice]['id']])
            if result > 0:
                print(f"Deleted rows: {result}")
                print(f"Choice {status_choice} for resolved status {menu[status_choice]['resolvedStatus']} deleted with ID {menu[status_choice]['id']}.")
                
    
class OperatorHandler:
    """ Handles operator CLI operations and coordinates interactions with the database.
        Each method corresponds to a specific operator menu action and manages
        user input and output, validation, and database calls.
    """
    def __init__(self, db_URL: str):
        self.db = Database(db_URL)
        self.date_format_human = "DD-MM-YYYY HH:MM" # Standard date format for the application, can be used across all functions that require date input to ensure consistency
        self.date_format_computer = "%d-%m-%Y %H:%M"
        # TODO : Use a dict to provide human readable input format and coresponding datetime format for more flexible date input

    def menu_builder_machines(self, db: Database) -> int: # Creates a menu of machines to select from
        """ This function creates a menu of machines to select from. It takes a database object as an argument and returns the ID of the selected machine.

        Args:
            db (Database): The database object to use for retrieving the list of machines.

        Returns:
            int: The ID of the selected machine.
        """
        machine_map = menu_map(db.list_machines())
        print("\nPress 0 to go back")
        for key in machine_map:
            print(f"Press {key} for {machine_map[key]['machineName']}")
        
        while True:
            chosen_machine = input("\nEnter machine number: ").strip()
            
            if chosen_machine.isdigit() and 1 <= int(chosen_machine) <= len(machine_map):
                machine_ID = int(chosen_machine)
                print(f"Selected machine: {machine_map[machine_ID]['machineName']}")
                return machine_map[machine_ID]['id']
            elif chosen_machine == "0":
                return 0
            else:
                print("Invalid machine selected, try again")          

    def menu_builder_resolved_status(self) -> int: # Creates a menu of resolved status to select from
        """ This function creates a menu of resolved status to select from. It retrieves the list of resolved status from the database 
        and returns the ID of the selected status.

        Returns:
            int: The ID of the selected resolved status.
        """
        resolved_map = menu_map(self.db.list_resolved_statuses())
        print("\nPress 0 to go back")
        for key in resolved_map:
            print(f"Press {key} for {resolved_map[key]['resolvedStatus']}")
        
        while True:
            chosen_resolved = input("\nEnter resolved status number: ").strip()
            
            if chosen_resolved.isdigit() and 1 <= int(chosen_resolved) <= len(resolved_map):
                resolved_ID = int(chosen_resolved)
                print(f"Selected resolved status: {resolved_map[resolved_ID]['resolvedStatus']}")
                return resolved_map[resolved_ID]['id']
            elif chosen_resolved == "0":
                return 0
            else:
                print("Invalid resolved status selected, try again")
                
    def error_selection_menu(self, machine_ID: int) -> int: # Creates a menu of errors to select from for a specific machine
        """ This function creates a menu of errors to select from for a specific machine. It retrieves the list of errors for the given machine ID from the database.

        Args:
            machine_ID (int): The ID of the machine for which to select an error.

        Returns:
            int: The ID of the selected error.
        """
        error_map = menu_map(self.db.list_errors(machine_id=machine_ID))
        print("\nPress 0 to go back")
        print("Press n to create a new error for this machine")
        for key in error_map:
            print(f"Press {key} to use error number: {error_map[key]['errorNumber']} Name: {error_map[key]['errorName']} - ID: {error_map[key]['id']} MAchine: {error_map[key]['machineID']}")
        
        while True:
            chosen_error = input("\nEnter error number: ").strip()

            if chosen_error.lower() == "n":
                return "n"
            elif chosen_error.isdigit() and 1 <= int(chosen_error) <= len(error_map):
                error_ID = int(chosen_error)
                print(f"Selected error: {error_map[error_ID]['errorName']}")
                return error_map[error_ID]['id']
            elif chosen_error == "0":
                return 0
            else:
                print("Invalid error selected, try again")
                
    def new_incident_handler(self)->int:
        """ This function handles the creation of a new incident. It guides the user through the process of selecting a machine, resolved status, error, occurance time, 
            resolved time and notes for the incident. It then calls the appropriate database functions to insert the new incident into the database.

        Returns:
            int: The ID of the newly created incident, 0 if the incident creation was aborted or failed.    
        """
        machine_ID = None
        resolved_ID = None
        error_ID = None    
        # self.date_format = "DD-MM-YYYY HH:MM"
        
        # Machine selection menu
        machine_ID = self.menu_builder_machines(self.db)
        if machine_ID == 0:
            print("Aborting new incident creation")
            return 0
        
        # Resolved status selection
        resolved_ID = self.menu_builder_resolved_status()
        if resolved_ID == 0:
            print("Aborting new incident creation")
            return 0
        
        # Error selection
        error_ID = self.error_selection_menu(machine_ID)
        
        if error_ID == "n":
            
            error_number = input("Enter the error number from the equipment: ").strip()
            error_name = input("Enter a name for the error: ").strip()
            error_description = input("Enter a description for the error: ").strip()
            
            error_ID = self.db.insert_error(error_number=error_number, error_name=error_name, error_description=error_description)
            
            if error_ID:
                print(f"New error created with ID {error_ID}")
        elif error_ID == 0:
            return 0

        connection_ID = self.db.connect_error_machine(machine_ID=machine_ID, error_ID=error_ID)
        if connection_ID:
            print(f"Error {error_ID} connected to machine {machine_ID} with connection ID {connection_ID}")        

        # Occurance time selection (default to current time)
        while True:
            occurance_time = input(f"Enter occurance time in format {self.date_format_human} or press enter to use current time: ").strip()
            if occurance_time == "":
                occurance_time = local_time_now(LOCAL_TIMEZONE)
                break
            else:
                try:
                    occurance_time = check_datetime(occurance_time, self.date_format_computer, self.date_format_human, LOCAL_TIMEZONE)
                    break
                except ValueError as e:
                    print(f"Invalid date format: {e}")    

        print(f"Occurance time set to current time: {occurance_time}")

        # Resolved time selection (default to None)
        while True:
            resolved_time = input(f"Enter resolved time in format {self.date_format_human} or press enter to leave it empty: ").strip()
            if resolved_time == "":
                # resolved_time = local_time_now(LOCAL_TIMEZONE)
                break
            else:
                try:
                    resolved_time = check_datetime(resolved_time, self.date_format_computer, self.date_format_human, LOCAL_TIMEZONE)
                    break
                except ValueError as e:
                    print(f"Invalid date format: {e}")

        # Notes input    
        notes = input("Enter any additional notes for the incident (optional): ").strip()
            
        insert_result = self.db.insert_incident(machine_ID=machine_ID, resolved_ID=resolved_ID, error_ID=error_ID, occurrence_time=occurance_time, resolved_time=resolved_time, notes=notes)
        if insert_result:
            print(f"New incident created with ID {insert_result}")
            return insert_result
        else:
            print("Failed to create new incident, please try again")
            return 0
        
    
    def list_incident_handler(self, machine_id: int = None, from_date_time: datetime = None, to_date_time: datetime = datetime.now(), resolved: int = None):
        """ This function handles the listing of incidents based on the given search criteria. It calls the appropriate database function to retrieve the 
        list of incidents and then prints the details of each incident.

        Args:
            machine_id (int, optional): The ID of the machine for which to list incidents. Defaults to None.
            from_date_time (datetime, optional): The start date and time for the search. Defaults to None.
            to_date_time (datetime, optional): The end date and time for the search. Defaults to datetime.now().
            resolved (int, optional): The status of the incidents to list (1 for resolved, 0 for unresolved). Defaults to None.
        """
        result = self.db.list_incidents(start_date=from_date_time, end_date=to_date_time, machine_id=machine_id, resolved_id=resolved)
        for incidents in result:
            print("")
            for keys in incidents:
                print(f"{keys}: {incidents[keys]}")


    def update_incident_status_handler(self):
        """ This function handles the updating of an incident's resolved status. It first lists all unresolved incidents and then allows the user to select an incident to update.
            The user can then enter a resolved date and time or leave it empty to use the current time.
            The function then calls the appropriate database function to update the incident's resolved status.
            
            Raises: 
                    ValueError: If the user enters an invalid date format for the resolved date and time.
        """
        incidents = self.db.list_incidents(resolved_id=1) # List unresolved incidents
        valid_ids = []
        for items in incidents:
            print("\n")
            valid_ids.append(str(items['id']))
            
            for keys in items:
                print(f"{keys}: {items[keys]}")
                
        incident_id = input("\nEnter the ID of the incident you want to update to resolved: ").strip()
        if incident_id in valid_ids:
            print(f"Chosen incident ID: {incident_id}")
            resolved_date_time = input(f"Enter resolved date and time in format {self.date_format_human} or press enter to use current time: ").strip()
            if resolved_date_time == "":
                resolved_date_time = local_time_now(LOCAL_TIMEZONE)
            else:
                try:
                    resolved_date_time = check_datetime(resolved_date_time, self.date_format_computer, self.date_format_human, LOCAL_TIMEZONE)
                except ValueError as e:
                    print(f"Invalid date format: {e}, using current time instead")
                    resolved_date_time = local_time_now(LOCAL_TIMEZONE)
                    
            try:       
                self.db.update_incident_resolved_status(incident_id=int(incident_id), resolved_id=2, resolved_time=resolved_date_time)
                print(f"Incident ID {incident_id} updated to resolved with resolved time {resolved_date_time}")
            except Exception as e:
                print(f"Failed to update incident status: {e}") 
                
        else:
            print("Incident ID not found in the list of unresolved incidents")


    def new_list_incidents_handler(self):
        """ This function handles the listing of incidents based on user-provided search criteria. 
            It prompts the user to enter a date range for the search and then calls the appropriate database function to retrieve the list of 
            incidents that occurred within that date range. The function then prints the details of each incident found.
        """
        print(f"Write search from date in format {self.date_format_human} or press enter to list incidents last 24 hours")
        from_date_time = input("From date and time: ").strip()
        to_date_time = None

        if from_date_time == "":
            from_date_time = local_time_now(LOCAL_TIMEZONE) - timedelta(days=1)
            to_date_time = local_time_now(LOCAL_TIMEZONE)
        else:
            to_date_time = input("To date and time: ").strip()
            from_date_time = check_datetime(from_date_time, self.date_format_computer, self.date_format_human, LOCAL_TIMEZONE)
            to_date_time = check_datetime(to_date_time, self.date_format_computer, self.date_format_human, LOCAL_TIMEZONE)

        print(f"\nSearching incidents from {from_date_time} to {to_date_time}")
        result = self.db.list_incidents(start_date=from_date_time, end_date=to_date_time)

        if not result:
            print("No incidents found for the given search criteria.")
        else:
            for incidents in result:
                print("\n***************************************************\n")
                for keys in incidents:
                    print(f"{keys}: {incidents[keys]}")
        
        input("\nPress Enter to go back to the operator menu...")