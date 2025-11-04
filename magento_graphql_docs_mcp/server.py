from fastmcp import FastMCP
from contextlib import asynccontextmanager
from .ingest import ingest_graphql_docs
from sqlite_utils import Database
from pydantic import Field
from typing import List, Optional
from .config import DB_PATH, DB_TOP_K, MAX_CODE_PREVIEW_LENGTH, SEARCH_RESULT_MULTIPLIER
from typing import Annotated
import json
import logging
import sys

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def server_lifespan(server: FastMCP):
    """Lifespan context manager for the FastMCP server."""
    try:
        await ingest_graphql_docs()
    except FileNotFoundError as e:
        logger.error(f"Failed to load documentation: {e}")
        logger.error("See SETUP.md for configuration help")
        logger.error("The server cannot start without access to the GraphQL documentation files")
        # Print to stderr as well for visibility
        print(f"\nERROR: {e}", file=sys.stderr)
        raise
    except Exception as e:
        logger.error(f"Unexpected error during ingestion: {e}")
        raise
    yield


# Initialize FastMCP server with lifespan
mcp = FastMCP("Magento GraphQL Docs", lifespan=server_lifespan)


@mcp.tool(
    name="search_documentation",
    description="""Search Magento 2 GraphQL documentation by keywords.
Use SHORT keyword queries (1-3 words) to find documentation pages.
Can filter by category, subcategory, or content type."""
)
def search_documentation(
    queries: Annotated[
        List[str],
        Field(description="List of 1-3 short keyword queries. Examples: ['product', 'cart'], ['checkout']")
    ],
    category: Annotated[
        Optional[str],
        Field(description="Filter by category: schema, develop, usage, tutorials, payment-methods")
    ] = None,
    subcategory: Annotated[
        Optional[str],
        Field(description="Filter by subcategory: products, cart, customer, checkout, etc.")
    ] = None,
    content_type: Annotated[
        Optional[str],
        Field(description="Filter by content type: guide, reference, tutorial, schema")
    ] = None
) -> str:
    """Search documentation with filters"""
    db = Database(DB_PATH)

    # Combine queries with OR
    combined_query = " OR ".join(f"({q})" for q in queries)

    # Perform FTS search (fetch more results than needed to allow for filtering)
    results = list(db["documents"].search(combined_query, limit=DB_TOP_K * SEARCH_RESULT_MULTIPLIER))

    # Apply filters
    if category:
        results = [r for r in results if r['category'] == category]

    if subcategory:
        results = [r for r in results if r.get('subcategory') == subcategory]

    if content_type:
        results = [r for r in results if r.get('content_type') == content_type]

    # Limit after filtering
    results = results[:DB_TOP_K]

    if not results:
        return "No matching documentation found."

    # Format results
    formatted_results = []
    for doc in results:
        excerpt = doc.get('description') or doc.get('content_md', '')[:200]

        formatted_results.append(
            f"### {doc['title']}\n"
            f"**Path:** {doc['file_path']}\n"
            f"**Category:** {doc['category']}/{doc.get('subcategory', 'N/A')}\n"
            f"**Type:** {doc.get('content_type', 'N/A')}\n"
            f"**Description:** {excerpt}...\n"
        )

    return "\n---\n\n".join(formatted_results)


@mcp.tool(
    name="get_document",
    description="Retrieve complete documentation page by file path"
)
def get_document(
    file_path: Annotated[str, Field(description="File path relative to docs root, e.g., 'schema/products/queries/products.md'")]
) -> str:
    """Get full document content"""
    db = Database(DB_PATH)

    try:
        # Query by file_path
        doc = dict(db.query(
            "SELECT * FROM documents WHERE file_path = ?",
            [file_path]
        ).__next__())
    except StopIteration:
        return f"Document not found: {file_path}\n\nTip: Use search_documentation to find the correct file path."

    # Parse keywords
    keywords = json.loads(doc.get('keywords_json', '[]'))
    keywords_str = ', '.join(keywords) if keywords else 'None'

    # Format document
    lines = [
        f"# {doc['title']}",
        "",
        f"**Path:** {doc['file_path']}",
        f"**Category:** {doc['category']}/{doc.get('subcategory', 'N/A')}",
        f"**Type:** {doc.get('content_type', 'N/A')}",
        f"**Keywords:** {keywords_str}",
        "",
    ]

    if doc.get('description'):
        lines.append(f"**Description:** {doc['description']}")
        lines.append("")

    lines.append("---")
    lines.append("")
    lines.append(doc['content_md'])

    return "\n".join(lines)


