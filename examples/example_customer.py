#!/usr/bin/env python3
"""
Example: Working with Customer Queries in Magento GraphQL

This script demonstrates:
1. Searching for customer documentation
2. Finding customer mutations (create, update, etc.)
3. Getting customer query details
4. Finding customer-related code examples
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
    """Run customer query examples"""
    print_section("Magento GraphQL - Customer Query Examples")

    server_params = StdioServerParameters(
        command=sys.executable,
        args=["-m", "magento_graphql_docs_mcp.server"],
        env=None
    )

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            print("✓ Connected to MCP server\n")

            # Example 1: Search for customer documentation
            print_section("Example 1: Search for Customer Documentation")
            result = await session.call_tool("search_documentation", arguments={
                "queries": ["customer"],
                "category": "schema"
            })
            print(result.content[0].text[:1000])
            print("\n... (truncated for readability)")

            # Example 2: Find customer mutations
            print_section("Example 2: Find Customer Mutations")
            result = await session.call_tool("search_graphql_elements", arguments={
                "query": "customer",
                "element_type": "mutation"
            })
            print(result.content[0].text[:1200])
            print("\n... (truncated for readability)")

            # Example 3: Get createCustomer mutation details
            print_section("Example 3: Get 'createCustomer' Mutation Details")
            result = await session.call_tool("search_graphql_elements", arguments={
                "query": "createCustomer"
            })

            if "No GraphQL elements found" in result.content[0].text:
                print("Note: createCustomer not found as extracted element.")
                print("Searching for customer creation examples instead...\n")

                result = await session.call_tool("search_examples", arguments={
                    "query": "createCustomer",
                    "language": "graphql"
                })
                print(result.content[0].text[:1000])
            else:
                print(result.content[0].text[:1000])

            print("\n... (truncated for readability)")

            # Example 4: Search for customer authentication examples
            print_section("Example 4: Search for Customer Authentication")
            result = await session.call_tool("search_documentation", arguments={
                "queries": ["customer", "token"]
            })
            print(result.content[0].text[:1000])
            print("\n... (truncated for readability)")

            # Example 5: Find customer address mutation examples
            print_section("Example 5: Find Customer Address Mutations")
            result = await session.call_tool("search_graphql_elements", arguments={
                "query": "updateCustomerAddress"
            })
            print(result.content[0].text[:800])
            print("\n... (truncated for readability)")

            # Example 6: Get specific customer documentation
            print_section("Example 6: Get Customer Query Document")
            result = await session.call_tool("search_documentation", arguments={
                "queries": ["customer", "query"],
                "content_type": "schema"
            })

            # Extract file path from first result
            lines = result.content[0].text.split('\n')
            file_path = None
            for line in lines:
                if line.startswith("**Path:**"):
                    file_path = line.replace("**Path:**", "").strip()
                    break

            if file_path:
                print(f"Found customer documentation at: {file_path}\n")
                result = await session.call_tool("get_document", arguments={
                    "file_path": file_path
                })
                print(result.content[0].text[:1000])
                print("\n... (truncated for readability)")
            else:
                print("Could not extract file path from search results")

            # Example 7: Find customer code examples
            print_section("Example 7: Find Customer JSON Response Examples")
            result = await session.call_tool("search_examples", arguments={
                "query": "customer",
                "language": "json"
            })
            print(result.content[0].text[:1000])
            print("\n... (truncated for readability)")

            print_section("Summary")
            print("✓ Searched customer documentation")
            print("✓ Found customer mutations")
            print("✓ Located customer creation examples")
            print("✓ Found authentication documentation")
            print("✓ Retrieved address mutation details")
            print("✓ Explored specific customer documents")
            print("✓ Found JSON response examples")
            print("\n🎉 All customer query examples completed successfully!\n")

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
