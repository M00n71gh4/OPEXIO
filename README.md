# OPEXIO

#### Video Demo: https://youtu.be/gREJP6iULo0

#### Description:

**OPEXIO** is a manual incident logger for industrial use.
It is an MVP that uses SQLite as a database, but it is built with SQLAlchemy Core so the database can easily be swapped for other databases
like MySQL or PostgreSQL at a later time.
This is also the reason I chose SQLAlchemy Core: it gives me a nice middle ground between familiar SQL syntax, higher security against SQL injections
(especially important for a potential web GUI later) and a database-agnostic stack as far as possible.
It has two modes: an administrator, who can set up the database and do configuration like creating new machines and machine groups,
and an operator, who can for example log incidents, list incidents and log new errors.

I chose this project because we use an Excel sheet at work for this at the moment, so it is inspired by a real-world factory case.

## Installation

```
pip install -r requirements.txt
```

## How to use

OPEXIO is purely a CLI tool at this stage. To start it, use a command line:

```
python project.py --argument(s)
```

There are two user modes in the incident monitor. Only one of these can be used at a time:

> `--admin`
>
> `--op`

There is also one database option:

> `--test`

This sets the database to a test database (default is SQLite `test.db`) rather than the production database (default is SQLite `opexio.db`).

### --admin

The admin features are accessed by typing:

```
python project.py --admin
```

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

The operator features are accessed by typing:

```
python project.py --op
```

This gives you the following operator menu:

> - "Exit"
> - "New incident"
> - "List incidents last 24h"
> - "List all incidents"
> - "List unresolved incidents"
> - "Update incident status to resolved"

### --test

`--test` is an optional flag. It can be used together with `--op` or `--admin` to use a test database instead of the production database.
The test database defaults to `sqlite:///test.db`, while the production database defaults to `sqlite:///opexio.db`.

This enables experimenting and training on a non-critical database.

The test mode is accessed by typing:

```
python project.py [--mode] --test
```

where `[--mode]` is either `--op` or `--admin`.


## Files

### About the files

Files are separated into four layers of responsibility:

> - Load the app in the correct user mode.
> - Handle main menus for the correct user mode.
> - Handle sub menus and logic.
> - Handle database communication.

### project.py

`project.py` is the loader file that starts the application.
It loads the correct database and the correct user mode (admin or operator).
At a later stage it might also load a GUI, if one is added as an option.
The user mode is selected through argparse, as described in the "How to use" section.

### cli.py

`cli.py` controls the main menus and calls the right functions for admin or operator features.

### cli_handlers.py

This file handles communication between the core functions and the CLI.
It calls the appropriate functions based on user input and returns the results to the CLI.
I chose to separate this file from `cli.py` to keep `cli.py` clean and focused on the main admin/operator menus,
while this file focuses on sub menu functions and the logic of calling the core functions, like the ones in `db.py`.

### db.py

Contains the database schema and the database functionality.
Uses SQLAlchemy Core to be as database-agnostic as possible.

### config.py

Contains the database type and paths.

## Database schema

I chose to deviate from the regular Python snake_case when naming database tables.
I used an old convention to easily separate Python code from SQL tables.
The `tbl` prefix also helps me group and find all table names using IntelliSense when typing.

**tblIGroups**

| Column | Type | Description |
|---|---|---|
| id | Integer | Autoincrement primary key |
| groupName | String | Name of the group of machines (for example "Cranes") |

**tblIMachines**

| Column | Type | Description |
|---|---|---|
| id | Integer | Autoincrement primary key |
| groupID | Integer | Foreign key to tblIGroups |
| machineName | String | Name of the machine (for example "Crane 2") |

**tblErrors**

| Column | Type | Description |
|---|---|---|
| id | Integer | Autoincrement primary key |
| errorNumber | String | Unique error number. Can also include characters (for example "E104") |
| errorName | String | Name of the error (for example "load overhang") |
| description | String | Describes the error in plain text |

**tblIResolved**

| Column | Type | Description |
|---|---|---|
| id | Integer | Autoincrement primary key |
| resolvedStatus | String | Unresolved or resolved |

**tblIncidents**

| Column | Type | Description |
|---|---|---|
| id | Integer | Autoincrement primary key |
| machineID | Integer | Foreign key to tblIMachines |
| resolvedID | Integer | Foreign key to tblIResolved |
| errorID | Integer | Foreign key to tblErrors |
| occurrenceTime | Date and time with timezone | When the issue occurred |
| resolvedTime | Date and time with timezone | When the issue was resolved |
| notes | Text | Additional information from the operator |

**tblIMachineError**

| Column | Type | Description |
|---|---|---|
| id | Integer | Autoincrement primary key |
| machineID | Integer | Foreign key to tblIMachines |
| errorID | Integer | Foreign key to tblErrors |

The following indexes are used to improve lookup and filtering performance:

- tblIncidents: resolvedID
- tblIncidents: errorID
- tblIncidents: occurrenceTime
- tblIMachineError: machineID
- tblIMachineError: errorID

The current MVP intentionally limits incident statuses to "Resolved" and "Unresolved" in order to reduce workflow complexity for the capstone version of the project.
However, the database schema is designed to allow future expansion into additional operational states such as "In Progress", "Monitoring" or "Awaiting Parts".
This is why Resolved/Unresolved, which could just be a boolean in this project, is instead normalised by design.
