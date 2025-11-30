"""
Module for uploading data to a SQLite database.

This module provides functionality to create a database, define tables,
and upload/insert data into the database.
"""

import re
import sqlite3
from typing import Any

# Pattern for valid SQL identifiers (table names, column names)
_VALID_IDENTIFIER_PATTERN = re.compile(r'^[a-zA-Z_][a-zA-Z0-9_]*$')


def _validate_identifier(name: str, identifier_type: str = "identifier") -> None:
    """
    Validate that a string is a safe SQL identifier.

    Args:
        name: The identifier to validate.
        identifier_type: Type of identifier for error messages (e.g., "table name").

    Raises:
        ValueError: If the identifier is invalid.
    """
    if not name or not _VALID_IDENTIFIER_PATTERN.match(name):
        raise ValueError(
            f"Invalid {identifier_type}: '{name}'. "
            f"Must start with a letter or underscore and contain only "
            f"alphanumeric characters and underscores."
        )


class DatabaseUploader:
    """Class for uploading data to a SQLite database."""

    def __init__(self, db_path: str = "data.db"):
        """
        Initialize the DatabaseUploader.

        Args:
            db_path: Path to the SQLite database file.
        """
        self.db_path = db_path
        self.connection = None

    def connect(self) -> None:
        """Establish a connection to the database."""
        self.connection = sqlite3.connect(self.db_path)

    def close(self) -> None:
        """Close the database connection."""
        if self.connection:
            self.connection.close()
            self.connection = None

    def create_table(self, table_name: str, columns: dict[str, str]) -> None:
        """
        Create a table in the database.

        Args:
            table_name: Name of the table to create.
            columns: Dictionary mapping column names to their SQL types.

        Raises:
            ValueError: If table_name or column names contain invalid characters.
        """
        if not self.connection:
            raise RuntimeError("Database connection not established. Call connect() first.")

        _validate_identifier(table_name, "table name")
        for col_name in columns:
            _validate_identifier(col_name, "column name")

        column_defs = ", ".join(f"{name} {dtype}" for name, dtype in columns.items())
        query = f"CREATE TABLE IF NOT EXISTS {table_name} ({column_defs})"
        cursor = self.connection.cursor()
        cursor.execute(query)
        self.connection.commit()

    def upload_data(self, table_name: str, data: list[dict[str, Any]]) -> int:
        """
        Upload data to the specified table.

        Args:
            table_name: Name of the table to upload data to.
            data: List of dictionaries, where each dictionary represents a row.
                  All dictionaries must have the same keys.

        Returns:
            Number of rows inserted.

        Raises:
            ValueError: If table_name or column names contain invalid characters,
                       or if rows have inconsistent keys.
        """
        if not self.connection:
            raise RuntimeError("Database connection not established. Call connect() first.")

        if not data:
            return 0

        _validate_identifier(table_name, "table name")

        columns = list(data[0].keys())
        column_set = set(columns)
        for col_name in columns:
            _validate_identifier(col_name, "column name")

        # Validate all rows have the same keys
        for i, row in enumerate(data):
            if set(row.keys()) != column_set:
                raise ValueError(
                    f"Row {i} has different keys than the first row. "
                    f"All rows must have the same keys."
                )

        placeholders = ", ".join("?" for _ in columns)
        column_names = ", ".join(columns)
        query = f"INSERT INTO {table_name} ({column_names}) VALUES ({placeholders})"

        # Convert data to list of tuples for executemany
        values_list = [tuple(row[col] for col in columns) for row in data]

        cursor = self.connection.cursor()
        cursor.executemany(query, values_list)
        self.connection.commit()

        return len(data)

    def query_data(self, table_name: str) -> list[tuple]:
        """
        Query all data from a table.

        Args:
            table_name: Name of the table to query.

        Returns:
            List of tuples representing rows in the table.

        Raises:
            ValueError: If table_name contains invalid characters.
        """
        if not self.connection:
            raise RuntimeError("Database connection not established. Call connect() first.")

        _validate_identifier(table_name, "table name")

        cursor = self.connection.cursor()
        cursor.execute(f"SELECT * FROM {table_name}")
        return cursor.fetchall()


def main():
    """Example usage of the DatabaseUploader class."""
    # Create a database uploader instance
    uploader = DatabaseUploader("example.db")

    # Connect to the database
    uploader.connect()

    # Create a table for storing user data
    uploader.create_table("users", {
        "id": "INTEGER PRIMARY KEY",
        "name": "TEXT NOT NULL",
        "email": "TEXT",
        "age": "INTEGER"
    })

    # Sample data to upload
    sample_data = [
        {"id": 1, "name": "Alice", "email": "alice@example.com", "age": 30},
        {"id": 2, "name": "Bob", "email": "bob@example.com", "age": 25},
        {"id": 3, "name": "Charlie", "email": "charlie@example.com", "age": 35},
    ]

    # Upload the data
    rows_inserted = uploader.upload_data("users", sample_data)
    print(f"Uploaded {rows_inserted} rows to the database.")

    # Query and display the data
    results = uploader.query_data("users")
    print("Data in the database:")
    for row in results:
        print(row)

    # Close the connection
    uploader.close()


if __name__ == "__main__":
    main()
