"""Tests for the upload_data module."""

import os
import sqlite3
import tempfile
import unittest

from upload_data import DatabaseUploader


class TestDatabaseUploader(unittest.TestCase):
    """Test cases for the DatabaseUploader class."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.temp_dir, "test.db")
        self.uploader = DatabaseUploader(self.db_path)

    def tearDown(self):
        """Clean up test fixtures."""
        if self.uploader.connection:
            self.uploader.close()
        if os.path.exists(self.db_path):
            os.remove(self.db_path)
        os.rmdir(self.temp_dir)

    def test_connect_creates_database(self):
        """Test that connect creates the database file."""
        self.uploader.connect()
        self.assertTrue(os.path.exists(self.db_path))
        self.assertIsNotNone(self.uploader.connection)

    def test_close_closes_connection(self):
        """Test that close properly closes the connection."""
        self.uploader.connect()
        self.uploader.close()
        self.assertIsNone(self.uploader.connection)

    def test_create_table(self):
        """Test that create_table creates a table in the database."""
        self.uploader.connect()
        self.uploader.create_table("test_table", {
            "id": "INTEGER PRIMARY KEY",
            "name": "TEXT"
        })

        # Verify table exists
        cursor = self.uploader.connection.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='test_table'")
        result = cursor.fetchone()
        self.assertIsNotNone(result)
        self.assertEqual(result[0], "test_table")

    def test_create_table_without_connection_raises_error(self):
        """Test that create_table without connection raises RuntimeError."""
        with self.assertRaises(RuntimeError):
            self.uploader.create_table("test_table", {"id": "INTEGER"})

    def test_upload_data(self):
        """Test that upload_data inserts data correctly."""
        self.uploader.connect()
        self.uploader.create_table("users", {
            "id": "INTEGER PRIMARY KEY",
            "name": "TEXT"
        })

        data = [
            {"id": 1, "name": "Alice"},
            {"id": 2, "name": "Bob"}
        ]

        rows_inserted = self.uploader.upload_data("users", data)
        self.assertEqual(rows_inserted, 2)

        # Verify data was inserted
        cursor = self.uploader.connection.cursor()
        cursor.execute("SELECT * FROM users")
        results = cursor.fetchall()
        self.assertEqual(len(results), 2)
        self.assertEqual(results[0], (1, "Alice"))
        self.assertEqual(results[1], (2, "Bob"))

    def test_upload_empty_data(self):
        """Test that upload_data with empty list returns 0."""
        self.uploader.connect()
        self.uploader.create_table("users", {"id": "INTEGER"})

        rows_inserted = self.uploader.upload_data("users", [])
        self.assertEqual(rows_inserted, 0)

    def test_upload_data_without_connection_raises_error(self):
        """Test that upload_data without connection raises RuntimeError."""
        with self.assertRaises(RuntimeError):
            self.uploader.upload_data("users", [{"id": 1}])

    def test_query_data(self):
        """Test that query_data returns all rows from a table."""
        self.uploader.connect()
        self.uploader.create_table("items", {
            "id": "INTEGER PRIMARY KEY",
            "value": "TEXT"
        })

        data = [
            {"id": 1, "value": "item1"},
            {"id": 2, "value": "item2"},
            {"id": 3, "value": "item3"}
        ]
        self.uploader.upload_data("items", data)

        results = self.uploader.query_data("items")
        self.assertEqual(len(results), 3)
        self.assertEqual(results[0], (1, "item1"))
        self.assertEqual(results[1], (2, "item2"))
        self.assertEqual(results[2], (3, "item3"))

    def test_query_data_without_connection_raises_error(self):
        """Test that query_data without connection raises RuntimeError."""
        with self.assertRaises(RuntimeError):
            self.uploader.query_data("users")

    def test_create_table_invalid_table_name_raises_error(self):
        """Test that create_table with invalid table name raises ValueError."""
        self.uploader.connect()
        with self.assertRaises(ValueError):
            self.uploader.create_table("users; DROP TABLE users", {"id": "INTEGER"})

    def test_create_table_invalid_column_name_raises_error(self):
        """Test that create_table with invalid column name raises ValueError."""
        self.uploader.connect()
        with self.assertRaises(ValueError):
            self.uploader.create_table("users", {"id; DROP TABLE users": "INTEGER"})

    def test_upload_data_invalid_table_name_raises_error(self):
        """Test that upload_data with invalid table name raises ValueError."""
        self.uploader.connect()
        with self.assertRaises(ValueError):
            self.uploader.upload_data("users; DROP TABLE users", [{"id": 1}])

    def test_upload_data_invalid_column_name_raises_error(self):
        """Test that upload_data with invalid column name raises ValueError."""
        self.uploader.connect()
        self.uploader.create_table("users", {"id": "INTEGER"})
        with self.assertRaises(ValueError):
            self.uploader.upload_data("users", [{"id; DROP TABLE users": 1}])

    def test_query_data_invalid_table_name_raises_error(self):
        """Test that query_data with invalid table name raises ValueError."""
        self.uploader.connect()
        with self.assertRaises(ValueError):
            self.uploader.query_data("users; DROP TABLE users")

    def test_upload_data_inconsistent_keys_raises_error(self):
        """Test that upload_data with inconsistent keys raises ValueError."""
        self.uploader.connect()
        self.uploader.create_table("users", {
            "id": "INTEGER PRIMARY KEY",
            "name": "TEXT"
        })
        data = [
            {"id": 1, "name": "Alice"},
            {"id": 2, "email": "bob@example.com"}  # Different keys
        ]
        with self.assertRaises(ValueError):
            self.uploader.upload_data("users", data)


if __name__ == "__main__":
    unittest.main()
