# Setup Guide - Magento 2 GraphQL Documentation MCP Server

Quick setup guide for developers.

## Prerequisites

- Python 3.10 or higher
- Git
- Terminal/Command line access

## Step-by-Step Setup

### 1. Clone the Documentation Repository

The MCP server needs access to Adobe Commerce GraphQL documentation files.

```bash
# Clone the official documentation
git clone https://github.com/AdobeDocs/commerce-webapi.git

# Note the path to the GraphQL docs
# Location: commerce-webapi/src/pages/graphql/
```

### 2. Clone This MCP Server (if not already done)

```bash
git clone <this-repository-url>
cd magento-graphql-docs-mcp
```

### 3. Configure Documentation Path

Choose one of these methods:

#### Method A: Symlink (Recommended for Development)

```bash
# From the magento-graphql-docs-mcp directory
ln -s /full/path/to/commerce-webapi/src/pages/graphql data

# Example:
ln -s ~/projects/commerce-webapi/src/pages/graphql data
```

Verify the symlink:
```bash
ls -la data/
# Should show: lrwxr-xr-x ... data -> /path/to/commerce-webapi/src/pages/graphql

# Test that it works:
ls data/index.md
# Should show the GraphQL documentation index file
```

#### Method B: Environment Variable (Recommended for Deployment)

```bash
# Add to your shell profile (~/.bashrc, ~/.zshrc, etc.)
export MAGENTO_GRAPHQL_DOCS_PATH="/full/path/to/commerce-webapi/src/pages/graphql"

# Apply the changes
source ~/.zshrc  # or ~/.bashrc
```

Verify:
```bash
echo $MAGENTO_GRAPHQL_DOCS_PATH
ls -la $MAGENTO_GRAPHQL_DOCS_PATH
```

#### Method C: Sibling Directory (Auto-detection)

If you clone both repos in the same parent directory:

```
projects/
├── magento-graphql-docs-mcp/      ← This server
└── commerce-webapi/                ← Documentation
    └── src/pages/graphql/
```

The server will automatically find the documentation.

### 4. Install the MCP Server

```bash
cd magento-graphql-docs-mcp
pip install -e .
```

Expected output:
```
Successfully installed magento-graphql-docs-mcp
```

### 5. Verify Installation

Run the verification tests from the project root:

```bash
# Make sure you're in the project root
cd magento-graphql-docs-mcp

# Test 1: Verify parser (should find 350 documents)
python3 tests/verify_parser.py

# Test 2: Verify database (should create SQLite database)
python3 tests/verify_db.py

# Test 3: Verify MCP server (should test all 8 tools)
python3 tests/verify_server.py

# Test 4: Benchmark performance
python3 tests/benchmark_performance.py
```

**Important**: All tests must be run from the project root directory, not from inside the `tests/` directory.

Expected results:
- ✓ 350 documents parsed
- ✓ 963 code blocks extracted
- ✓ 51 GraphQL elements found
- ✓ All 8 MCP tools working
- ✓ Startup time: <5 seconds
- ✓ Search speed: <100ms

### 6. Run the Server

```bash
magento-graphql-docs-mcp
```

On first run, the server will:
1. Parse 350 markdown files (~3-5 seconds)
2. Extract code blocks and GraphQL elements
3. Create SQLite database with FTS5 indexes
4. Start listening for MCP requests

On subsequent runs (if documentation hasn't changed):
- Startup time: ~0.87 seconds

## Configure MCP Client

### Claude Desktop

Edit `~/Library/Application Support/Claude/claude_desktop_config.json` (macOS):

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

**Important**:
- Use **absolute paths** (not `~` or relative paths)
- Replace `/Users/you/projects/` with your actual path

### Other MCP Clients

For other clients (Cline, etc.), use similar configuration:

```json
{
  "command": "python3",
  "args": ["-m", "magento_graphql_docs_mcp.server"],
  "env": {
    "MAGENTO_GRAPHQL_DOCS_PATH": "/absolute/path/to/commerce-webapi/src/pages/graphql"
  }
}
```

## Verification Checklist

Before using the server, verify:

- [ ] Python 3.10+ installed (`python3 --version`)
- [ ] commerce-webapi repository cloned
- [ ] Documentation path accessible (`ls $MAGENTO_GRAPHQL_DOCS_PATH`)
- [ ] MCP server installed (`pip show magento-graphql-docs-mcp`)
- [ ] All tests pass (`python3 tests/verify_*.py`)
- [ ] Database created (`ls ~/.mcp/magento-graphql-docs/database.db`)
- [ ] MCP client configured with absolute path

## Quick Troubleshooting

### Documentation Not Found

The server now validates paths on startup and provides helpful error messages.

```bash
# Check if path is set
echo $MAGENTO_GRAPHQL_DOCS_PATH

# Check if directory exists
ls -la $MAGENTO_GRAPHQL_DOCS_PATH

# Check if symlink exists
ls -la data/

# If not found, choose a setup method:

# Option 1: Set environment variable
export MAGENTO_GRAPHQL_DOCS_PATH="/path/to/commerce-webapi/src/pages/graphql"

# Option 2: Create symlink
cd magento-graphql-docs-mcp
ln -s /path/to/commerce-webapi/src/pages/graphql data

# Option 3: Clone as sibling (automatic detection)
cd ..
git clone https://github.com/AdobeDocs/commerce-webapi.git
```

The server will tell you exactly which paths it checked when it fails to find the documentation.

### Module Not Found

```bash
# Reinstall in development mode
cd magento-graphql-docs-mcp
pip install -e .
```

### No Search Results

```bash
# Recreate database
rm ~/.mcp/magento-graphql-docs/database.db
magento-graphql-docs-mcp
```

### Server Won't Start in MCP Client

1. Test command directly:
   ```bash
   which magento-graphql-docs-mcp
   magento-graphql-docs-mcp  # Should start server
   ```

2. Check MCP client logs:
   - Claude Desktop: `~/Library/Logs/Claude/`

3. Use absolute paths in config (not `~` or relative)

## Next Steps

Once setup is complete:

1. **Try the tools** - Use your MCP client to search documentation
2. **Read the documentation** - See README.md for tool details
3. **Explore the code** - See CLAUDE.md for architecture details

## Getting Help

If you encounter issues:

1. Run all verification scripts and check output
2. Check the Troubleshooting section in README.md
3. Create a GitHub issue with:
   - Output of verification scripts
   - Your Python version
   - Documentation path configuration
   - Error messages

## Summary

```bash
# Quick setup (copy-paste)
git clone https://github.com/AdobeDocs/commerce-webapi.git
cd magento-graphql-docs-mcp
export MAGENTO_GRAPHQL_DOCS_PATH="/path/to/commerce-webapi/src/pages/graphql"
pip install -e .
python3 tests/verify_parser.py
python3 tests/verify_db.py
python3 tests/verify_server.py
magento-graphql-docs-mcp
```

You're all set! 🎉
