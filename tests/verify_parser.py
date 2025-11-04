#!/usr/bin/env python3
"""Verify that the markdown parser works correctly"""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from magento_graphql_docs_mcp.parser import MarkdownDocParser
from magento_graphql_docs_mcp.config import DOCS_PATH


def main():
    print("=" * 70)
    print("Magento GraphQL Docs Parser Verification")
    print("=" * 70)
    print()

    print(f"Documentation path: {DOCS_PATH}")
    print()

    # Check if docs exist
    docs_path = Path(DOCS_PATH)
    if not docs_path.exists():
        print(f"❌ Documentation directory not found: {DOCS_PATH}")
        print()
        print("Please set MAGENTO_GRAPHQL_DOCS_PATH environment variable")
        print("or ensure commerce-webapi/src/pages/graphql/ exists")
        return 1

    # Create parser
    parser = MarkdownDocParser(DOCS_PATH)

    # Test directory walking
    print("Finding markdown files...")
    files = parser.walk_directory()
    print(f"✓ Found {len(files)} markdown files")
    print()

    # Parse all documents
    print("Parsing all documents...")
    try:
        documents, code_blocks, graphql_elements = parser.parse_all()
    except Exception as e:
        print(f"❌ Failed to parse: {e}")
        return 1

    print(f"✓ Successfully parsed all documents")
    print()

    # Stats
    print("Statistics:")
    print(f"  - Total documents: {len(documents)}")
    print(f"  - Total code blocks: {len(code_blocks)}")
    print(f"  - Total GraphQL elements: {len(graphql_elements)}")
    print()

    # Category breakdown
    print("Documents by category:")
    categories = {}
    for doc in documents:
        key = doc.category
        categories[key] = categories.get(key, 0) + 1

    for cat, count in sorted(categories.items()):
        print(f"  - {cat}: {count} documents")
    print()

    # Show some example documents
    print("Sample Documents:")
    for i, doc in enumerate(documents[:5]):
        print(f"  {i+1}. {doc.title}")
        print(f"     Path: {doc.file_path}")
        print(f"     Category: {doc.category}/{doc.subcategory or 'N/A'}")
        print(f"     Type: {doc.content_type}")
        print(f"     Keywords: {', '.join(doc.keywords[:3]) if doc.keywords else 'None'}")
        print()

    # Show some example code blocks
    if code_blocks:
        print("Sample Code Blocks:")
        languages = {}
        for block in code_blocks:
            languages[block.language] = languages.get(block.language, 0) + 1

        for lang, count in sorted(languages.items(), key=lambda x: x[1], reverse=True)[:5]:
            print(f"  - {lang}: {count} blocks")
        print()

    # Show some example GraphQL elements
    if graphql_elements:
        print("Sample GraphQL Elements:")
        element_types = {}
        for elem in graphql_elements:
            element_types[elem.element_type] = element_types.get(elem.element_type, 0) + 1

        for elem_type, count in sorted(element_types.items()):
            print(f"  - {elem_type}: {count} elements")

        print()
        print("Example elements:")
        for i, elem in enumerate(graphql_elements[:5]):
            print(f"  {i+1}. {elem.element_type} {elem.name}")
            if elem.fields:
                print(f"     Fields: {', '.join(elem.fields[:5])}")
        print()

    print("=" * 70)
    print("✓ Parser verification complete!")
    print("=" * 70)
    return 0


if __name__ == "__main__":
    sys.exit(main())
