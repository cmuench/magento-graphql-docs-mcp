import os
import sys
from pathlib import Path

def get_db_path() -> str:
    """
    Determines the database path.
    Prioritizes MAGENTO_GRAPHQL_DOCS_DB_PATH environment variable.
    Defaults to ~/.mcp/magento-graphql-docs/database.db.
    Ensures the parent directory exists.
    """
    env_path = os.environ.get("MAGENTO_GRAPHQL_DOCS_DB_PATH")
    if env_path:
        db_path = Path(env_path)
    else:
        db_path = Path.home() / ".mcp" / "magento-graphql-docs" / "database.db"

    # Ensure directory exists
    db_path.parent.mkdir(parents=True, exist_ok=True)

    return str(db_path)

def get_docs_path() -> str:
    """
    Determines the GraphQL documentation directory path.

    Priority order:
    1. MAGENTO_GRAPHQL_DOCS_PATH environment variable
    2. ./data/ directory (symlink or actual directory in project root)
    3. ../commerce-webapi/src/pages/graphql/ (sibling directory)

    Validates that the path exists and contains documentation files.
    Raises FileNotFoundError with helpful message if not found.
    """
    # Priority 1: Environment variable
    env_path = os.environ.get("MAGENTO_GRAPHQL_DOCS_PATH")
    if env_path:
        path = Path(env_path).resolve()
        if not path.exists():
            print(f"ERROR: MAGENTO_GRAPHQL_DOCS_PATH set to '{env_path}' but directory does not exist", file=sys.stderr)
            raise FileNotFoundError(
                f"Documentation directory not found: {env_path}\n"
                f"The MAGENTO_GRAPHQL_DOCS_PATH environment variable points to a non-existent directory.\n"
                f"Please verify the path or unset the variable to use auto-detection."
            )
        return str(path)

    # Priority 2: ./data/ directory (relative to project root)
    package_dir = Path(__file__).parent.parent
    data_path = package_dir / "data"
    if data_path.exists():
        # Check if it's a symlink or directory with content
        if data_path.is_symlink() or (data_path.is_dir() and list(data_path.glob("*.md"))):
            return str(data_path.resolve())

    # Priority 3: Sibling commerce-webapi directory
    sibling_path = package_dir.parent / "commerce-webapi" / "src" / "pages" / "graphql"
    if sibling_path.exists():
        return str(sibling_path)

    # No valid path found - provide helpful error message
    error_msg = (
        "Documentation directory not found!\n\n"
        "The Magento GraphQL documentation files are required but could not be located.\n\n"
        "Please choose one of these setup methods:\n\n"
        "1. Set environment variable:\n"
        f"   export MAGENTO_GRAPHQL_DOCS_PATH='/path/to/commerce-webapi/src/pages/graphql'\n\n"
        "2. Create symlink in project (recommended for development):\n"
        f"   cd {package_dir}\n"
        f"   ln -s /path/to/commerce-webapi/src/pages/graphql data\n\n"
        "3. Clone commerce-webapi as sibling directory:\n"
        f"   cd {package_dir.parent}\n"
        "   git clone https://github.com/AdobeDocs/commerce-webapi.git\n\n"
        "For detailed setup instructions, see SETUP.md"
    )
    print(f"ERROR: {error_msg}", file=sys.stderr)
    raise FileNotFoundError(error_msg)

# Configuration values
DB_PATH = get_db_path()
DOCS_PATH = get_docs_path()

# Configurable constants
DB_TOP_K = int(os.environ.get("MAGENTO_GRAPHQL_DOCS_TOP_K", "5"))
MAX_FIELDS_PER_ELEMENT = int(os.environ.get("MAGENTO_GRAPHQL_DOCS_MAX_FIELDS", "20"))
MAX_CODE_PREVIEW_LENGTH = int(os.environ.get("MAGENTO_GRAPHQL_DOCS_CODE_PREVIEW", "400"))
SEARCH_RESULT_MULTIPLIER = 2  # Fetch 2x results before filtering
