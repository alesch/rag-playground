"""
Tests for SQLiteClient using the VectorDatabaseContract.
"""

import pytest
import os
import tempfile
from pathlib import Path
from src.infrastructure.database.sqlite_client import SQLiteClient
from .contract_vector_db import VectorDatabaseContract

class TestSQLiteClient(VectorDatabaseContract):
    """
    Runs the standard contract tests against SQLiteClient.
    """
    
    @pytest.fixture(autouse=True)
    def setup_mocks(self, mock_embeddings):
        """Automatically mock embeddings for all tests in this class."""
        pass

    @pytest.fixture(scope="module")
    def client(self):
        """
        Fixture that creates an in-memory SQLite DB.
        """
        # Initialize client with in-memory database
        db_client = SQLiteClient(db_path=":memory:")
        
        yield db_client
        
        # Cleanup
        db_client.conn.close()

    def test_domain_tables_initialization(self, client):
        """Verify that domain tables are created on initialization."""
        cursor = client.conn.cursor()
        
        # List of expected tables
        expected_tables = {
            "questionnaires",
            "questions",
            "runs",
            "answers",
            "document_chunks",
            "vec_document_chunks"
        }
        
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' OR type='view'")
        tables = {row[0] for row in cursor.fetchall()}
        
        # Check that all expected tables exist
        for table in expected_tables:
            assert table in tables, f"Table {table} missing from database"
            
        # Verify foreign keys are enabled
        cursor.execute("PRAGMA foreign_keys")
        assert cursor.fetchone()[0] == 1
