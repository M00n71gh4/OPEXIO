from sqlalchemy import create_engine, make_url, MetaData, Table, Column, Integer, String, DateTime, ForeignKey, Text, Index, make_url, select, insert, delete, join, inspect, update
from sqlalchemy.sql import ClauseElement
from datetime import datetime
from pathlib import Path 
from typing import Sequence

#*****************************************************
#   Setting up the database schema / defining tables
#*****************************************************
metadata = MetaData()

# Defining Tables

tblIGroups = Table("tblIGroups",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("groupName", String)
)

tblIMachines = Table("tblIMachines",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("groupID", Integer, ForeignKey("tblIGroups.id", ondelete="SET NULL"), nullable=True),
    Column("machineName", String)
)

tblErrors = Table("tblErrors",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("errorNumber", String),
    Column("errorName", String),
    Column("description", String)
)

tblIResolved = Table("tblIResolved", 
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("resolvedStatus", String, unique=True, nullable=False)
)

tblIncidents = Table("tblIncidents",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("machineID", Integer, ForeignKey("tblIMachines.id")),
    Column("resolvedID", Integer, ForeignKey("tblIResolved.id")),
    Column("errorID", Integer, ForeignKey("tblErrors.id")),
    Column("occurrenceTime", DateTime(timezone=True), nullable=False),
    Column("resolvedTime", DateTime(timezone=True), nullable=True),
    Column("notes", Text)
)

tblIMachineError = Table("tblIMachineError",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("machineID", Integer, ForeignKey("tblIMachines.id")),
    Column("errorID", Integer, ForeignKey("tblErrors.id"))
)
# Creating Indexes
Index("idx_resolvedID", tblIncidents.c.resolvedID)
Index("idx_errorID", tblIncidents.c.errorID)
Index("idx_occurrenceTime", tblIncidents.c.occurrenceTime)
Index("idx_machineID", tblIMachineError.c.machineID)
Index("idx_machineErrorID", tblIMachineError.c.errorID)


# Standard values for the function: populate_standard_resolved_statuses
# Having them as a dict allows for easier expansion in the future if needed.
resolved_statuses = (
                    {"resolvedStatus":"Unresolved"}, 
                    {"resolvedStatus":"Resolved"}
                    )


class Database:
    def __init__(self, db_URL: str, echo: bool=False):
        """initializes Database and creates an SQLAlchemy core database engine

        Args:
            db_URL (str): Path do database
            echo (bool, optional): Debug mode, logs SQL strings to console. Defaults to False.
        """
        self.db_URL = db_URL
        self.engine = create_engine(db_URL, echo=echo)
        
    def check_if_database_exists(self) -> bool:
        """Checks if the database exists by checking the file.

        Returns:
            bool: Returns True if the connection is sucessfull, False if not.
        """
        # At the moment it checks for SQLite database files, but this can be expanded in the future to check for other types of databases.
        url = make_url(self.db_URL)  
        if url.get_backend_name() == "sqlite":
            return Path(url.database).exists()
        return False


    def setup_database(self) -> list[str]:
        """Create all tables if they don't exist. Listed manually to avoid issues with order of creation and foreign keys (Especially SQLite)

        Returns:
            list[str]: Creates a list with the tables that is created.
        """
        inspector = inspect(self.engine)
        before = inspector.get_table_names()
        
        with self.engine.begin() as conn:
            metadata.create_all(conn, tables=[
                tblIGroups,
                tblIResolved,
                tblIMachines,
                tblErrors,
                tblIncidents,
                tblIMachineError
                ])
            
        # Recreates the inspector to avoid caching of tables    
        inspector = inspect(self.engine)   
        
        after = inspector.get_table_names()
        created_tables = set(after) - set(before)
        
        return list(created_tables)
        
