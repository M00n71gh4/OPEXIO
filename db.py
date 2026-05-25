from sqlalchemy import create_engine, Engine, MetaData, Table, Column, Integer, String, DateTime, ForeignKey, Text, Index, select, insert, delete
from sqlalchemy.sql import ClauseElement
from datetime import datetime, timedelta
import config 
import utils
from typing import Sequence

#*****************************************************
#   Setting up the database schema / defining tables
#*****************************************************
metadata = MetaData()

# Defining Tables

tblIGroups = Table('tblIGroups',
    metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('groupName', String)
)

tblIResolved = Table('tblIResolved', 
    metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('resolvedStatus', String, unique=True, nullable=False)
)

tblIMachines = Table('tblIMachines',
    metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('groupID', Integer, ForeignKey('tblIGroups.id', ondelete="SET NULL"), nullable=True),
    Column('machineName', String)
)

tblErrors = Table('tblErrors',
    metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('machineID', Integer, ForeignKey('tblIMachines.id')),
    Column('errorNumber', String),
    Column('errorName', String),
    Column('description', String)
)

tblIResolution = Table('tblIResolution',
    metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('machineID', Integer, ForeignKey('tblIMachines.id')),
    Column('errorID', Integer, ForeignKey('tblErrors.id')),
    Column('notes', Text)
)

tblIncidents = Table('tblIncidents',
    metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('machineID', Integer, ForeignKey('tblIMachines.id')),
    Column('resolvedID', Integer, ForeignKey('tblIResolved.id')),
    Column('resolutionID', Integer, ForeignKey('tblIResolution.id')),
    Column('occurrenceTime', DateTime, nullable=False),
    Column('resolvedTime', DateTime, nullable=True),
    Column('notes', Text)
)

# Creating Indexes
Index('idx_machineID', tblIncidents.c.machineID)
Index('idx_resolvedID', tblIncidents.c.resolvedID)
Index('idx_resolutionID', tblIncidents.c.resolutionID)
Index('idx_occurrenceTime', tblIncidents.c.occurrenceTime)

# Standard values for the function: populate_standard_resolved_statuses
resolved_statuses = ('Unresolved', 
                    'In Progress', 
                    'Temporarily resolved', 
                    'Resolved'
                    )