@mcp.tool(
    name="search_graphql_elements",
    description="Search for GraphQL queries, mutations, types, or interfaces"
)
def search_graphql_elements(
    query: Annotated[str, Field(description="Search term, e.g., 'products', 'cart', 'customer'")],
    element_type: Annotated[
        Optional[str],
        Field(description="Filter by element type: query, mutation, type, interface, union")
    ] = None
) -> str:
    """Search GraphQL schema elements"""
    db = Database(DB_PATH)

    # FTS search
    results = list(db["graphql_elements"].search(query, limit=10))

    # Apply filter
    if element_type:
        results = [r for r in results if r['element_type'] == element_type]

    if not results:
        return f"No GraphQL elements found matching: {query}"

    # Format results
    formatted_results = []
    for elem in results:
        # Get source document
        try:
            doc = dict(db.query(
                "SELECT title, file_path FROM documents WHERE id = ?",
                [elem['document_id']]
            ).__next__())
            source = f"{doc['title']} ({doc['file_path']})"
        except StopIteration:
            source = "Unknown"

        fields = json.loads(elem.get('fields_json', '[]'))
        params = json.loads(elem.get('parameters_json', '[]'))

        formatted_results.append(
            f"### `{elem['element_type']}` **{elem['name']}**\n"
            f"**Source:** {source}\n"
            f"**Fields:** {', '.join(fields[:10]) if fields else 'None'}\n"
            f"**Parameters:** {', '.join(params) if params else 'None'}\n"
        )

    return "\n---\n\n".join(formatted_results)


@mcp.tool(
    name="get_element_details",
    description="Get complete details about a specific GraphQL element"
)
def get_element_details(
    element_name: Annotated[str, Field(description="Element name, e.g., 'products', 'createCustomer', 'ProductInterface'")],
    element_type: Annotated[Optional[str], Field(description="Optional type filter: query, mutation, type, interface")] = None
) -> str:
    """Get element details with source document"""
    db = Database(DB_PATH)

    # Build query
    if element_type:
        sql = "SELECT * FROM graphql_elements WHERE name = ? AND element_type = ?"
        params = [element_name, element_type]
    else:
        sql = "SELECT * FROM graphql_elements WHERE name = ?"
        params = [element_name]

    elements = list(db.query(sql, params))

    if not elements:
        return f"GraphQL element not found: {element_name}\n\nTip: Use search_graphql_elements to find similar elements."

    # Format each element
    formatted = []
    for elem in elements:
        # Get source document
        try:
            doc = dict(db.query(
                "SELECT * FROM documents WHERE id = ?",
                [elem['document_id']]
            ).__next__())
        except StopIteration:
            doc = None

        fields = json.loads(elem.get('fields_json', '[]'))
        params = json.loads(elem.get('parameters_json', '[]'))

        lines = [
            f"# `{elem['element_type']}` **{elem['name']}**",
            ""
        ]

        if params:
            lines.append(f"**Parameters:** {', '.join(params)}")
            lines.append("")

        if fields:
            lines.append(f"**Fields:** {', '.join(fields)}")
            lines.append("")

        if elem.get('description'):
            lines.append(f"**Description:** {elem['description']}")
            lines.append("")

        if doc:
            lines.append(f"**Source Document:** {doc['title']}")
            lines.append(f"**Path:** {doc['file_path']}")
            lines.append("")

            # Get code blocks from same document
            code_blocks = list(db.query(
                "SELECT * FROM code_blocks WHERE document_id = ? AND language = 'graphql' LIMIT 3",
                [elem['document_id']]
            ))

            if code_blocks:
                lines.append("**Example Code:**")
                lines.append("")
                for block in code_blocks:
                    lines.append("```graphql")
                    # Limit code length for readability
                    code_preview = block['code'][:MAX_CODE_PREVIEW_LENGTH + 100]
                    lines.append(code_preview)
                    lines.append("```")
                    lines.append("")

        formatted.append("\n".join(lines))

    return "\n---\n\n".join(formatted)


@mcp.tool(
    name="list_categories",
    description="List all documentation categories with document counts"
)
def list_categories() -> str:
    """List category hierarchy"""
    db = Database(DB_PATH)

    # Get category counts
    categories = db.query(
        "SELECT category, subcategory, COUNT(*) as count FROM documents GROUP BY category, subcategory ORDER BY category, subcategory"
    )

    # Build hierarchy
    cat_tree = {}
    for row in categories:
        cat = row['category']
        subcat = row['subcategory'] or 'N/A'
        count = row['count']

        if cat not in cat_tree:
            cat_tree[cat] = {}

        cat_tree[cat][subcat] = count

    # Format output
    lines = ["# Magento 2 GraphQL Documentation Categories\n"]

    for cat in sorted(cat_tree.keys()):
        # Calculate total for category
        total = sum(cat_tree[cat].values())
        lines.append(f"## {cat} ({total} documents)")
        lines.append("")

        for subcat in sorted(cat_tree[cat].keys()):
            count = cat_tree[cat][subcat]
            lines.append(f"  - `{subcat}`: {count} documents")

        lines.append("")

    return "\n".join(lines)


