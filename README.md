# Magento 2 GraphQL Documentation MCP Server

A local STDIO MCP server that provides tools to search and retrieve Magento 2 GraphQL API documentation from local markdown files.

> **📖 New to setup?** See [SETUP.md](SETUP.md) for a step-by-step quick start guide.

## Features

- **Search Documentation**: Full-text search across 350+ GraphQL documentation pages
- **Get Complete Documents**: Retrieve full documentation with metadata
- **Search GraphQL Elements**: Find queries, mutations, types, and interfaces
- **Get Element Details**: View complete schema element definitions with examples
- **Browse Categories**: Navigate documentation hierarchy (schema, develop, usage, tutorials)
- **Access Tutorials**: Get step-by-step learning paths (e.g., checkout workflow)
- **Search Code Examples**: Find working code examples in GraphQL, JSON, JavaScript
- **Discover Related Docs**: Find related documentation automatically
- **Offline Operation**: Works entirely offline using local markdown files
- **Fast Startup**: Only re-indexes if documentation files have changed (<5 seconds)

## How it Works

1. **Parsing**: On startup, the server parses markdown files with YAML frontmatter
2. **Extraction**: Extracts metadata, code blocks, and GraphQL schema elements
3. **Indexing**: Stores data in SQLite with FTS5 full-text search indexes
4. **Searching**: Provides intelligent search across documentation, code, and schema

## Quick Start

### Step 1: Clone the Documentation Repository

The MCP server requires access to the Adobe Commerce GraphQL documentation markdown files. Clone the official repository:

```bash
# Clone the commerce-webapi repository
git clone https://github.com/AdobeDocs/commerce-webapi.git

# The GraphQL docs are located at:
# commerce-webapi/src/pages/graphql/
```

### Step 2: Set Up the Documentation Path

You have two options for configuring the documentation path:

**Option A: Using a Symlink (Recommended)**

Create a symlink in the project directory:

```bash
cd magento-graphql-docs-mcp
ln -s /path/to/commerce-webapi/src/pages/graphql data
```

**Option B: Using Environment Variable**

Set the `MAGENTO_GRAPHQL_DOCS_PATH` environment variable:

```bash
export MAGENTO_GRAPHQL_DOCS_PATH="/path/to/commerce-webapi/src/pages/graphql"
```

To make this permanent, add it to your shell profile (`~/.bashrc`, `~/.zshrc`, etc.):

```bash
echo 'export MAGENTO_GRAPHQL_DOCS_PATH="/path/to/commerce-webapi/src/pages/graphql"' >> ~/.zshrc
source ~/.zshrc
```

### Step 3: Verify Documentation Access

Check that the documentation path is accessible:

```bash
# If using symlink:
ls -la data/

# If using environment variable:
ls -la $MAGENTO_GRAPHQL_DOCS_PATH/

# You should see files like:
# - index.md
# - release-notes.md
# - schema/ (directory)
# - tutorials/ (directory)
# - develop/ (directory)
```

### Step 4: Install the MCP Server

```bash
cd magento-graphql-docs-mcp
pip install -e .
```

### (Optional) Build and Run with Docker

If you prefer Docker, build the image and mount your docs path to `/data` (or set `MAGENTO_GRAPHQL_DOCS_PATH` to another location):

```bash
docker build -t magento-graphql-docs-mcp -f docker/Dockerfile .
docker run --rm -it \
  -v /absolute/path/to/commerce-webapi/src/pages/graphql:/data \
  magento-graphql-docs-mcp
```

Auto-fetch fallback: if you do not mount docs, the container can clone them on start. Control this with `MAGENTO_GRAPHQL_DOCS_AUTO_FETCH` (default: `true`):

