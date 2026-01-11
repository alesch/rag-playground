"""
Tests for SQLiteClient using the VectorDatabaseContract.
"""

import pytest
import os
import tempfile
from pathlib import Path
from src.database.sqlite_client import SQLiteClient
from tests.contract_vector_db import VectorDatabaseContract

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
