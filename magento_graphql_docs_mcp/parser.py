import hashlib
import logging
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional, Tuple
from pydantic import BaseModel, Field
import frontmatter
from .config import MAX_FIELDS_PER_ELEMENT

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Document(BaseModel):
    """Represents a documentation page"""
    id: str  # SHA256 hash of file_path
    file_path: str  # Relative to docs root
    title: str
    description: Optional[str] = None
    keywords: List[str] = Field(default_factory=list)
    category: str  # e.g., "schema", "develop", "usage"
    subcategory: Optional[str] = None  # e.g., "products", "cart"
    content_type: str  # "guide", "reference", "tutorial", "schema"
    searchable_text: str  # Combined: title + description + content
    headers: List[str] = Field(default_factory=list)  # All markdown headers
    last_modified: datetime
    content_md: str  # Full markdown content


class CodeBlock(BaseModel):
    """Represents a code example"""
    document_id: str
    language: str  # graphql, json, javascript, bash
    code: str
    context: Optional[str] = None  # Surrounding text for context
    line_number: int


class GraphQLElement(BaseModel):
    """Represents a GraphQL schema element"""
    document_id: str
    element_type: str  # query, mutation, type, interface, union
    name: str
    fields: List[str] = Field(default_factory=list)
    parameters: List[str] = Field(default_factory=list)
    return_type: Optional[str] = None
    description: Optional[str] = None
    searchable_text: str