```bash
# Let the container clone docs (uses /tmp/commerce-webapi/src/pages/graphql)
docker run --rm -it magento-graphql-docs-mcp

# Disable auto-fetch; require a mount or preset MAGENTO_GRAPHQL_DOCS_PATH
docker run --rm -it \
  -e MAGENTO_GRAPHQL_DOCS_AUTO_FETCH=false \
  -v /absolute/path/to/commerce-webapi/src/pages/graphql:/data \
  magento-graphql-docs-mcp
```

### Host-Side Docker Wrapper (STDIO)

Use the provided wrapper to run the container and forward STDIN/STDOUT for MCP clients (no TTY added):

```bash
# From repo root
./run-docker-mcp.sh
```

What it does:
- Builds the `magento-graphql-docs-mcp` image automatically if it is missing
- Mounts `MAGENTO_GRAPHQL_DOCS_PATH` (or `./data`) to `/data` if it exists; otherwise relies on auto-fetch
- Keeps STDIO clean for MCP clients; prints connection instructions on start
- Respects `MAGENTO_GRAPHQL_DOCS_AUTO_FETCH` (set to `false` to require a mounted path)

Point your MCP client command to the wrapper path. Example Claude Desktop config:

```json
{
  "mcpServers": {
    "magento-graphql-docs": {
      "command": "/absolute/path/to/run-docker-mcp.sh"
    }
  }
}
```

### VS Code MCP Configuration

Example VS Code MCP config using the Docker wrapper:

```json
{
  "servers": {
    "magento-webapi-docs": {
      "type": "stdio",
      "command": "/absolute/path/to/run-docker-mcp.sh"
    }
  }
}
```

After adding the server entry, open the VS Code MCP/Tools panel and press “Start” for `magento-webapi-docs` to launch the container-backed STDIO server.

### Step 5: Run and Verify

```bash
# Run the server (will parse and index 350 documents on first run)
magento-graphql-docs-mcp

# In another terminal, run verification tests:
python3 tests/verify_parser.py
python3 tests/verify_db.py
python3 tests/verify_server.py
```

## Installation

### Requirements

