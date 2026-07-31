"""
Check what collections exist in ChromaDB
"""

import chromadb
from pathlib import Path

VECTOR_INDEX_DIR = Path("data/vector_index")

client = chromadb.PersistentClient(path=str(VECTOR_INDEX_DIR))

# List all collections
collections = client.list_collections()

print("Collections in ChromaDB:")
print("="*60)
for collection in collections:
    print(f"Name: {collection.name}")
    print(f"ID: {collection.id}")
    print(f"Count: {collection.count()}")
    print("-"*60)

if not collections:
    print("No collections found. Need to run corpus pipeline.")
