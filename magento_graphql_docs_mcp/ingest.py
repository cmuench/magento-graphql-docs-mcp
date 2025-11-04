import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from sqlite_utils import Database
from .parser import MarkdownDocParser
from .config import DB_PATH, DOCS_PATH

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def should_reingest(db: Database, docs_path: str) -> bool:
    """
    Determine if we need to reingest based on directory modification time.
    """
    docs_dir = Path(docs_path)

    if not docs_dir.exists():
        logger.error(f"Documentation directory not found: {docs_path}")
        return False

    # Get directory modification time (recursively check all files)
    latest_mtime = max(
        (f.stat().st_mtime for f in docs_dir.rglob("*.md")),
        default=0
    )
    latest_mtime_iso = datetime.fromtimestamp(latest_mtime, tz=timezone.utc).isoformat()

    # Check if metadata table exists
    if "metadata" not in db.table_names():
        logger.info("No metadata table found, will ingest")
        return True

    # Check last ingestion time
    try:
        metadata = db["metadata"].get("last_ingestion")
        last_docs_mtime = metadata.get("docs_directory_mtime")

        if last_docs_mtime == latest_mtime_iso:
            logger.info("Documentation unchanged, skipping ingestion")
            return False

        logger.info(f"Documentation modified, will reingest")
        return True
    except Exception:
        # No metadata found, ingest
        return True


def create_tables(db: Database) -> None:
    """Create database schema"""
    logger.info("Creating database tables...")

    # Metadata table
    if "metadata" not in db.table_names():
        db["metadata"].create({
            "key": str,
            "docs_directory_mtime": str,
            "total_files": int,
            "ingestion_time": str,
        }, pk="key")

    # Documents table
    if "documents" not in db.table_names():
        db["documents"].create({
            "id": str,
            "file_path": str,
            "title": str,
            "description": str,
            "keywords_json": str,
            "category": str,
            "subcategory": str,
            "content_type": str,
            "searchable_text": str,
            "headers_json": str,
            "last_modified": str,
            "content_md": str,
        }, pk="id")
        db["documents"].create_index(["category"])
        db["documents"].create_index(["subcategory"])
        db["documents"].create_index(["content_type"])

    # Code blocks table
    if "code_blocks" not in db.table_names():
        db["code_blocks"].create({
            "id": int,
            "document_id": str,
            "language": str,
            "code": str,
            "context": str,
            "line_number": int,
        }, pk="id")
        db["code_blocks"].create_index(["document_id"])
        db["code_blocks"].create_index(["language"])

    # GraphQL elements table
    if "graphql_elements" not in db.table_names():
        db["graphql_elements"].create({
            "id": int,
            "document_id": str,
            "element_type": str,
            "name": str,
            "fields_json": str,
            "parameters_json": str,
            "return_type": str,
            "description": str,
            "searchable_text": str,
        }, pk="id")
        db["graphql_elements"].create_index(["document_id"])
        db["graphql_elements"].create_index(["element_type"])
        db["graphql_elements"].create_index(["name"])

    # Create FTS5 indexes
    if "documents_fts" not in db.table_names():
        db["documents"].enable_fts(
            ["searchable_text"],
            create_triggers=True,
            tokenize="trigram"
        )
        logger.info("Created FTS index for documents")

    if "graphql_elements_fts" not in db.table_names():
        db["graphql_elements"].enable_fts(
            ["searchable_text"],
            create_triggers=True,
            tokenize="trigram"
        )
        logger.info("Created FTS index for graphql_elements")


def ingest_data(db: Database, parser: MarkdownDocParser) -> None:
    """Ingest parsed data into database"""
    logger.info("Parsing all documentation files...")

    # Parse all files
    documents, code_blocks, graphql_elements = parser.parse_all()

    # Clear existing data
    logger.info("Clearing existing data...")
    db["code_blocks"].delete_where()
    db["graphql_elements"].delete_where()
    db["documents"].delete_where()

    # Insert documents
    logger.info(f"Inserting {len(documents)} documents...")
    doc_records = []
    for doc in documents:
        doc_records.append({
            "id": doc.id,
            "file_path": doc.file_path,
            "title": doc.title,
            "description": doc.description,  # Allow NULL for missing descriptions
            "keywords_json": json.dumps(doc.keywords),
            "category": doc.category,
            "subcategory": doc.subcategory,  # Allow NULL for missing subcategories
            "content_type": doc.content_type,
            "searchable_text": doc.searchable_text,
            "headers_json": json.dumps(doc.headers),
            "last_modified": doc.last_modified.isoformat(),
            "content_md": doc.content_md,
        })

    if doc_records:
        db["documents"].insert_all(doc_records)
        logger.info(f"Inserted {len(doc_records)} documents")

    # Insert code blocks
    logger.info(f"Inserting {len(code_blocks)} code blocks...")
    code_block_records = []
    for block in code_blocks:
        code_block_records.append({
            "document_id": block.document_id,
            "language": block.language,
            "code": block.code,
            "context": block.context,  # Allow NULL for missing context
            "line_number": block.line_number,
        })

    if code_block_records:
        db["code_blocks"].insert_all(code_block_records)
        logger.info(f"Inserted {len(code_block_records)} code blocks")

    # Insert GraphQL elements
    logger.info(f"Inserting {len(graphql_elements)} GraphQL elements...")
    element_records = []
    for element in graphql_elements:
        element_records.append({
            "document_id": element.document_id,
            "element_type": element.element_type,
            "name": element.name,
            "fields_json": json.dumps(element.fields),
            "parameters_json": json.dumps(element.parameters),
            "return_type": element.return_type,  # Allow NULL for missing return type
            "description": element.description,  # Allow NULL for missing description
            "searchable_text": element.searchable_text,
        })

    if element_records:
        db["graphql_elements"].insert_all(element_records)
        logger.info(f"Inserted {len(element_records)} GraphQL elements")


def update_metadata(db: Database, docs_path: str, total_files: int) -> None:
    """Update metadata after successful ingestion"""
    docs_dir = Path(docs_path)

    # Get latest modification time
    latest_mtime = max(
        (f.stat().st_mtime for f in docs_dir.rglob("*.md")),
        default=0
    )
    latest_mtime_iso = datetime.fromtimestamp(latest_mtime, tz=timezone.utc).isoformat()

    db["metadata"].upsert({
        "key": "last_ingestion",
        "docs_directory_mtime": latest_mtime_iso,
        "total_files": total_files,
        "ingestion_time": datetime.now(timezone.utc).isoformat(),
    }, pk="key")


async def ingest_graphql_docs() -> None:
    """Main ingestion function to be called on server startup"""
    logger.info("Starting GraphQL documentation ingestion...")

    db = Database(DB_PATH)

    # Check if we need to reingest
    if not should_reingest(db, DOCS_PATH):
        logger.info("Skipping ingestion, data is up to date")
        return

    # Create tables
    create_tables(db)

    # Parse documentation
    parser = MarkdownDocParser(DOCS_PATH)

    try:
        # Get file count before parsing
        files = parser.walk_directory()
        total_files = len(files)

        # Ingest data
        ingest_data(db, parser)

        # Update metadata
        update_metadata(db, DOCS_PATH, total_files)

        logger.info("GraphQL documentation ingestion complete")
    except FileNotFoundError as e:
        logger.error(f"Cannot ingest: {e}")
        return
    except Exception as e:
        logger.error(f"Error during ingestion: {e}")
        raise


if __name__ == "__main__":
    import asyncio
    asyncio.run(ingest_graphql_docs())
