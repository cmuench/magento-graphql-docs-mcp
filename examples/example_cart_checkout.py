#!/usr/bin/env python3
"""
Example: Working with Cart and Checkout in Magento GraphQL

This script demonstrates:
1. Searching for cart documentation
2. Finding cart mutations (create, add items, etc.)
3. Getting checkout tutorial
4. Finding cart-related code examples
5. Exploring the complete checkout workflow
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
    """Run cart and checkout examples"""
    print_section("Magento GraphQL - Cart & Checkout Examples")

    server_params = StdioServerParameters(
        command=sys.executable,
        args=["-m", "magento_graphql_docs_mcp.server"],
        env=None
    )

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            print("✓ Connected to MCP server\n")

            # Example 1: Search for cart documentation
            print_section("Example 1: Search for Cart Documentation")
            result = await session.call_tool("search_documentation", arguments={
                "queries": ["cart"],
                "category": "schema"
            })
            print(result.content[0].text[:1000])
            print("\n... (truncated for readability)")

            # Example 2: Find cart mutations
            print_section("Example 2: Find Cart Mutations")
            result = await session.call_tool("search_graphql_elements", arguments={
                "query": "cart",
                "element_type": "mutation"
            })
            print(result.content[0].text[:1200])
            print("\n... (truncated for readability)")

            # Example 3: Get createEmptyCart mutation details
            print_section("Example 3: Get 'createEmptyCart' Mutation Details")
            result = await session.call_tool("search_graphql_elements", arguments={
                "query": "createEmptyCart"
            })
            print(result.content[0].text[:1000])
            print("\n... (truncated for readability)")

            # Example 4: Get the checkout tutorial
            print_section("Example 4: Get Complete Checkout Tutorial")
            result = await session.call_tool("get_tutorial", arguments={
                "tutorial_name": "checkout"
            })
            print(result.content[0].text[:2000])
            print("\n... (truncated - showing first 2 steps)")

            # Example 5: Search for add to cart examples
            print_section("Example 5: Search for 'Add to Cart' Examples")
            result = await session.call_tool("search_examples", arguments={
                "query": "addProductsToCart",
                "language": "graphql"
            })
            print(result.content[0].text[:1200])
            print("\n... (truncated for readability)")

            # Example 6: Find cart query examples
            print_section("Example 6: Find Cart Query Examples")
            result = await session.call_tool("search_graphql_elements", arguments={
                "query": "cart",
                "element_type": "query"
            })
            print(result.content[0].text[:1000])
            print("\n... (truncated for readability)")

            # Example 7: Search for checkout-specific documentation
            print_section("Example 7: Search for Checkout Documentation")
            result = await session.call_tool("search_documentation", arguments={
                "queries": ["checkout"],
                "category": "tutorials"
            })
            print(result.content[0].text[:1000])
            print("\n... (truncated for readability)")

            # Example 8: Find related cart documents
            print_section("Example 8: Find Related Cart Documents")
            result = await session.call_tool("search_documentation", arguments={
                "queries": ["cart"],
                "content_type": "schema"
            })

            # Get the first document path
            lines = result.content[0].text.split('\n')
            file_path = None
            for line in lines:
                if line.startswith("**Path:**"):
                    file_path = line.replace("**Path:**", "").strip()
                    break

            if file_path:
                print(f"Finding related documents for: {file_path}\n")
                result = await session.call_tool("get_related_documents", arguments={
                    "file_path": file_path
                })
                print(result.content[0].text[:1000])
                print("\n... (truncated for readability)")
            else:
                print("Could not find cart document path")

            # Example 9: Search for JSON cart response examples
            print_section("Example 9: Find Cart JSON Response Examples")
            result = await session.call_tool("search_examples", arguments={
                "query": "cart",
                "language": "json"
            })
            print(result.content[0].text[:1000])
            print("\n... (truncated for readability)")

            # Example 10: List all tutorial categories
            print_section("Example 10: Browse All Tutorials")
            result = await session.call_tool("list_categories", arguments={})
            lines = result.content[0].text.split('\n')

            # Find tutorials section
            in_tutorials = False
            print("Available tutorials:")
            for line in lines:
                if line.startswith("## tutorials"):
                    in_tutorials = True
                    print(line)
                    continue
                if in_tutorials:
                    if line.startswith("##"):
                        break
                    if line.strip():
                        print(line)

            print_section("Summary - Checkout Workflow")
            print("Complete checkout workflow with MCP tools:")
            print("")
            print("1. Create empty cart       → createEmptyCart mutation")
            print("2. Add products to cart    → addProductsToCart mutation")
            print("3. Set shipping address    → setShippingAddressesOnCart mutation")
            print("4. Set shipping method     → setShippingMethodsOnCart mutation")
            print("5. Set payment method      → setPaymentMethodOnCart mutation")
            print("6. Place order             → placeOrder mutation")
            print("")
            print("✓ Searched cart documentation")
            print("✓ Found cart mutations")
            print("✓ Retrieved checkout tutorial")
            print("✓ Located code examples")
            print("✓ Explored related documents")
            print("✓ Browsed tutorials")
            print("\n🎉 All cart & checkout examples completed successfully!\n")

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