class MarkdownDocParser:
    """Parse markdown documentation files"""

    def __init__(self, docs_root: Path):
        self.docs_root = Path(docs_root)
        if not self.docs_root.exists():
            raise FileNotFoundError(f"Documentation directory not found: {docs_root}")

    def walk_directory(self) -> List[Path]:
        """Find all .md files recursively"""
        md_files = list(self.docs_root.rglob("**/*.md"))
        logger.info(f"Found {len(md_files)} markdown files")
        return md_files

    def parse_file(self, file_path: Path) -> Document:
        """Parse single markdown file"""
        # Read file content
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Parse frontmatter
        post = frontmatter.loads(content)
        metadata = post.metadata
        markdown_content = post.content

        # Get file stats
        stat = file_path.stat()
        last_modified = datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc)

        # Extract relative path
        rel_path = str(file_path.relative_to(self.docs_root))

        # Generate document ID
        doc_id = hashlib.sha256(rel_path.encode('utf-8')).hexdigest()

        # Extract category and subcategory from path
        category, subcategory = self.extract_category_from_path(file_path)

        # Determine content type
        content_type = self.determine_content_type(category, rel_path)

        # Extract title (from frontmatter or first header)
        title = metadata.get('title', self.extract_first_header(markdown_content) or rel_path)

        # Extract description
        description = metadata.get('description')

        # Extract keywords
        keywords = metadata.get('keywords', [])
        if isinstance(keywords, str):
            keywords = [keywords]

        # Extract headers
        headers = self.extract_headers(markdown_content)

        # Build searchable text
        searchable_text = self.build_searchable_text(
            title, description, markdown_content, keywords, headers
        )

        return Document(
            id=doc_id,
            file_path=rel_path,
            title=title,
            description=description,
            keywords=keywords,
            category=category,
            subcategory=subcategory,
            content_type=content_type,
            searchable_text=searchable_text,
            headers=headers,
            last_modified=last_modified,
            content_md=markdown_content
        )

    def extract_category_from_path(self, file_path: Path) -> Tuple[str, Optional[str]]:
        """Extract category and subcategory from file path"""
        rel_path = file_path.relative_to(self.docs_root)
        parts = rel_path.parts

        if len(parts) == 1:
            # Root level file (e.g., index.md, release-notes.md)
            return "root", None

        category = parts[0]  # First directory: schema, develop, usage, tutorials, etc.

        # Extract subcategory (second level directory if exists)
        subcategory = None
        if len(parts) > 2:
            subcategory = parts[1]

        return category, subcategory

    def determine_content_type(self, category: str, rel_path: str) -> str:
        """Determine content type based on category and path"""
        if category == "schema":
            return "schema"
        elif category == "tutorials":
            return "tutorial"
        elif category in ["develop", "usage"]:
            return "guide"
        elif "reference" in rel_path.lower():
            return "reference"
        else:
            return "guide"

    def extract_first_header(self, markdown: str) -> Optional[str]:
        """Extract first markdown header as fallback title"""
        for line in markdown.split('\n'):
            line = line.strip()
            if line.startswith('#'):
                # Remove # symbols and strip whitespace
                return line.lstrip('#').strip()
        return None

    def extract_headers(self, markdown: str) -> List[str]:
        """Extract all markdown headers"""
        headers = []
        for line in markdown.split('\n'):
            line = line.strip()
            if line.startswith('#'):
                # Remove # symbols and keep the text
                header_text = line.lstrip('#').strip()
                if header_text:
                    headers.append(header_text)
        return headers

    def build_searchable_text(
        self,
        title: str,
        description: Optional[str],
        content: str,
        keywords: List[str],
        headers: List[str]
    ) -> str:
        """Build searchable text from all available text"""
        parts = [title]

        if description:
            parts.append(description)

        if keywords:
            parts.extend(keywords)

        # Add headers
        parts.extend(headers)

        # Add content (remove code blocks and excessive whitespace)
        content_text = self.clean_content(content)
        parts.append(content_text)

        return " ".join(filter(None, parts))

    def clean_content(self, markdown: str) -> str:
        """Clean markdown content for search indexing"""
        # Remove code blocks
        content = re.sub(r'```[\s\S]*?```', '', markdown)

        # Remove inline code
        content = re.sub(r'`[^`]+`', '', content)

        # Remove markdown links but keep text [text](url) -> text
        content = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', content)

        # Remove excessive whitespace
        content = ' '.join(content.split())

        return content

    def extract_code_blocks(self, markdown: str, doc_id: str) -> List[CodeBlock]:
        """Extract code blocks with language tags"""
        code_blocks = []
        lines = markdown.split('\n')
        i = 0
        line_number = 0

        while i < len(lines):
            line = lines[i]

            # Check for code block start
            if line.strip().startswith('```'):
                # Extract language
                language = line.strip()[3:].strip().lower()
                if not language:
                    language = "text"

                # Find code block end
                code_lines = []
                i += 1
                start_line = i + 1

                while i < len(lines) and not lines[i].strip().startswith('```'):
                    code_lines.append(lines[i])
                    i += 1

                code = '\n'.join(code_lines)

                # Extract context (previous paragraph)
                context = self.extract_context(lines, start_line - 2)

                code_blocks.append(CodeBlock(
                    document_id=doc_id,
                    language=language,
                    code=code,
                    context=context,
                    line_number=start_line
                ))

            i += 1
            line_number += 1

        return code_blocks

    def extract_context(self, lines: List[str], start_idx: int) -> Optional[str]:
        """Extract context before code block (previous paragraph)"""
        if start_idx < 0:
            return None

        # Look backwards for non-empty lines
        context_lines = []
        for i in range(start_idx, max(-1, start_idx - 5), -1):
            line = lines[i].strip()
            if line and not line.startswith('#'):
                context_lines.insert(0, line)
            elif context_lines:
                # Stop at empty line or header
                break

        return ' '.join(context_lines) if context_lines else None

    def extract_graphql_elements(self, code: str, doc_id: str) -> List[GraphQLElement]:
        """Extract GraphQL queries/mutations/types from code blocks"""
        elements = []

        # Detect query
        query_match = re.search(r'query\s+(\w+)', code)
        if query_match:
            name = query_match.group(1)
            fields = self.extract_fields(code)
            parameters = self.extract_parameters(code)

            elements.append(GraphQLElement(
                document_id=doc_id,
                element_type="query",
                name=name,
                fields=fields,
                parameters=parameters,
                searchable_text=f"query {name} {' '.join(fields)} {' '.join(parameters)}"
            ))

        # Detect mutation
        mutation_match = re.search(r'mutation\s+(\w+)', code)
        if mutation_match:
            name = mutation_match.group(1)
            fields = self.extract_fields(code)
            parameters = self.extract_parameters(code)

            elements.append(GraphQLElement(
                document_id=doc_id,
                element_type="mutation",
                name=name,
                fields=fields,
                parameters=parameters,
                searchable_text=f"mutation {name} {' '.join(fields)} {' '.join(parameters)}"
            ))

        # Detect type
        type_match = re.search(r'type\s+(\w+)', code)
        if type_match:
            name = type_match.group(1)
            fields = self.extract_fields(code)

            elements.append(GraphQLElement(
                document_id=doc_id,
                element_type="type",
                name=name,
                fields=fields,
                searchable_text=f"type {name} {' '.join(fields)}"
            ))

        # Detect interface
        interface_match = re.search(r'interface\s+(\w+)', code)
        if interface_match:
            name = interface_match.group(1)
            fields = self.extract_fields(code)

            elements.append(GraphQLElement(
                document_id=doc_id,
                element_type="interface",
                name=name,
                fields=fields,
                searchable_text=f"interface {name} {' '.join(fields)}"
            ))

        return elements

    def extract_fields(self, code: str) -> List[str]:
        """Extract field names from GraphQL code"""
        # Simple field extraction (field_name followed by optional type)
        fields = re.findall(r'\b([a-z_]\w*)\s*(?:\(|:|\{)', code, re.IGNORECASE)
        # Limit to MAX_FIELDS_PER_ELEMENT unique fields to avoid bloat
        return list(set(fields))[:MAX_FIELDS_PER_ELEMENT]

    def extract_parameters(self, code: str) -> List[str]:
        """Extract parameter names from GraphQL code"""
        # Extract parameters in format ($paramName: Type)
        params = re.findall(r'\$(\w+)\s*:', code)
        return list(set(params))

    def parse_all(self) -> Tuple[List[Document], List[CodeBlock], List[GraphQLElement]]:
        """Parse all markdown files and extract all data"""
        documents = []
        all_code_blocks = []
        all_graphql_elements = []

        files = self.walk_directory()

        for file_path in files:
            try:
                # Parse document
                doc = self.parse_file(file_path)
                documents.append(doc)

                # Extract code blocks
                code_blocks = self.extract_code_blocks(doc.content_md, doc.id)
                all_code_blocks.extend(code_blocks)

                # Extract GraphQL elements from GraphQL code blocks
                for block in code_blocks:
                    if block.language == 'graphql':
                        elements = self.extract_graphql_elements(block.code, doc.id)
                        all_graphql_elements.extend(elements)

            except Exception as e:
                logger.error(f"Error parsing {file_path}: {e}")
                continue

        logger.info(f"Parsed {len(documents)} documents, {len(all_code_blocks)} code blocks, {len(all_graphql_elements)} GraphQL elements")

        return documents, all_code_blocks, all_graphql_elements
