#!/bin/bash
#
# Run all MCP server usage examples
#

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "========================================================================"
echo "  Running All Magento GraphQL MCP Server Examples"
echo "========================================================================"
echo ""

# Check if server can be run
if ! command -v magento-graphql-docs-mcp &> /dev/null; then
    echo "⚠️  Warning: magento-graphql-docs-mcp command not found"
    echo "   Make sure to run: pip install -e ."
    echo ""
fi

# Check documentation path
if [ -z "$MAGENTO_GRAPHQL_DOCS_PATH" ] && [ ! -L "$SCRIPT_DIR/../data" ]; then
    echo "⚠️  Warning: Documentation path not configured"
    echo "   Set MAGENTO_GRAPHQL_DOCS_PATH or create a 'data' symlink"
    echo ""
fi

echo "1/3: Running Product Query Examples..."
echo "========================================================================"
python3 "$SCRIPT_DIR/example_products.py"

echo ""
echo ""
echo "2/3: Running Customer Query Examples..."
echo "========================================================================"
python3 "$SCRIPT_DIR/example_customer.py"

echo ""
echo ""
echo "3/3: Running Cart & Checkout Examples..."
echo "========================================================================"
python3 "$SCRIPT_DIR/example_cart_checkout.py"

echo ""
echo "========================================================================"
echo "  ✅ All Examples Completed Successfully!"
echo "========================================================================"
echo ""
echo "Summary:"
echo "  ✓ Product queries and types"
echo "  ✓ Customer authentication and mutations"
echo "  ✓ Cart operations and checkout workflow"
echo ""
echo "All 8 MCP tools demonstrated across the examples."
echo ""
