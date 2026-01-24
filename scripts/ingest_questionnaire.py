#!/usr/bin/env python3
"""
Ingest a markdown questionnaire into the database.
"""

import argparse
import sys
import os
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.database.sqlite_client import SQLiteClient
from src.domain.questionnaire_store import QuestionnaireStore
from src.config import SQLITE_DB_PATH

def main():
    parser = argparse.ArgumentParser(description="Ingest a markdown questionnaire.")
    parser.add_argument("file", type=str, help="Path to the markdown questionnaire file")
    args = parser.parse_args()

    path = Path(args.file)
    if not path.exists():
        print(f"Error: File '{path}' not found.")
        sys.exit(1)

    db_client = SQLiteClient(str(SQLITE_DB_PATH))
    store = QuestionnaireStore(db_client)

    print(f"Ingesting questionnaire from {path}...")
    try:
        questionnaire, questions = store.import_from_markdown(path)
        print(f"✅ Successfully ingested questionnaire: {questionnaire.name}")
        print(f"   ID: {questionnaire.id}")
        print(f"   Questions: {len(questions)}")
    except Exception as e:
        print(f"❌ Error during ingestion: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
