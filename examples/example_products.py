#!/usr/bin/env python3
"""
Example: Working with Product Queries in Magento GraphQL

This script demonstrates:
1. Searching for product documentation
2. Finding GraphQL product queries and types
3. Getting detailed element information
4. Searching for product code examples
"""
import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


def print_section(title):
    """Print a formatted section header"""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70 + "\n")


async def main():
    """Run product query examples"""
    print_section("Magento GraphQL - Product Query Examples")

    server_params = StdioServerParameters(
        command=sys.executable,
        args=["-m", "magento_graphql_docs_mcp.server"],
        env=None
    )

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            print("✓ Connected to MCP server\n")

            # Example 1: Search for product documentation
            print_section("Example 1: Search for Product Documentation")
            result = await session.call_tool("search_documentation", arguments={
                "queries": ["product"],
                "category": "schema"
            })
            print(result.content[0].text[:800])
            print("\n... (truncated for readability)")

            # Example 2: Find product GraphQL queries
            print_section("Example 2: Find Product GraphQL Queries")
            result = await session.call_tool("search_graphql_elements", arguments={
                "query": "products",
                "element_type": "query"
            })
            print(result.content[0].text)

            # Example 3: Get detailed information about products query
            print_section("Example 3: Get 'products' Query Details")
            result = await session.call_tool("get_element_details", arguments={
                "element_name": "products"
            })
            print(result.content[0].text[:1000])
            print("\n... (truncated for readability)")

            # Example 4: Search for product query code examples
            print_section("Example 4: Search for Product Query Examples")
            result = await session.call_tool("search_examples", arguments={
                "query": "products",
                "language": "graphql"
            })
            print(result.content[0].text[:1200])
            print("\n... (truncated for readability)")

            # Example 5: Get ProductInterface details
            print_section("Example 5: Get ProductInterface Type Details")
            result = await session.call_tool("get_element_details", arguments={
                "element_name": "ProductInterface",
                "element_type": "interface"
            })
            print(result.content[0].text[:800])
            print("\n... (truncated for readability)")

            # Example 6: Find related product documentation
            print_section("Example 6: Browse Product Documentation Categories")
            result = await session.call_tool("list_categories", arguments={})
            lines = result.content[0].text.split('\n')
            # Find and show products category
            in_products = False
            for line in lines:
                if 'products' in line.lower():
                    in_products = True
                if in_products:
                    print(line)
                    if line == "":
                        break

            print_section("Summary")
            print("✓ Searched product documentation")
            print("✓ Found product GraphQL queries")
            print("✓ Retrieved detailed query information")
            print("✓ Located product code examples")
            print("✓ Explored ProductInterface type")
            print("✓ Browsed product categories")
            print("\n🎉 All product query examples completed successfully!\n")

    return 0


if __name__ == "__main__":
    try:
        sys.exit(asyncio.run(main()))
    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