class Database:
    def __init__(self, db_URL: str, echo: bool=False):
        """initializes Database and creates an SQLAlchemy core database engine

        Args:
            db_URL (str): Path do database
            echo (bool, optional): Debug mode, logs SQL strings to console. Defaults to False.
        """
        print(f"db.py - {db_URL}")
        self.engine = create_engine(db_URL, echo=echo)

    def setup_database(self) -> dict:
        """Create all tables if they don't exist. Listed manually to avoid issues with order of creation and foreign keys (Especially SQLite)

        Returns:
            dict: dictionary with: 
                - code: 200 = ok, 400 = error, 
                - message: sucessfull or error message,
                - data: if payload is provided.
        """ 
        try:
            print("Creating all tables...")
            with self.engine.begin() as conn:
                metadata.create_all(conn, tables=[
                    tblIGroups,
                    tblIResolved,
                    tblIMachines,
                    tblErrors,
                    tblIResolution,
                    tblIncidents
                    ])

            return utils.status_ok()
        except Exception as e:
            return utils.status_error(payload=str(e))
        
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
    """
    def delete_tables(self)-> bool|str:
        
        with self.engine.begin() as conn:
            metadata.drop_all(conn)  
            return utils.status_ok()


    def delete_groups(self, group_id: int)-> dict:
        # Delete a machine group and all belonging machines, errors, resolutions, and incidents
        try:
            with self.engine.begin() as conn:
                stm = delete(tblIGroups).where(tblIGroups.c.id == group_id)
                conn.execute(stm)
            return utils.status_ok()
        except Exception as e:
            return utils.status_error(payload=str(e))
    """
    def populate_standard_resolved_statuses(self, status: tuple = resolved_statuses)-> bool|str:
        """This gives the pre defines resolved statuses for the database.
            Unresolved, In Progress, Temporarily resolved, or Resolveds.

        Args:
            status (tuple, optional): Defaults to resolved_statuses.

        Returns:
            bool|str: Returns True if sucessfull, a str with error if not
        """
        try:
            with self.engine.begin() as conn:
                #Defaul statuses populated to the database
                for status in status:
                    #Try to insert, ignore if already exists
                    conn.execute(
                        tblIResolved.insert().values(resolvedStatus=status)
                        )
            return utils.status_ok()
        except Exception as e:
            return utils.status_error(payload=str(e))

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
        
        
        else:
            with self.engine.connect() as conn:    
                return conn.execute(stm).mappings().all() #.fetchall() is legacy core 1.x, .all() is core 2.x way
            #return False
        
    def list_incidents(self, resolved: int=None, machine_id: int=None, start_date: datetime=None, end_date: datetime=None, note_search: str=None):
        stm = select(tblIncidents)
        conditions = []
        
        if resolved:
            conditions.append(tblIncidents.c.resolvedID == resolved)
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
        
    def show_resolution(self, machne_id=None, error_id=None, note_search=None):
        stm = select(tblIResolution)
        conditions = []

        if machne_id:
            conditions.append(tblIResolution.c.machineID == machne_id)
        if error_id:
            conditions.append(tblIResolution.c.errorID == error_id)
        if note_search:
            conditions.append(tblIResolution.c.notes.ilike(f"%{note_search}%"))
            
        if conditions:
            stm = stm.where(*conditions)
        with self.engine.connect() as conn:
            return conn.execute(stm).mappings().all()

    def list_machines(self, group_id=None, machine_name=None):
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

    def list_errors(self, machine_id=None, error_number=None, error_name=None, description=None):
        stm = select(tblErrors)
        conditions = []

        if machine_id:
            conditions.append(tblErrors.c.machineID == machine_id)
        if error_number:
            conditions.append(tblErrors.c.errornumber.ilike(f"%{error_number}%"))
        if error_name:
            conditions.append(tblErrors.c.errorName.ilike(f"%{error_name}%"))
        if description:
            conditions.append(tblErrors.c.description.ilike(f"%{description}%"))
            
        if conditions:
            stm = stm.where(*conditions)
        with self.engine.connect() as conn:
            return conn.execute(stm).mappings().all()

    def list_resolved_statuses(self):
        stm = select(tblIResolved)
        with self.engine.connect() as conn:
            return conn.execute(stm).mappings().all()

    #*****************************************************
    #               INSERT functions
    #*****************************************************
    # For admin  ********************************************************************
    def insert_group(self, group_name=None):
        if not group_name:
            return None

        stm = insert(tblIGroups).values(groupName=group_name).returning(tblIGroups.c.id)
        with self.engine.begin() as conn:
            return conn.execute(stm).scalar_one_or_none()
        
    #******************************************************************************************************************************************************************
    # Generalized insert function
    #******************************************************************************************************************************************************************
    
    def new_insert(self, table: Table, conditions: Sequence[ClauseElement]) -> int:
        """ Generalized insert function to insert a new row into a specified table with given conditions.

        Args:
            table (Table): SQLAlchemy Table object where to insert new row
            conditions (Sequence[ClauseElement]): A sequence of SQLAlchemy ClauseElement conditions to define the data to insert.
            can be created using {"column_name": value, ...} in form of a dictionary or other iterables.

        Raises:
            ValueError: If no conditions are provided.

        Returns:
            int: The ID of the newly inserted row, or None if no row was inserted.
        """
        if len(conditions) == 0:
            raise ValueError("At least one condition must be provided for insertion.")
        
        stm = insert(table).values(**conditions).returning(table.c.id)
        with self.engine.begin() as conn:
            return conn.execute(stm).scalar_one_or_none()
    
    def insert_machine(self, machine_name=None, group_id=None):
            conditions = {}

            if machine_name:
                conditions["machineName"]= machine_name
            if group_id:
                conditions["groupID"]= group_id
            print(f"********************************************************************************* TYPE: {type(group_id)} VALUE: {group_id} *******************************")
            if not conditions:
                return None  # No data to insert

            stm = insert(tblIMachines).values(**conditions).returning(tblIMachines.c.id)    
            with self.engine.begin() as conn:
                return conn.execute(stm).scalar_one_or_none()

    def insert_resolved(self, resolved_status=None):
        conditions = {}
        
        if resolved_status:
            conditions["resolvedStatus"]= resolved_status
            
        if not conditions:
            return None  # No data to insert

        stm = insert(tblIResolved).values(**conditions).returning(tblIResolved.c.id)    
        with self.engine.begin() as conn:
            return conn.execute(stm).scalar_one_or_none()

    # For production ********************************************************************

    def insert_incident(self, machineID=None, resolvedID=None, resolutionID=None, occurrenceTime=None, resolvedTime=None, notes=None):
        conditions = {}

        if machineID:
            conditions["machineID"]= machineID
        if resolvedID:
            conditions["resolvedID"]= resolvedID
        if resolutionID:
            conditions["resolutionID"]= resolutionID
        if occurrenceTime:
            conditions["occurrenceTime"]= occurrenceTime
        if resolvedTime:
            conditions["resolvedTime"]= resolvedTime
        if notes:
            conditions["notes"]= notes
            
        if not conditions:
            return None  # No data to insert

        stm = insert(tblIncidents).values(**conditions).returning(tblIncidents.c.id)    
        with self.engine.begin() as conn:
            return conn.execute(stm).scalar_one_or_none()
        
    def insert_resolution(self, machineID=None, errorID=None, notes=None):
        conditions = {}

        if machineID:
            conditions["machineID"]= machineID
        if errorID:
            conditions["errorID"]= errorID
        if notes:
            conditions["notes"]= notes

        if not conditions:
            return None  # No data to insert

        stm = insert(tblIResolution).values(**conditions).returning(tblIResolution.c.id)    
        with self.engine.begin() as conn:
            return conn.execute(stm).scalar_one_or_none()

    def insert_error(self, error_number=None, error_name=None, description=None):
        conditions = {}

        if error_number:
            conditions["errorNumber"]= error_number
        if error_name:
            conditions["errorName"]= error_name
        if description:
            conditions["description"]= description

        if not conditions:
            return None  # No data to insert

        stm = insert(tblErrors).values(**conditions).returning(tblErrors.c.id)    
        with self.engine.begin() as conn:
            return conn.execute(stm).scalar_one_or_none()
        
        
