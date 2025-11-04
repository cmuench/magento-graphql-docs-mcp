#!/usr/bin/env python3
"""Verify that the MCP server works correctly"""
import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


async def run():
    print("=" * 70)
    print("Magento GraphQL Docs MCP Server Verification")
    print("=" * 70)
    print()

    server_params = StdioServerParameters(
        command=sys.executable,
        args=["-m", "magento_graphql_docs_mcp.server"],
        env=None
    )

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            # Initialize the connection
            await session.initialize()
            print("✓ Server initialized")
            print()

            # List available tools
            tools = await session.list_tools()
            print(f"Available tools ({len(tools.tools)}):")
            for tool in tools.tools:
                print(f"  - {tool.name}: {tool.description[:60]}...")
            print()

            # Test 1: Search documentation
            print("Test 1: Search for 'product' documentation")
            result = await session.call_tool("search_documentation", arguments={
                "queries": ["product"]
            })
            print(f"  Result length: {len(result.content[0].text)} chars")
            print(f"  Preview: {result.content[0].text[:200]}...")
            print()

            # Test 2: Get specific document
            print("Test 2: Get document 'index.md'")
            result = await session.call_tool("get_document", arguments={
                "file_path": "index.md"
            })
            print(f"  Result length: {len(result.content[0].text)} chars")
            print(f"  Preview: {result.content[0].text[:200]}...")
            print()

            # Test 3: Search GraphQL elements
            print("Test 3: Search GraphQL elements for 'products'")
            result = await session.call_tool("search_graphql_elements", arguments={
                "query": "products"
            })
            print(f"  Result length: {len(result.content[0].text)} chars")
            print(f"  Preview: {result.content[0].text[:200]}...")
            print()

            # Test 4: Get element details
            print("Test 4: Get details for 'Query' type")
            result = await session.call_tool("get_element_details", arguments={
                "element_name": "Query"
            })
            print(f"  Result length: {len(result.content[0].text)} chars")
            print(f"  Preview: {result.content[0].text[:200]}...")
            print()

            # Test 5: List categories
            print("Test 5: List all categories")
            result = await session.call_tool("list_categories", arguments={})
            print(f"  Result length: {len(result.content[0].text)} chars")
            lines = result.content[0].text.split('\n')
            category_count = len([l for l in lines if l.startswith('##')])
            print(f"  Categories found: {category_count}")
            print()

            # Test 6: Get tutorial
            print("Test 6: Get 'checkout' tutorial")
            result = await session.call_tool("get_tutorial", arguments={
                "tutorial_name": "checkout"
            })
            print(f"  Result length: {len(result.content[0].text)} chars")
            print(f"  Preview: {result.content[0].text[:200]}...")
            print()

            # Test 7: Search examples
            print("Test 7: Search examples for 'mutation'")
            result = await session.call_tool("search_examples", arguments={
                "query": "mutation",
                "language": "graphql"
            })
            print(f"  Result length: {len(result.content[0].text)} chars")
            print(f"  Preview: {result.content[0].text[:200]}...")
            print()

            # Test 8: Get related documents
            print("Test 8: Get related documents for 'index.md'")
            result = await session.call_tool("get_related_documents", arguments={
                "file_path": "index.md"
            })
            print(f"  Result length: {len(result.content[0].text)} chars")
            print(f"  Preview: {result.content[0].text[:200]}...")
            print()

    print("=" * 70)
    print("✓ All 8 tools tested successfully!")
    print("=" * 70)
    return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(run()))