- Python 3.10 or higher
- Git (to clone the documentation repository)
- 350+ Magento 2 GraphQL documentation markdown files from [AdobeDocs/commerce-webapi](https://github.com/AdobeDocs/commerce-webapi)

### Detailed Setup

#### 1. Clone Both Repositories

```bash
# Clone the documentation source
git clone https://github.com/AdobeDocs/commerce-webapi.git

# Clone this MCP server
cd magento-graphql-docs-mcp
```

#### 2. Configure Documentation Path

The server looks for documentation in this order (with path validation on startup):

1. **Environment variable** `MAGENTO_GRAPHQL_DOCS_PATH` (if set, validates path exists)
2. **`./data/` directory** (symlink or directory with .md files in project root)
3. **`../commerce-webapi/src/pages/graphql/`** (sibling directory auto-detection)

If no valid path is found, the server will fail with a helpful error message explaining all three setup options.

Choose the method that works best for your setup:

```bash
# Method 1: Symlink (recommended for development)
ln -s ~/projects/commerce-webapi/src/pages/graphql data

# Method 2: Environment variable (recommended for deployment)
export MAGENTO_GRAPHQL_DOCS_PATH="$HOME/projects/commerce-webapi/src/pages/graphql"

# Method 3: Clone commerce-webapi as sibling directory
# magento-graphql-docs-mcp/
# commerce-webapi/
#   └── src/pages/graphql/
```

#### 3. Install Dependencies

```bash
pip install -e .
```

This installs:
- `fastmcp` - MCP server framework
- `sqlite-utils` - Database management
- `pydantic` - Data validation
- `python-frontmatter` - YAML frontmatter parsing
- `markdown-it-py` - Markdown processing

## Usage

### Running the Server

Once configured, start the server:

```bash
# Start the MCP server
magento-graphql-docs-mcp

# The server will:
# 1. Check if documentation has changed (compares file modification times)
# 2. Parse markdown files if needed (350 files, ~3-5 seconds)
# 3. Index content in SQLite with FTS5
# 4. Start listening for MCP requests over STDIO
```

On subsequent runs, if the documentation hasn't changed, startup is nearly instant (~0.87s).

### Configuration

The server uses environment variables for configuration:

#### Documentation Path

Set where the GraphQL documentation is located:

```bash
# Option 1: Absolute path (recommended)
export MAGENTO_GRAPHQL_DOCS_PATH="/Users/you/projects/commerce-webapi/src/pages/graphql"

# Option 2: Relative path (from project root)
export MAGENTO_GRAPHQL_DOCS_PATH="./data"

# Option 3: Home directory relative
export MAGENTO_GRAPHQL_DOCS_PATH="~/repos/commerce-webapi/src/pages/graphql"
```

**Default**: The server looks for documentation in these locations (in order, with validation):
1. `MAGENTO_GRAPHQL_DOCS_PATH` environment variable (validated on startup)
2. `./data/` directory in project root (must contain .md files)
3. `../commerce-webapi/src/pages/graphql/` (sibling directory auto-detection)

#### Database Location

Customize where the SQLite database is stored:

```bash
# Default: ~/.mcp/magento-graphql-docs/database.db
export MAGENTO_GRAPHQL_DOCS_DB_PATH="/custom/path/magento-graphql.db"
```

The database directory will be created automatically if it doesn't exist.

#### Performance Tuning (Optional)

Customize search behavior and limits:

```bash
# Number of search results to return (default: 5)
export MAGENTO_GRAPHQL_DOCS_TOP_K=10

# Max fields per GraphQL element (default: 20)
export MAGENTO_GRAPHQL_DOCS_MAX_FIELDS=30

# Max code preview length in characters (default: 400)
export MAGENTO_GRAPHQL_DOCS_CODE_PREVIEW=600
```

### Using with an MCP Client

Configure your MCP client (e.g., Claude Desktop, Cline, etc.) to use this server.

#### Example: Claude Desktop Configuration

Add to `~/Library/Application Support/Claude/claude_desktop_config.json` (macOS):

```json
{
  "mcpServers": {
    "magento-graphql-docs": {
      "command": "magento-graphql-docs-mcp",
      "env": {
        "MAGENTO_GRAPHQL_DOCS_PATH": "/Users/you/projects/commerce-webapi/src/pages/graphql"
      }
    }
  }
}
```

#### Example: Using Python Module Directly

```json
{
  "mcpServers": {
    "magento-graphql-docs": {
      "command": "python3",
      "args": ["-m", "magento_graphql_docs_mcp.server"],
      "env": {
        "MAGENTO_GRAPHQL_DOCS_PATH": "/path/to/commerce-webapi/src/pages/graphql"
      }
    }
  }
}
```

#### Example: With Custom Database Path

```json
{
  "mcpServers": {
    "magento-graphql-docs": {
      "command": "magento-graphql-docs-mcp",
      "env": {
        "MAGENTO_GRAPHQL_DOCS_PATH": "/path/to/commerce-webapi/src/pages/graphql",
        "MAGENTO_GRAPHQL_DOCS_DB_PATH": "/custom/databases/magento-graphql.db"
      }
    }
  }
}
```

After configuration, restart your MCP client to activate the server.

## Usage Examples

The `examples/` directory contains practical usage examples demonstrating all MCP tools:

### Available Examples

1. **Product Queries** (`examples/example_products.py`)
   - Search product documentation
   - Find product GraphQL queries and types
   - Explore ProductInterface details
   - Search product code examples

2. **Customer Queries** (`examples/example_customer.py`)
   - Search customer documentation
   - Find customer mutations (create, update)
   - Explore authentication and tokens
   - Find customer address operations

3. **Cart & Checkout** (`examples/example_cart_checkout.py`)
   - Search cart documentation
   - Complete checkout workflow tutorial
   - Find cart mutations and queries
   - Explore checkout step-by-step

### Running Examples

```bash
# Run individual examples
python3 examples/example_products.py
python3 examples/example_customer.py
python3 examples/example_cart_checkout.py

# Or run all examples at once
bash examples/run_all_examples.sh
```

See [examples/README.md](examples/README.md) for detailed documentation.

## MCP Tools

### 1. `search_documentation`

Search for documentation pages using keywords.

**Parameters:**
- `queries`: List of 1-3 short keyword queries (e.g., ["product", "cart"])
- `category`: Optional filter (schema, develop, usage, tutorials)
- `subcategory`: Optional filter (products, cart, customer, etc.)
- `content_type`: Optional filter (guide, reference, tutorial, schema)

**Example:**
```python
search_documentation(queries=["checkout"], category="tutorials")
```

### 2. `get_document`

Get complete documentation page by file path.

**Parameters:**
- `file_path`: Relative path to document (e.g., "schema/products/queries/products.md")

**Returns:** Full document content with metadata, frontmatter, and markdown.

### 3. `search_graphql_elements`

Search for GraphQL queries, mutations, types, or interfaces.

**Parameters:**
- `query`: Search term
- `element_type`: Optional filter (query, mutation, type, interface, union)

**Example:**
```python
search_graphql_elements(query="products", element_type="query")
```

### 4. `get_element_details`

Get complete details about a specific GraphQL element.

**Parameters:**
- `element_name`: Element name (e.g., "products", "createCustomer")
- `element_type`: Optional type filter

**Returns:** Full element definition with fields, parameters, source document, and code examples.

### 5. `list_categories`

List all documentation categories with document counts.

**Returns:** Hierarchical category tree showing all available documentation areas.

### 6. `get_tutorial`

Get complete tutorial with all steps in order.

**Parameters:**
- `tutorial_name`: Tutorial name (e.g., "checkout")

**Returns:** Sequential tutorial steps with code examples and explanations.

### 7. `search_examples`

Search for code examples by topic and language.

**Parameters:**
- `query`: Search term
- `language`: Optional language filter (graphql, json, javascript, php, bash)

**Example:**
```python
search_examples(query="add to cart", language="graphql")
```

### 8. `get_related_documents`

Find documents related to a specified document.

**Parameters:**
- `file_path`: File path of source document

**Returns:** Related documents based on category and keywords.

## Verification Scripts

Test each component independently.

**Important**: Run all tests from the project root directory:

```bash
# Navigate to project root
cd magento-graphql-docs-mcp

# Test the markdown parser
python3 tests/verify_parser.py

# Test database ingestion
python3 tests/verify_db.py

# Test MCP server and all 8 tools
python3 tests/verify_server.py

# Run performance benchmarks
python3 tests/benchmark_performance.py
```

Running tests from other directories will cause import errors.

## Database Schema

The server uses SQLite with the following tables:

- **documents**: All documentation pages with FTS5 index
- **code_blocks**: Code examples from documentation
- **graphql_elements**: Extracted GraphQL schema elements with FTS5 index
- **metadata**: Ingestion tracking

## Performance

Based on benchmarks (run `python3 tests/benchmark_performance.py`):

- **Startup Time**: 0.87s (when data unchanged) | 3-5s (first run or files changed)
- **Search Speed**: 5.5ms average (FTS5 direct: 0.7ms)
- **Document Retrieval**: 8.2ms
- **GraphQL Element Search**: 3.4ms
- **Database Size**: ~30 MB for 350 documents
- **Indexed Content**: 350 documents, 963 code blocks, 51 GraphQL elements

All performance targets exceeded: <5s startup ✓, <100ms searches ✓

## Example Queries

| Query | Tool | Result |
|-------|------|--------|
| "How do I query products?" | search_documentation | Product query documentation |
| "Show me product query details" | search_graphql_elements | products query definition |
| "Complete checkout flow" | get_tutorial | Step-by-step checkout guide |
| "Cart mutation examples" | search_examples | Working GraphQL cart examples |
| "All B2B documentation" | list_categories + search | B2B schema documentation |

## Development

### Project Structure

```
magento-graphql-docs-mcp/
├── magento_graphql_docs_mcp/
│   ├── __init__.py
│   ├── config.py          # Configuration
│   ├── parser.py          # Markdown + GraphQL parser
│   ├── ingest.py          # Database ingestion
│   └── server.py          # MCP server with 8 tools
├── tests/
│   ├── verify_parser.py   # Parser verification
│   ├── verify_db.py       # Database verification
│   └── verify_server.py   # Server verification
├── data/
│   └── (symlink to docs)
├── pyproject.toml
├── README.md
└── CLAUDE.md
```

### Architecture

```
Markdown Files (350)
    ↓
Parser (frontmatter + content + GraphQL extraction)
    ↓
SQLite (documents + code_blocks + graphql_elements + FTS5)
    ↓
FastMCP Server (8 tools via STDIO)
    ↓
MCP Client (Claude, IDE, etc.)
```

## Advantages

### vs Web Scraping
- ✅ Offline operation (no network required)
- ✅ Fast startup (3-5s vs 30-60s)
- ✅ Local control (works with custom docs)
- ✅ No HTML parsing complexity

### vs REST API MCP
- ✅ Includes tutorials and guides (not just API specs)
- ✅ Code examples searchable
- ✅ Narrative content for learning
- ✅ Tutorial workflows

### Unique Features
- 📚 350 documents indexed
- 🔍 8 specialized search tools
- 💡 Tutorial support
- 📝 Code example search
- 🔗 Related document discovery
- ⚡ Fast FTS5 search
- 🎯 GraphQL-aware parsing

## Troubleshooting

### Documentation Not Found Error

**Error**: `FileNotFoundError: Documentation directory not found!`

**The server now provides a helpful error message showing all three setup methods.**

**Solutions**:

1. **Verify the documentation repository is cloned:**
   ```bash
   git clone https://github.com/AdobeDocs/commerce-webapi.git
   ```

2. **Check the path is correct:**
   ```bash
   # If using environment variable:
   echo $MAGENTO_GRAPHQL_DOCS_PATH
   ls -la $MAGENTO_GRAPHQL_DOCS_PATH

   # If using symlink:
   ls -la data/
   # Should show a symlink pointing to the GraphQL docs

   # You should see 350+ markdown files and directories like:
   # - schema/
   # - tutorials/
   # - develop/
   # - index.md
   ```

3. **Set the correct path (choose one method):**
   ```bash
   # Method 1: Environment variable (recommended for deployment)
   export MAGENTO_GRAPHQL_DOCS_PATH="/path/to/commerce-webapi/src/pages/graphql"

   # Method 2: Create symlink (recommended for development)
   cd magento-graphql-docs-mcp
   ln -s /path/to/commerce-webapi/src/pages/graphql data
   # Verify: ls -la data/ should show the symlink

   # Method 3: Clone as sibling directory (automatic)
   cd parent-directory
   git clone https://github.com/AdobeDocs/commerce-webapi.git
   # Server will automatically find it
   ```

4. **Verify the setup:**
   ```bash
   # The server validates paths on startup and will show helpful errors
   magento-graphql-docs-mcp
   # If path is invalid, you'll see exactly which methods were tried
   ```

### Server Won't Start

**Error**: `ModuleNotFoundError: No module named 'magento_graphql_docs_mcp'`

**Solution**: Install the package in development mode:
```bash
cd magento-graphql-docs-mcp
pip install -e .
```

**Error**: Server starts but immediately exits

**Solution**: Check Python version (requires 3.10+):
```bash
python3 --version  # Should be 3.10 or higher
```

### No Search Results

**Issue**: Search returns no results even though documentation exists

**Solutions**:

1. **Use shorter, simpler keywords:**
   ```bash
   # Instead of: "customer authentication token generation"
   # Try: ["customer", "token"]

   # Instead of: "how to add products to cart"
   # Try: ["cart", "add"]
   ```

2. **Check if database was created:**
   ```bash
   ls -la ~/.mcp/magento-graphql-docs/
   # Should show database.db (around 30 MB)
   ```

3. **Verify data was indexed:**
   ```bash
   python3 tests/verify_db.py
   # Should show: 350 documents, 963 code blocks, 51 GraphQL elements
   ```

4. **Re-index the database:**
   ```bash
   rm ~/.mcp/magento-graphql-docs/database.db
   magento-graphql-docs-mcp  # Will parse and re-index everything
   ```

### Database Errors

**Error**: `sqlite3.OperationalError: database is locked`

**Solution**: Another process is using the database:
```bash
# Find and kill the process
lsof ~/.mcp/magento-graphql-docs/database.db
kill <PID>

# Or simply remove and recreate
rm ~/.mcp/magento-graphql-docs/database.db
magento-graphql-docs-mcp
```

**Error**: `sqlite3.DatabaseError: database disk image is malformed`

**Solution**: Database is corrupted, recreate it:
```bash
rm -rf ~/.mcp/magento-graphql-docs/
magento-graphql-docs-mcp  # Will recreate from scratch
```

### Slow Performance

**Issue**: First startup takes >10 seconds

**Solution**: This is normal! First run parses 350 files. Subsequent runs are <1s.

**Issue**: Every startup is slow

**Solution**: Documentation mtime is changing. Check:
```bash
# Verify git isn't changing file times
cd /path/to/commerce-webapi
git status
git pull  # Update to latest if needed
```

### Verification Failed

**Issue**: `verify_server.py` fails with connection errors

**Solution**:
```bash
# Ensure dependencies are installed
pip install -e ".[dev]"

# Check MCP client libraries
pip list | grep mcp

# Re-run individual verifications
python3 tests/verify_parser.py   # Test parsing
python3 tests/verify_db.py       # Test database
python3 tests/verify_server.py   # Test MCP server
```

### MCP Client Integration Issues

**Issue**: MCP client shows "Server not found" or "Connection failed"

**Solutions**:

1. **Verify command is correct:**
   ```bash
   # Test the command directly
   which magento-graphql-docs-mcp
   # or
   python3 -m magento_graphql_docs_mcp.server
   ```

2. **Check environment variables in MCP config:**
   ```json
   {
     "mcpServers": {
       "magento-graphql-docs": {
         "command": "magento-graphql-docs-mcp",
         "env": {
           "MAGENTO_GRAPHQL_DOCS_PATH": "/FULL/PATH/to/commerce-webapi/src/pages/graphql"
         }
       }
     }
   }
   ```

   **Important**: Use absolute paths, not `~` or relative paths in MCP config.

3. **Check logs:**
   - Claude Desktop: `~/Library/Logs/Claude/` (macOS)
   - Look for error messages related to the server

### Getting Help

If you're still having issues:

1. **Run all verification scripts:**
   ```bash
   python3 tests/verify_parser.py
   python3 tests/verify_db.py
   python3 tests/verify_server.py
   python3 tests/benchmark_performance.py
   ```

2. **Check your setup:**
   ```bash
   # Python version
   python3 --version

   # Documentation path
   echo $MAGENTO_GRAPHQL_DOCS_PATH
   ls -la $MAGENTO_GRAPHQL_DOCS_PATH | head -20

   # Database
   ls -la ~/.mcp/magento-graphql-docs/

   # Package installation
   pip show magento-graphql-docs-mcp
   ```

3. **Create a GitHub issue** with the output of the above commands.

## License

MIT

## Contributing

Contributions welcome! Please test all changes with verification scripts before submitting.

## Support

For issues or questions:
1. Run verification scripts to diagnose issues
2. Check database location and permissions
3. Verify documentation path is correct
