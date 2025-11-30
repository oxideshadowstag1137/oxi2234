# oxi2234

Upload data to a SQLite database.

## Features

- Create database tables with custom schemas
- Upload data from Python dictionaries to database tables
- Query data from database tables

## Usage

```python
from upload_data import DatabaseUploader

# Create a database uploader instance
uploader = DatabaseUploader("my_database.db")

# Connect to the database
uploader.connect()

# Create a table
uploader.create_table("users", {
    "id": "INTEGER PRIMARY KEY",
    "name": "TEXT NOT NULL",
    "email": "TEXT"
})

# Upload data
data = [
    {"id": 1, "name": "Alice", "email": "alice@example.com"},
    {"id": 2, "name": "Bob", "email": "bob@example.com"}
]
uploader.upload_data("users", data)

# Query data
results = uploader.query_data("users")

# Close the connection
uploader.close()
```

## Running the Example

```bash
python upload_data.py
```

## Running Tests

```bash
python -m unittest test_upload_data -v
```