@mcp.tool(
    name="get_tutorial",
    description="Get complete tutorial with all steps in order"
)
def get_tutorial(
    tutorial_name: Annotated[str, Field(description="Tutorial name, e.g., 'checkout'")]
) -> str:
    """Get sequential tutorial steps"""
    db = Database(DB_PATH)

    # Search for tutorial documents
    docs = list(db.query(
        "SELECT * FROM documents WHERE category = 'tutorials' AND (subcategory = ? OR file_path LIKE ?) ORDER BY file_path",
        [tutorial_name, f"tutorials/{tutorial_name}%"]
    ))

    if not docs:
        return f"Tutorial not found: {tutorial_name}\n\nAvailable tutorials: Use list_categories() to see all tutorials."

    # Format tutorial
    lines = [f"# {tutorial_name.title()} Tutorial", ""]

    for i, doc in enumerate(docs, 1):
        lines.append(f"## Step {i}: {doc['title']}")
        lines.append("")
        lines.append(f"**File:** {doc['file_path']}")
        lines.append("")

        if doc.get('description'):
            lines.append(doc['description'])
            lines.append("")

        # Get code examples
        code_blocks = list(db.query(
            "SELECT * FROM code_blocks WHERE document_id = ? AND language IN ('graphql', 'json') LIMIT 2",
            [doc['id']]
        ))

        if code_blocks:
            for block in code_blocks:
                lines.append(f"```{block['language']}")
                lines.append(block['code'])
                lines.append("```")
                lines.append("")

        lines.append("---")
        lines.append("")

    return "\n".join(lines)


@mcp.tool(
    name="search_examples",
    description="Search for code examples by topic and language"
)
def search_examples(
    query: Annotated[str, Field(description="Search term for code examples")],
    language: Annotated[
        Optional[str],
        Field(description="Filter by language: graphql, json, javascript, php, bash")
    ] = None
) -> str:
    """Search code blocks"""
    db = Database(DB_PATH)

    # Search in code and context
    sql = """
        SELECT cb.*, d.title, d.file_path
        FROM code_blocks cb
        JOIN documents d ON cb.document_id = d.id
        WHERE (cb.code LIKE ? OR cb.context LIKE ?)
    """
    params = [f"%{query}%", f"%{query}%"]

    if language:
        sql += " AND cb.language = ?"
        params.append(language)

    sql += " LIMIT 10"

    results = list(db.query(sql, params))

    if not results:
        return f"No code examples found matching: {query}"

    # Format results
    formatted = []
    for block in results:
        context_str = f"**Context:** {block['context']}\n" if block.get('context') else ""

        formatted.append(
            f"### {block['title']}\n"
            f"**File:** {block['file_path']}\n"
            f"**Language:** {block['language']}\n"
            f"{context_str}"
            f"\n```{block['language']}\n"
            f"{block['code'][:MAX_CODE_PREVIEW_LENGTH]}\n"  # Limit code length for readability
            f"```\n"
        )

    return "\n---\n\n".join(formatted)


@mcp.tool(
    name="get_related_documents",
    description="Find documents related to the specified document"
)
def get_related_documents(
    file_path: Annotated[str, Field(description="File path of source document")]
) -> str:
    """Find related docs"""
    db = Database(DB_PATH)

    # Get source document
    try:
        source_doc = dict(db.query(
            "SELECT * FROM documents WHERE file_path = ?",
            [file_path]
        ).__next__())
    except StopIteration:
        return f"Document not found: {file_path}"

    # Find related documents
    # 1. Same category and subcategory
    related_by_category = list(db.query(
        "SELECT * FROM documents WHERE category = ? AND subcategory = ? AND file_path != ? LIMIT 5",
        [source_doc['category'], source_doc['subcategory'], file_path]
    ))

    # 2. Similar keywords
    source_keywords = set(json.loads(source_doc.get('keywords_json', '[]')))
    related_by_keywords = []

    if source_keywords:
        for keyword in list(source_keywords)[:3]:
            matches = list(db.query(
                "SELECT * FROM documents WHERE keywords_json LIKE ? AND file_path != ? LIMIT 3",
                [f"%{keyword}%", file_path]
            ))
            related_by_keywords.extend(matches)

    # Combine and deduplicate
    seen = set()
    all_related = []

    for doc in related_by_category + related_by_keywords:
        if doc['file_path'] not in seen:
            seen.add(doc['file_path'])
            all_related.append(doc)

    all_related = all_related[:5]

    if not all_related:
        return f"No related documents found for: {file_path}"

    # Format results
    lines = [f"# Related Documents for: {source_doc['title']}", ""]

    for doc in all_related:
        relationship = "Same category" if doc['category'] == source_doc['category'] else "Similar content"

        lines.append(f"### {doc['title']}")
        lines.append(f"**Path:** {doc['file_path']}")
        lines.append(f"**Relationship:** {relationship}")
        lines.append(f"**Category:** {doc['category']}/{doc.get('subcategory', 'N/A')}")

        if doc.get('description'):
            lines.append(f"**Description:** {doc['description'][:150]}...")

        lines.append("")

    return "\n".join(lines)


def main():
    mcp.run()


if __name__ == "__main__":
    main()
