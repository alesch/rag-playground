# Roadmap: Document Loader

**Module**: `src/ingestion/document_loader.py`  
**Test File**: `tests/test_document_loader.py`  
**Type**: Technical Implementation (filesystem integration)

---

## Test Scenarios

1. Load single markdown file and extract frontmatter fields (version, title, tags)
2. Generate document_id by slugifying title
3. Load all corpus documents
4. Raise error when required frontmatter fields are missing (version or title)

---

## Implementation Approach

Single test at a time with RED→GREEN→REFACTOR cycles.

Start with Test 1 (simplest: load one file with frontmatter).

---

## Frontmatter Format

```yaml
---
version: 1
title: Technical Infrastructure Documentation
tags: [technical, infrastructure, azure, security]
---
```

**Required fields**: `version`, `title`  
**Optional fields**: `tags`

---

## Document ID Generation

`document_id` = slugified title

Examples:
- "Technical Infrastructure Documentation" → "technical-infrastructure-documentation"
- "SOC 2 Compliance Documentation" → "soc-2-compliance-documentation"
