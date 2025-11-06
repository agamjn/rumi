# Rumi Development Guidelines

This document contains best practices and guidelines for developing Rumi.

## Table of Contents
- [Letta Custom Tools](#letta-custom-tools)
- [Code Style](#code-style)
- [Testing](#testing)

---

## Letta Custom Tools

### NEVER Add Imports Inside Functions

**IMPORTANT RULE**: Never add `import` statements inside function definitions.

❌ **WRONG** (Bad Pattern):
```python
def my_tool(query: str) -> str:
    """A custom tool."""
    # DO NOT DO THIS!
    import sys
    sys.path.append('/some/path')
    from src.storage.client import Client

    # ... tool code
```

✅ **CORRECT** (Good Pattern):
```python
from src.storage.client import Client

def my_tool(query: str) -> str:
    """A custom tool."""
    # ... tool code
```

**Why?**
- Letta needs to parse function signatures to generate OpenAI tool schemas
- Imports inside functions prevent proper schema generation
- Without proper schema, the LLM cannot see or use the tool
- Tools will appear registered but won't be callable

### Use BaseTool with Pydantic Models

Always follow the official Letta documentation pattern for creating custom tools.

✅ **Correct Pattern**:

```python
from typing import Optional, List, Type
from pydantic import BaseModel, Field
from letta_client.client import BaseTool

# 1. Define Pydantic model for arguments
class MyToolArgs(BaseModel):
    query: str = Field(
        ...,
        description="The search query"
    )
    limit: int = Field(
        5,
        description="Maximum number of results"
    )

# 2. Extend BaseTool
class MyCustomTool(BaseTool):
    name: str = "my_custom_tool"
    args_schema: Type[BaseModel] = MyToolArgs
    description: str = "Description of what this tool does"
    tags: List[str] = ["category", "search"]

    def run(self, query: str, limit: int = 5) -> str:
        # Tool implementation here
        return result

# 3. Register with Letta
tool = client.tools.add(tool=MyCustomTool())
```

### All Imports at Top of File

All imports must be at the top of the file:

```python
# Standard library
from typing import Optional, List, Type
import logging

# Third-party
from pydantic import BaseModel, Field
from letta_client.client import BaseTool

# Local imports
from src.storage.qdrant_client import RumiQdrantClient
from src.storage.embeddings import EmbeddingGenerator

# Then define your tool classes...
```

---

## Code Style

### Import Order
1. Standard library imports
2. Third-party imports
3. Local application imports

### Type Hints
Always use type hints for function parameters and return values:

```python
def process_query(query: str, limit: int = 5) -> List[Dict[str, Any]]:
    pass
```

### Docstrings
Use Google-style docstrings for all functions and classes:

```python
def my_function(param1: str, param2: int) -> str:
    """
    Brief description of the function.

    Args:
        param1: Description of param1
        param2: Description of param2

    Returns:
        Description of return value
    """
    pass
```

---

## Testing

### Test Tool Implementations Directly

Before registering tools with Letta, test them directly:

```python
# scripts/test_tools_directly.py
from src.agents.tools import SearchBlogPostsTool

tool = SearchBlogPostsTool()
result = tool.run(query="test query", limit=3)
print(result)
```

### Test Tools with Letta Agent

After registration, test with actual agent:

```python
# scripts/test_rumi_blog_search.py
from src.agents.letta_client import RumiLettaClient

client = RumiLettaClient()
# ... test agent responses
```

---

## Common Mistakes to Avoid

1. ❌ Adding imports inside functions
2. ❌ Using plain functions instead of BaseTool classes
3. ❌ Not providing Pydantic schema for tool arguments
4. ❌ Forgetting to register tools with Letta server
5. ❌ Not attaching tools to the agent after registration
6. ❌ Assuming tools work without testing them directly first

---

## Architecture Overview

```
Rumi Architecture:
├── src/
│   ├── agents/
│   │   ├── letta_client.py    # LLM-agnostic Letta client
│   │   └── tools.py            # Custom BaseTool implementations
│   ├── storage/
│   │   ├── qdrant_client.py    # Qdrant vector DB client
│   │   └── embeddings.py       # OpenAI embeddings
│   └── ingestion/
│       └── blog_ingestion.py   # Blog post scraping & ingestion
└── scripts/
    ├── register_tools_with_letta.py  # Register & attach tools
    └── chat_with_rumi.py              # Interactive chat interface
```

### Data Flow

1. **Ingestion**: Blog posts → Scraped → Chunked → Embedded → Qdrant
2. **Tool Creation**: BaseTool classes with Pydantic schemas
3. **Tool Registration**: Tools → Letta server (creates OpenAI schema)
4. **Tool Attachment**: Tools → Rumi agent (makes available to LLM)
5. **Query**: User → Rumi → LLM decides to call tool → Tool executes → Results

---

## References

- [Letta Documentation - Custom Tools](https://docs.letta.com/guides/agents/custom-tools)
- [Pydantic Documentation](https://docs.pydantic.dev/)
- [Google Python Style Guide](https://google.github.io/styleguide/pyguide.html)
