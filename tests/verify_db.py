#!/usr/bin/env python3
"""Verify that the database ingestion works correctly"""
import sys
from pathlib import Path
import asyncio

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlite_utils import Database
from magento_graphql_docs_mcp.config import DB_PATH, DOCS_PATH
from magento_graphql_docs_mcp.ingest import ingest_graphql_docs


async def main():
    print("=" * 70)
    print("Magento GraphQL Docs Database Verification")
    print("=" * 70)
    print()

    print(f"Database path: {DB_PATH}")
    print(f"Documentation path: {DOCS_PATH}")
    print()

    # Run ingestion
    print("Running ingestion...")
    try:
        await ingest_graphql_docs()
    except Exception as e:
        print(f"❌ Ingestion failed: {e}")
        import traceback
        traceback.print_exc()
        return 1

    print("✓ Ingestion complete")
    print()

    # Open database
    db = Database(DB_PATH)

    # Check tables
    print("Database Tables:")
    for table_name in db.table_names():
        count = db[table_name].count
        print(f"  - {table_name}: {count} rows")
    print()

    # Test FTS search on documents
    print("Testing FTS search on documents...")
    test_queries = ["product", "cart", "customer", "checkout"]
    for query in test_queries:
        results = list(db["documents"].search(query, limit=3))
        print(f"  Query: '{query}' -> {len(results)} results")
        for r in results[:2]:
            print(f"    - {r['title']} ({r['category']})")
    print()

    # Test FTS search on GraphQL elements
    print("Testing FTS search on GraphQL elements...")
    test_queries = ["products", "cart", "customer"]
    for query in test_queries:
        results = list(db["graphql_elements"].search(query, limit=3))
        print(f"  Query: '{query}' -> {len(results)} results")
        for r in results[:2]:
            print(f"    - {r['element_type']} {r['name']}")
    print()

    # Check specific document
    print("Testing specific document lookup...")
    docs = list(db.query("SELECT * FROM documents LIMIT 1"))
    if docs:
        doc = docs[0]
        print(f"  ✓ Found: {doc['title']}")
        print(f"    Category: {doc['category']}/{doc['subcategory']}")
        print(f"    Type: {doc['content_type']}")
    else:
        print(f"  ❌ No documents found")
    print()

    # Check code blocks
    print("Testing code blocks...")
    code_blocks = list(db.query("SELECT language, COUNT(*) as count FROM code_blocks GROUP BY language ORDER BY count DESC LIMIT 5"))
    print(f"  Top languages:")
    for row in code_blocks:
        print(f"    - {row['language']}: {row['count']} blocks")
    print()

    print("=" * 70)
    print("✓ Database verification complete!")
    print("=" * 70)
    return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
