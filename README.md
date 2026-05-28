# OPEXIO INCIDENT MONITOR

#### Video Demo:  <URL HERE>

#### Description:

**OPEXIO** is an manual incident logger for industrial use.
It is an MVP that uses SQLite as a database, but is using SQLAlchemy core so the databse can easely be swapped for other databases
like MySQL or PostgreSQL at a later time.
This is also the reason I chose SQLAlchemy Core, it gives me a nice middle ground between familiar SQL syntax, higher security against SQL injections 
(Specially important for potential WEB GUI later) and a database agnostic stack as possible.
It has a split mode as administrator, who can set up database and do configurations like creating new machines and machine groups, 
or an operator who can for example log incidents, list incidents and log new errors.

I chose this as we use an exel sheet at work for this at the moment, so it is inspired by a real world factory case.

## Installation

pip install -r requirements.txt

## How to use
To start OPEXIO you use a command line as it is purely a CLI tool at this stage.
python project.py --argument(s)

There is two options for the user modes in the incident monitor
Only one of these can be used at a time.

> --admin
>
> --op

There is also one database option:

> --test

This sets the database to a test database (Default is SQLIte test.db) rather then the production database (Default is SQLite opexio.db).

### --admin

The admin feature can be accessed by typing:

> python project.py --admin

This gives you the following admin menu:

> - "Exit"
> - "Setup database"
> - "Create new groups and machines"
> - "Create new machine for existing group"
> - "Create new resolved status"
> - "Delete groups"
> - "Delete machine"
> - "Delete resolved status"
> - "Create new error for existing machine(s)"

### --op

The operator features is accesed by typing:

> python project.py --op

This gives you the following operator menu:

> - "Exit":
> - "New incident"
> - "List incidents last 24h"
> - "List all incidents"
> - "List unresolved incidents"
> - "Update incident status to resolved"

### --test

it also has the otional value of --test
This can be used togheter with --op or --admin in order to use a test database instead of a pproduction database.
Test database defaults to: sqlite:///test.db while production database defaults to: sqlite:///opexio.db

This enables experimenting and training on a non crucial database.

The test mode is acccessed by typing:

> python project.py [--mode] --test

Where [--mode] is eiher  --op or --admin

## Files

### About the files.

Files are seperated in four layers or responsibilities:

> - Load the app i correct user mode.
> - Handle main menus for the correct user mode.
> - Handle sub menus and logic.
> - Handle database communication.

### project.py

project.py is the loader file that loads the application.
It takes care of loading the correct database and correct user mode (admin or operator)
At a later stage this might also load a GUI if added as an option.
The user mode is done trough argparse as described in the "How to use" section.


### cli.py

The cli.py controlls the main menus, and calls the right functions for admin or op features.


### cli_handlers.py

This file handles communication between the core functions and the cli.
It is responsible for calling the appropriate functions based on user input and returning the results to the cli.
I chose to seperate this file from the cli.py file to keep the cli file clean and focused on handling main admin/operator user menus. 
while this file focuses on handling sub menu functions and the logic of calling the core functions like the functions in the db.py file.

### db.py

Containes the database schema and the database functionality.
Uses SQLAlchemy core for being as database agnostic as possible.


### Database schema:
I chose to deviate from the regular python snake_case when typing database tables.
I used an old convention to easelly seperate python code and SQL tables.
The tbl prefix also helps me to easelly group and access all table names using intellisence when typing. 

tblIGroups

    > - id: Integer, autoincrement primary key
    > - groupName: String, the name of the Group of machines (For example "Cranes")

tblIMachines

    > - id: Integer, autoincrement primary key
    > - groupID: Integer, , ForeignKey from tblIGroups
    > - machineName: String, the name of the machine (For example "Crane 2")

tblErrors

    > - id: Integer, autoincrement primary key
    > - errorNumber: String, for a unique error number. This can also include characters. (For exmple "E104")
    > - errorName", String, name for the error (Like "load overhang")
    > - description: String, describes the error in plain text

tblIResolved 

    > - id: Integer, autoincrement primary key
    > - resolvedStatus: String, for unresolved or resolved

tblIncidents

> - id: Integer, autoincrement primary key
    > - machineID: Integer, ForeignKey from tblIMachines
    > - resolvedID: Integer, ForeignKey from tblIResolved
    > - errorID: Integer, ForeignKey from tblErrors
    > - occurrenceTime: Date and time with timezone for when the issue occured
    > - resolvedTime: Date and time with timezone for when the issue was resolved
    > - notes: Text, if the operator want to add aditional information.

tblIMachineError

    > - id: Integer, autoincrement primary key
    > - machineID: Integer, ForeignKey from tblIMachines
    > - errorID: Integer, ForeignKey from tblErrors

The following indexes are used to improve lookup and filtering performance:

tblIncidents: resolvedID
tblIncidents: errorID
tblIncidents: occurrenceTime
tblIMachineError: machineID
tblIMachineError: errorID

The current MVP intentionally limits incident statuses to "Resolved" and "Unresolved" in order to reduce workflow complexity for the capstone version of the project. However, the database schema was designed to allow future expansion into additional operational states such as "In Progress", "Monitoring", or "Awaiting Parts".
This is the reason Resolved/unresolve that could just be a boolean in this project is instead normalised by design. 


### config.py

Contains the database type and paths