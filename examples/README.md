# Usage Examples

Practical examples demonstrating how to use the Magento GraphQL Documentation MCP server.

## Prerequisites

Before running these examples:

1. **Install the MCP server:**
   ```bash
   cd magento-graphql-docs-mcp
   pip install -e .
   ```

2. **Configure documentation path:**
   ```bash
   export MAGENTO_GRAPHQL_DOCS_PATH="/path/to/commerce-webapi/src/pages/graphql"
   ```

3. **Verify setup:**
   ```bash
   python3 tests/verify_server.py
   ```

## Available Examples

### 1. Product Queries (`example_products.py`)

Demonstrates working with product documentation:
- Searching for product documentation
- Finding product GraphQL queries and types
- Getting detailed element information
- Searching for product code examples
- Exploring ProductInterface

**Run:**
```bash
python3 examples/example_products.py
```

**Shows:**
- ✓ Product schema documentation
- ✓ Product GraphQL queries
- ✓ ProductInterface type details
- ✓ Product query code examples
- ✓ Product category browsing

---

### 2. Customer Queries (`example_customer.py`)

Demonstrates working with customer documentation:
- Searching for customer documentation
- Finding customer mutations (create, update)
- Getting customer authentication details
- Finding customer address operations
- Exploring customer response examples

**Run:**
```bash
python3 examples/example_customer.py
```

**Shows:**
- ✓ Customer schema documentation
- ✓ Customer mutations (create, update)
- ✓ Customer authentication & tokens
- ✓ Customer address mutations
- ✓ Customer JSON response examples

---

### 3. Cart & Checkout (`example_cart_checkout.py`)

Demonstrates the complete checkout workflow:
- Searching for cart documentation
- Finding cart mutations
- Getting the checkout tutorial
- Exploring the complete checkout flow
- Finding cart-related code examples

**Run:**
```bash
python3 examples/example_cart_checkout.py
```

**Shows:**
- ✓ Cart schema documentation
- ✓ Cart mutations (create, add items)
- ✓ Complete checkout tutorial
- ✓ Checkout workflow steps
- ✓ Cart query examples
- ✓ Related cart documents

**Checkout workflow covered:**
1. Create empty cart (`createEmptyCart`)
2. Add products to cart (`addProductsToCart`)
3. Set shipping address (`setShippingAddressesOnCart`)
4. Set shipping method (`setShippingMethodsOnCart`)
5. Set payment method (`setPaymentMethodOnCart`)
6. Place order (`placeOrder`)

---

## Running All Examples

To run all examples in sequence:

```bash
# Run all examples
python3 examples/example_products.py
python3 examples/example_customer.py
python3 examples/example_cart_checkout.py
```

Or create a simple script:

```bash
#!/bin/bash
echo "Running Product Examples..."
python3 examples/example_products.py

echo -e "\n\nRunning Customer Examples..."
python3 examples/example_customer.py

echo -e "\n\nRunning Cart & Checkout Examples..."
python3 examples/example_cart_checkout.py

echo -e "\n\n✅ All examples completed!"
```

## What These Examples Demonstrate

### MCP Tools Used

Each example demonstrates multiple MCP tools:

| Tool | Products | Customer | Cart |
|------|----------|----------|------|
| `search_documentation` | ✓ | ✓ | ✓ |
| `get_document` | - | ✓ | - |
| `search_graphql_elements` | ✓ | ✓ | ✓ |
| `get_element_details` | ✓ | - | ✓ |
| `list_categories` | ✓ | - | ✓ |
| `get_tutorial` | - | - | ✓ |
| `search_examples` | ✓ | ✓ | ✓ |
| `get_related_documents` | - | - | ✓ |

**All 8 tools** are demonstrated across the three examples.

### Common Patterns

All examples follow this pattern:

1. **Connect to MCP server** via STDIO
2. **Initialize session**
3. **Call multiple tools** with different queries
4. **Display formatted results**
5. **Show practical use cases**

### Real-World Scenarios

- **Product Example**: How to build a product catalog
- **Customer Example**: How to implement authentication & account management
- **Cart Example**: How to implement a complete checkout flow

## Troubleshooting

### Module Not Found Error

```bash
ModuleNotFoundError: No module named 'mcp'
```

**Solution**: Install dev dependencies:
```bash
pip install -e ".[dev]"
```

### Documentation Not Found

```bash
FileNotFoundError: Documentation directory not found
```

**Solution**: Set the documentation path:
```bash
export MAGENTO_GRAPHQL_DOCS_PATH="/path/to/commerce-webapi/src/pages/graphql"
```

### Server Connection Failed

**Solution**: Verify the server works standalone:
```bash
python3 tests/verify_server.py
```

## Expected Output

Each example will show:
- Section headers for each operation
- Formatted results from MCP tools
- Truncated output for readability
- Summary of operations completed
- Success message

Example output format:
```
======================================================================
  Example 1: Search for Product Documentation
======================================================================

### Product interface implementations
**Path:** schema/products/interfaces/types/index.md
**Category:** schema/products
**Type:** schema
...

✓ All operations completed successfully!
```

## Performance

- Each example completes in **~2-3 seconds**
- Server startup time: **~1 second** (if database exists)
- Each tool call: **~5-10ms**

## Next Steps

After running these examples:

1. **Modify the queries** - Try your own search terms
2. **Explore other tools** - Add calls to other MCP tools
3. **Build integrations** - Use these patterns in your applications
4. **Read the docs** - See README.md for complete tool documentation

## Contributing

Feel free to add more examples:
- Orders and returns
- Payment methods
- B2B functionality
- Custom GraphQL schema extensions

Each example should:
- Focus on a specific use case
- Demonstrate multiple MCP tools
- Include clear comments
- Show practical applications
- Handle errors gracefully