# GENERAL DELETE STATEMENT

    def delete_rows(self, table: Table, condition: Sequence[ClauseElement]) -> int:
        """Delete rows from a table based on given conditions.

        Args:
            table (Table): SQLAlchemy Table object from which to delete rows.
            condition (Sequence[ClauseElement]): A sequence of SQLAlchemy ClauseElement conditions to filter which rows to delete.
            can be created using [table.c.column_name == value]
            
        Raises:
            ValueError: If no conditions are provided.

        Returns:
            int: Number of rows deleted.
        """
        if len(condition) == 0:
            raise ValueError("At least one condition must be provided for deletion.")
        
        with self.engine.begin() as conn:
            stm = delete(table).where(*condition)
            result = conn.execute(stm)
            
        return result.rowcount
    

    #*****************************************************
    #               SELECT / list functions
    #*****************************************************
    def list_groups(self, machine_search: str=None)-> list|bool:
        """Search for machine groups.

        Args:
            machine_search (str, optional): Search criteria for machine groups. Defaults to None.

        Returns:
            list|bool:  Returns a list if there are results, False if not.
        """
        stm = select(tblIGroups)
        conditions = []

        # Could be done winthout conditions list, but this way it's easier to expand with more filters later if needed.
        if machine_search is not None:
            conditions.append(tblIGroups.c.groupName.ilike(f"%{machine_search}%")) # '.ilike' not case sensetive '.like' is c.s in most DBs

        if conditions:
            stm = stm.where(*conditions)

        with self.engine.connect() as conn:    
            return conn.execute(stm).mappings().all() #.fetchall() is legacy core 1.x, .all() is core 2.x way
            #return False

    def list_incidents(self, resolved_id: int=None, machine_id: int=None, start_date: datetime=None, end_date: datetime=None, note_search: str=None)-> list:
        """Lists incidents based on given search criteria.

        Args:
            resolved_id (int, optional): The ID of the resolved status to filter incidents by. Defaults to None.
            machine_id (int, optional): The ID of the machine to filter incidents by. Defaults to None.
            start_date (datetime, optional): The start date for filtering incidents. Defaults to None.
            end_date (datetime, optional): The end date for filtering incidents. Defaults to None.
            note_search (str, optional): The search term for filtering incidents by notes. Defaults to None.

        Returns:
            list[dict]: A list of dictionaries representing the filtered incidents.
        """
        stm = select(
                    tblIncidents.c.id,
                    tblIncidents.c.occurrenceTime,
                    tblIncidents.c.resolvedTime,
                    tblIncidents.c.notes,
                    tblErrors.c.errorNumber,
                    tblErrors.c.errorName,
                    tblErrors.c.description,
                    tblIResolved.c.resolvedStatus, 
                    tblIMachines.c.machineName).join(
                    tblIResolved, tblIncidents.c.resolvedID == tblIResolved.c.id).join(
                    tblIMachines, tblIncidents.c.machineID == tblIMachines.c.id).join(
                    tblErrors, tblIncidents.c.errorID == tblErrors.c.id)
        conditions = []

        if resolved_id:
            conditions.append(tblIncidents.c.resolvedID == resolved_id)
        if machine_id:
            conditions.append(tblIncidents.c.machineID == machine_id)
        if start_date:
            conditions.append(tblIncidents.c.occurrenceTime >= start_date)
        if end_date:
            conditions.append(tblIncidents.c.occurrenceTime <= end_date)
        if note_search:
            conditions.append(tblIncidents.c.notes.ilike(f"%{note_search}%"))
        if conditions:
            stm = stm.where(*conditions)
            
        with self.engine.connect() as conn:    
            return conn.execute(stm).mappings().all() 
        

    def list_machines(self, group_id=None, machine_name=None)-> list:
        """Lists machines based on given search criteria.
        
        Args:
            group_id (int, optional): The ID of the group to filter machines by. Defaults to None.
            machine_name (str, optional): The name of the machine to filter by. Defaults to None.

        Returns:
            list[dict]: A list of dictionaries representing the filtered machines.
        """
        stm = select(tblIMachines)
        conditions = []

        if group_id:
            conditions.append(tblIMachines.c.groupID == group_id)
        if machine_name:
            conditions.append(tblIMachines.c.machineName.ilike(f"%{machine_name}%"))
            
        if conditions:
            stm = stm.where(*conditions)
        with self.engine.connect() as conn:
            return conn.execute(stm).mappings().all()

    def list_errors(self, machine_id=None, error_number=None, error_name=None, description=None)-> list:
        """Lists errors based on given search criteria. If machine_id is provided, it will list errors that are connected to that machine through the tblIMachineError table.

        Args:
            machine_id (int, optional): The ID of the machine to filter errors by. Defaults to None.
            error_number (str, optional): The error number to filter by. Defaults to None.
            error_name (str, optional): The error name to filter by. Defaults to None.
            description (str, optional): The description to filter by. Defaults to None.

        Returns:
            list[dict]: A list of dictionaries representing the filtered errors.
        

        Returns:
            list[dict]: A list of dictionaries representing the filtered errors.
        """
        tbl_join = join(tblErrors, tblIMachineError, tblErrors.c.id == tblIMachineError.c.errorID)
        stm = select(tblErrors, tblIMachineError).select_from(tbl_join)
        
        conditions = []

        if machine_id:
            conditions.append(tblIMachineError.c.machineID == machine_id)
        if error_number:
            conditions.append(tblErrors.c.errorNumber.ilike(f"%{error_number}%"))   
        if error_name:
            conditions.append(tblErrors.c.errorName.ilike(f"%{error_name}%"))
        if description:
            conditions.append(tblErrors.c.description.ilike(f"%{description}%"))
            
        if conditions:
            stm = stm.where(*conditions)
        with self.engine.connect() as conn:
            return conn.execute(stm).mappings().all()

    def list_resolved_statuses(self)-> list:
        """Lists all resolved statuses in the database.

        Returns:
            list[dict]: A list of dictionaries representing the resolved statuses.
        """
        stm = select(tblIResolved)
        with self.engine.connect() as conn:
            return conn.execute(stm).mappings().all()

    #*****************************************************
    #               INSERT functions
    #*****************************************************
    # For admin  ********************************************************************
    def insert_group(self, group_name: str=None):
        """Inserts a new group into the database.

        Args:
            group_name (str, optional): _description_. Defaults to None.

        Returns:
            int: The ID of the inserted group.
        """
        if not group_name:
            return None

        stm = insert(tblIGroups).values(groupName=group_name).returning(tblIGroups.c.id)
        with self.engine.begin() as conn:
            return conn.execute(stm).scalar_one_or_none()
        
    
    def insert_resolved_statuses(self, status: list[dict] = resolved_statuses)-> int:
        """Inserts resolved statuses into the database if they don't already exist.

        Args:
            status (list[dict], optional): A list of dictionaries representing the resolved statuses to insert. Defaults to resolved_statuses.

        Returns:
            int: The number of rows inserted into the database. Returns 0 if no new rows were inserted (i.e., all provided statuses already exist in the database).
        """
        with self.engine.begin() as conn:
            # Gets a list of existing resolved statuses in the database
            existing_statuses = conn.execute(select(tblIResolved.c.resolvedStatus)).scalars().all()
            existing_statuses_set = set(existing_statuses)
            missing_statuses = [s for s in status if s['resolvedStatus'] not in existing_statuses_set]
            
            # If there are no missing statuses, return 0 to indicate that no new rows were inserted
            # If there are missing statuses, insert them and return the number of rows inserted
            if not missing_statuses:
                return 0
            else:
                stm = insert(tblIResolved).values(missing_statuses)
                result = conn.execute(stm)
                return result.rowcount


    def insert_machine(self, machine_name=None, group_id=None)-> int:
        """Inserts a new machine into the database.

        Args:
            machine_name (str, optional): The name of the machine. Defaults to None.
            group_id (int, optional): The ID of the group to which the machine belongs. Defaults to None.

        Returns:
            int: The ID of the inserted machine.
        """
        conditions = {}

        if machine_name:
            conditions["machineName"]= machine_name
        if group_id:
            conditions["groupID"]= group_id

        if not conditions:
            return 0  # No data to insert

        stm = insert(tblIMachines).values(**conditions).returning(tblIMachines.c.id)    
        with self.engine.begin() as conn:
            return conn.execute(stm).scalar_one_or_none()

    # Is this function needed. insert_resolved_statyses is more complete and can be used to insert single statuses as well.
    def insert_resolved(self, resolved_status=None)->int:
        """Inserts a new resolved status into the database.

        Args:
            resolved_status (str, optional): The status of the resolved incident. Defaults to None.

        Returns:
            int: The ID of the inserted resolved status.
        """
        conditions = {}
        
        if resolved_status:
            conditions["resolvedStatus"]= resolved_status
            
        if not conditions:
            return None  # No data to insert

        stm = insert(tblIResolved).values(**conditions).returning(tblIResolved.c.id)    
        with self.engine.begin() as conn:
            return conn.execute(stm).scalar_one_or_none()




    # For production ********************************************************************

    def insert_incident(self, machine_ID: int = None, resolved_ID: int = None, error_ID: int = None, occurrence_time: datetime = None, resolved_time: datetime = None, notes: str = None)->int:
        """Inserts a new incident into the database.

        Args:
            machine_ID (int, optional): The ID of the machine associated with the incident. Defaults to None.
            resolved_ID (int, optional): The ID of the resolved status. Defaults to None.
            error_ID (int, optional): The ID of the error associated with the incident. Defaults to None.
            occurrence_time (datetime, optional): The time when the incident occurred. Defaults to None.
            resolved_time (datetime, optional): The time when the incident was resolved. Defaults to None.
            notes (str, optional): Additional notes about the incident. Defaults to None.

        Returns:
            int: The ID of the inserted incident.
        """
        conditions = {}
        print("Start generating conditions:")
        if machine_ID:
            conditions["machineID"]= machine_ID
        if resolved_ID:
            conditions["resolvedID"]= resolved_ID
        if error_ID:
            conditions["errorID"]= error_ID
        if occurrence_time:
            conditions["occurrenceTime"]= occurrence_time
        if resolved_time:
            conditions["resolvedTime"]= resolved_time
        if notes:
            conditions["notes"]= notes
        print("Start saving conditions to DB")
        if not conditions:
            return 0  # No data to insert
        else:
            stm = insert(tblIncidents).values(**conditions).returning(tblIncidents.c.id)    
            with self.engine.begin() as conn:
                return conn.execute(stm).scalar_one_or_none()


    def insert_error(self, error_number=None, error_name=None, error_description=None)-> int:
        """Inserts a new error into the database.

        Args:
            error_number (str, optional): The number of the error. Defaults to None. string is used to allow for error numbers that contain letters or special characters, which is common in many error coding systems.
            error_name (str, optional): The name of the error. Defaults to None.
            error_description (str, optional): The description of the error. Defaults to None.

        Returns:
            int: The ID of the inserted error.
        """
        conditions = {}

        if error_number:
            conditions["errorNumber"]= error_number
        if error_name:
            conditions["errorName"]= error_name
        if error_description:
            conditions["description"]= error_description

        if not conditions:
            return None  # No data to insert

        stm = insert(tblErrors).values(**conditions).returning(tblErrors.c.id)    
        with self.engine.begin() as conn:
            return conn.execute(stm).scalar_one_or_none()
        
        
    def connect_error_machine(self, machine_ID: int, error_ID: int) -> int:
        """ Connects an error to a machine

        Args:
            machine_ID (int): ID of the machine to connect
            error_ID (int): ID of the error to connect
        Raises:
            ValueError: If either machine_ID or error_ID is not provided, a ValueError is raised with an appropriate error message.

        Returns:
            int: Returns the ID of the new connection in the tblIMachineError table if the connection is successfully created, or None if the connection already exists.    
        """
        if machine_ID == None or error_ID == None:
            raise ValueError("Both machine_ID and error_ID must be provided.")
        
        stm = insert(tblIMachineError).values(machineID=machine_ID, errorID=error_ID).returning(tblIMachineError.c.id)
        with self.engine.begin() as conn:
            return conn.execute(stm).scalar_one_or_none()
        
        
    def update_incident_resolved_status(self, incident_id: int, resolved_id: int, resolved_time: datetime=None) -> int:
        """Updates the resolved status of an incident.

        Args:
            incident_id (int): ID of the incident to update
            resolved_id (int): ID of the new resolved status
            resolved_time (datetime, optional): Time when the incident was resolved. If not provided, the current time will be used. Defaults to None.

        Raises:
            ValueError: If either incident_id or resolved_id is not provided, a ValueError is raised with an appropriate error message.
            
        Returns:
            int: Returns the number of rows updated in the tblIncidents table (should be 1 if the update is successful, or 0 if no incident with the given ID exists).
        """
        if incident_id == None or resolved_id == None:
            raise ValueError("Both incident_id and resolved_id must be provided.")
        
        if not resolved_time:
            resolved_time = datetime.now()

        stm = (
            update(tblIncidents)
            .where(tblIncidents.c.id == incident_id)
            .values(resolvedID=resolved_id, resolvedTime=resolved_time)
        )
        with self.engine.begin() as conn:
            result = conn.execute(stm)
            return result.rowcount