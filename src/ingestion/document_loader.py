"""
Document loader for markdown files with frontmatter support.

Loads markdown documents from filesystem and extracts YAML frontmatter metadata.
"""

from pathlib import Path
from typing import Dict, Any, Tuple
from dataclasses import dataclass
import re
import yaml


@dataclass
class Document:
    """Represents a loaded document with content and metadata."""
    
    document_id: str
    content: str
    metadata: Dict[str, Any]


def _parse_frontmatter(content: str) -> Tuple[Dict[str, Any], str]:
    """
    Parse YAML frontmatter from markdown content.
    
    Args:
        content: Raw markdown content with potential frontmatter
        
    Returns:
        Tuple of (metadata dict, content without frontmatter)
        
    Raises:
        ValueError: If frontmatter is malformed
    """
    if not content.startswith("---"):
        return {}, content
    
    parts = content.split("---", 2)
    
    if len(parts) < 3:
        raise ValueError("Malformed frontmatter: missing closing '---'")
    
    try:
        metadata = yaml.safe_load(parts[1]) or {}
    except yaml.YAMLError as e:
        raise ValueError(f"Invalid YAML in frontmatter: {e}")
    
    document_content = parts[2].lstrip("\n")
    
    return metadata, document_content


def _slugify(text: str) -> str:
    """
    Convert text to a URL-friendly slug.
    
    Args:
        text: Text to slugify
        
    Returns:
        Lowercase slug with hyphens instead of spaces
    """
    slug = text.lower()
    slug = re.sub(r'[\s_]+', '-', slug)  # Replace spaces/underscores with hyphens
    slug = re.sub(r'[^a-z0-9-]', '', slug)  # Remove non-alphanumeric except hyphens
    slug = re.sub(r'-+', '-', slug)  # Collapse multiple hyphens
    return slug.strip('-')  # Remove leading/trailing hyphens


def load_document(file_path: Path) -> Document:
    """
    Load a markdown document and extract frontmatter metadata.
    
    Args:
        file_path: Path to the markdown file
        
    Returns:
        Document with content (frontmatter stripped), metadata, and generated document_id
        
    Raises:
        FileNotFoundError: If file does not exist
        ValueError: If frontmatter is malformed
    """
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    
    content = file_path.read_text()
    metadata, document_content = _parse_frontmatter(content)
    
    # Generate document_id from title
    title = metadata.get('title', '')
    document_id = _slugify(title)
    
    return Document(
        document_id=document_id,
        content=document_content,
        metadata=metadata
    )
