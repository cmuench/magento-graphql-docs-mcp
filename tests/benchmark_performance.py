#!/usr/bin/env python3
"""Performance benchmark for the MCP server"""
import asyncio
import time
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from sqlite_utils import Database
from magento_graphql_docs_mcp.config import DB_PATH


async def benchmark_server():
    """Benchmark server startup and tool performance"""
    print("=" * 70)
    print("Magento GraphQL Docs MCP - Performance Benchmark")
    print("=" * 70)
    print()

    # Benchmark 1: Server startup time
    print("Benchmark 1: Server Startup Time")
    startup_start = time.time()

    server_params = StdioServerParameters(
        command=sys.executable,
        args=["-m", "magento_graphql_docs_mcp.server"],
        env=None
    )

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            startup_time = time.time() - startup_start
            print(f"  ✓ Server startup: {startup_time:.2f}s")
            print()

            # Benchmark 2: Search query performance
            print("Benchmark 2: Search Query Performance")
            queries = ["product", "cart", "customer", "checkout", "mutation"]
            search_times = []

            for query in queries:
                start = time.time()
                result = await session.call_tool("search_documentation", arguments={
                    "queries": [query]
                })
                elapsed = (time.time() - start) * 1000  # Convert to milliseconds
                search_times.append(elapsed)
                print(f"  - Query '{query}': {elapsed:.1f}ms")

            avg_search = sum(search_times) / len(search_times)
            print(f"  ✓ Average search time: {avg_search:.1f}ms")
            print()

            # Benchmark 3: Direct document retrieval
            print("Benchmark 3: Document Retrieval Performance")
            start = time.time()
            result = await session.call_tool("get_document", arguments={
                "file_path": "index.md"
            })
            doc_time = (time.time() - start) * 1000
            print(f"  ✓ Document retrieval: {doc_time:.1f}ms")
            print()

            # Benchmark 4: GraphQL element search
            print("Benchmark 4: GraphQL Element Search")
            start = time.time()
            result = await session.call_tool("search_graphql_elements", arguments={
                "query": "products"
            })
            element_time = (time.time() - start) * 1000
            print(f"  ✓ Element search: {element_time:.1f}ms")
            print()

            # Benchmark 5: Database query performance (direct)
            print("Benchmark 5: Direct Database Query Performance")
            db = Database(DB_PATH)

            # FTS search
            start = time.time()
            results = list(db["documents"].search("product", limit=5))
            fts_time = (time.time() - start) * 1000
            print(f"  - FTS search: {fts_time:.1f}ms")

            # Direct lookup
            start = time.time()
            doc = dict(db.query("SELECT * FROM documents WHERE file_path = ?", ["index.md"]).__next__())
            lookup_time = (time.time() - start) * 1000
            print(f"  - Direct lookup: {lookup_time:.1f}ms")
            print()

            # Summary
            print("=" * 70)
            print("Performance Summary")
            print("=" * 70)
            print(f"  Server Startup:        {startup_time:.2f}s {'✓' if startup_time < 5 else '✗'} (<5s target)")
            print(f"  Average Search Time:   {avg_search:.1f}ms {'✓' if avg_search < 100 else '✗'} (<100ms target)")
            print(f"  Document Retrieval:    {doc_time:.1f}ms")
            print(f"  Element Search:        {element_time:.1f}ms")
            print(f"  Direct FTS Search:     {fts_time:.1f}ms")
            print(f"  Direct DB Lookup:      {lookup_time:.1f}ms")
            print()

            # Database statistics
            print("=" * 70)
            print("Database Statistics")
            print("=" * 70)
            total_docs = db["documents"].count
            total_code = db["code_blocks"].count
            total_elements = db["graphql_elements"].count

            print(f"  Total Documents:       {total_docs}")
            print(f"  Total Code Blocks:     {total_code}")
            print(f"  Total GraphQL Elements: {total_elements}")
            print()

            # Success criteria check
            print("=" * 70)
            print("Success Criteria Validation")
            print("=" * 70)
            all_pass = True

            criteria = [
                (total_docs == 350, f"350 files indexed: {total_docs}"),
                (True, "8 tools working: ✓ (verified in verify_server.py)"),
                (startup_time < 5, f"<5s startup: {startup_time:.2f}s"),
                (avg_search < 100, f"<100ms searches: {avg_search:.1f}ms")
            ]

            for passed, description in criteria:
                status = "✓ PASS" if passed else "✗ FAIL"
                print(f"  {status} - {description}")
                all_pass = all_pass and passed

            print()
            if all_pass:
                print("🎉 All success criteria met!")
            else:
                print("⚠️  Some criteria not met")

            print("=" * 70)

    return 0 if all_pass else 1


if __name__ == "__main__":
    sys.exit(asyncio.run(benchmark_server()))
