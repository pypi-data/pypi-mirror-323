from setuptools import setup, find_packages

setup(
    name='portableDB',
    version='2.0',
    author='DoubleSquad',
    description="This library is an easyest way to use local database!",
    long_description_content_type="text/markdown",
    long_description="""
    
# PortableDB Documentation

PortableDB is a lightweight, easy-to-use Python package for creating, managing, and interacting with portable databases.

## Installation

To install PortableDB, use pip:

```bash
pip install portableDB
```

## Methods

### ` db = DATABASE(name)`

Defines the database to work with. You must initialize a `DATABASE` object before using other methods.

- **Arguments:**
  - `name` (str): The name of the database file (e.g., `'Database.db'`).
    - This file will be created if it doesn't already exist.

### `db.LogType(Type)`

Sets the logging state for database operations.

- **Arguments:**
  - `Type` (str): Can be one of the following:
    - `'COLORFUL'`: Enables colorful logs for better readability.
    - `'BASE'`: Enables normal command-line logging.
    - `'NONE'`: Disables logging output.

### `db.CreateDatabase()`

Creates a new database.

- **Arguments:**
  - No arguments are required.

### `db.WriteDatabase(information, cell)`

Writes data to the database.

- **Arguments:**
  - `information` (array): An array of values to write (e.g., `['String value', 32]`).
  - `cell` (str): The cell where the data will be written (e.g., `'LOL'`).
    - Cell can be of any type or value.

### `db.WriteIndex(information, cell, index)`

Writes data to a specific index within a specified cell.

- **Arguments:**
  - `information` (any type): The information to write (e.g., `'PON'`).
  - `cell` (str): The cell in which to write the information (e.g., `'LOL'`).
    - Cell can be of any type or value.
  - `index` (int): The index at which to write the information (e.g., `0`).

### `db.ReadDatabase(cell, index)`

Reads data from the database.

- **Arguments:**
  - `cell` (str): The cell to read from (e.g., `'LOL'`).
  - `index` (str or int, optional): 
    - `'ALL'`: Reads all elements in the specified cell.
    - An integer: Reads the specific element at the given index in the array.
    - If this argument is ignored, it behaves like `'ALL'` was given.

- **Returns:**
  - The data read from the specified cell and index.

### `db.RenameDatabase(newName)`

Renames the database.

- **Arguments:**
  - `newName` (str): The new name for the database (do not include the file type like '.db').

### `db.DeleteDatabase()`

Deletes the specified database.

- **Arguments:**
  - No arguments are required.

     """,
    packages=find_packages(),
    install_requires=[
        'colorama>=0.4.6'
    ],
)