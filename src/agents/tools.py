"""
Custom Letta tools for Rumi.

These tools give the Letta agent the ability to search and retrieve
content from Qdrant (blog posts, documents, etc.).

IMPORTANT: Tools must be self-contained as Letta executes them in a sandbox.
All imports and logic must be inside the run() method.
"""

from typing import Optional, List, Type
import logging
from pydantic import BaseModel, Field
from letta_client.client import BaseTool

logger = logging.getLogger(__name__)


# Pydantic models for tool arguments
class SearchBlogPostsArgs(BaseModel):
    query: str = Field(
        ...,
        description="What to search for (e.g., 'vLLM optimization', 'detachment philosophy')"
    )
    category: Optional[str] = Field(
        None,
        description="Optional filter - 'work' for technical posts, 'personal' for philosophy/life posts"
    )
    limit: int = Field(
        3,
        description="Maximum number of posts to return"
    )


class GetBlogPostContentArgs(BaseModel):
    title: str = Field(
        ...,
        description="Title of the blog post (exact or partial match)"
    )


class ListRecentPostsArgs(BaseModel):
    category: Optional[str] = Field(
        None,
        description="Optional filter - 'work' or 'personal'"
    )
    limit: int = Field(
        5,
        description="Number of posts to list"
    )


# Tool implementations using BaseTool
class SearchBlogPostsTool(BaseTool):
    name: str = "search_blog_posts"
    args_schema: Type[BaseModel] = SearchBlogPostsArgs
    description: str = (
        "Search Agam's blog posts for relevant content using semantic search. "
        "Use this when the user asks about topics, concepts, or specific content "
        "from Agam's blog. Returns the most relevant posts with summaries."
    )
    tags: List[str] = ["blog", "search", "qdrant"]

    def run(self, query: str, category: Optional[str] = None, limit: int = 3) -> str:
        """Self-contained search - all logic inline for Letta sandbox."""
        import os
        from qdrant_client import QdrantClient
        from openai import OpenAI

        try:
            # Connect to Qdrant
            qdrant_host = os.getenv('QDRANT_HOST', 'localhost')
            qdrant_port = int(os.getenv('QDRANT_PORT', '6333'))
            qdrant = QdrantClient(host=qdrant_host, port=qdrant_port)

            # Connect to OpenAI for embeddings
            openai_client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
            embedding_model = os.getenv('OPENAI_EMBEDDING_MODEL', 'text-embedding-3-small')

            # Generate embedding
            response = openai_client.embeddings.create(input=query, model=embedding_model)
            query_embedding = response.data[0].embedding

            # Build filter
            must_conditions = []
            if category:
                must_conditions.append({
                    "key": "category",
                    "match": {"value": category}
                })

            query_filter = {"must": must_conditions} if must_conditions else None

            # Search Qdrant
            search_results = qdrant.search(
                collection_name="rumi_content",
                query_vector=query_embedding,
                limit=limit,
                query_filter=query_filter
            )

            if not search_results:
                return f"No blog posts found matching '{query}'."

            # Format results
            output = f"Found {len(search_results)} relevant blog post(s):\n\n"

            for i, hit in enumerate(search_results, 1):
                metadata = hit.payload
                score = hit.score

                output += f"{i}. **{metadata['title']}** (Relevance: {score:.2f})\n"
                output += f"   Category: {metadata['category']}\n"
                output += f"   Summary: {metadata['summary']}\n"
                output += f"   Tags: {', '.join(metadata['tags'][:5])}\n"
                output += f"   URL: {metadata['url']}\n"
                output += f"   Published: {metadata['published']}\n"
                output += "\n"

            return output

        except Exception as e:
            import traceback
            return f"Error searching blog posts: {str(e)}\n{traceback.format_exc()}"


class GetBlogPostContentTool(BaseTool):
    name: str = "get_blog_post_content"
    args_schema: Type[BaseModel] = GetBlogPostContentArgs
    description: str = (
        "Get the full content of a specific blog post by title. "
        "Use this when you need more detail about a specific post."
    )
    tags: List[str] = ["blog", "content", "qdrant"]

    def run(self, title: str) -> str:
        """Self-contained blog post retrieval."""
        import os
        from qdrant_client import QdrantClient
        from openai import OpenAI

        try:
            # Connect to Qdrant
            qdrant_host = os.getenv('QDRANT_HOST', 'localhost')
            qdrant_port = int(os.getenv('QDRANT_PORT', '6333'))
            qdrant = QdrantClient(host=qdrant_host, port=qdrant_port)

            # Connect to OpenAI for embeddings
            openai_client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
            embedding_model = os.getenv('OPENAI_EMBEDDING_MODEL', 'text-embedding-3-small')

            # Generate embedding for title search
            response = openai_client.embeddings.create(input=title, model=embedding_model)
            query_embedding = response.data[0].embedding

            # Search Qdrant
            search_results = qdrant.search(
                collection_name="rumi_content",
                query_vector=query_embedding,
                limit=1
            )

            if not search_results:
                return f"Blog post not found: '{title}'"

            # Get the best match
            hit = search_results[0]
            metadata = hit.payload

            # Format output
            output = f"**{metadata['title']}**\n\n"
            output += f"Summary: {metadata['summary']}\n\n"
            output += f"Category: {metadata['category']}\n"
            output += f"Tags: {', '.join(metadata['tags'])}\n"
            output += f"URL: {metadata['url']}\n\n"
            output += "Note: For full content, please visit the URL above.\n"

            return output

        except Exception as e:
            import traceback
            return f"Error getting blog post content: {str(e)}\n{traceback.format_exc()}"


class ListRecentPostsTool(BaseTool):
    name: str = "list_recent_posts"
    args_schema: Type[BaseModel] = ListRecentPostsArgs
    description: str = (
        "List Agam's most recent blog posts. "
        "Use this to give an overview or when the user asks what they've written about."
    )
    tags: List[str] = ["blog", "list", "qdrant"]

    def run(self, category: Optional[str] = None, limit: int = 5) -> str:
        """Self-contained list recent posts."""
        import os
        from qdrant_client import QdrantClient
        from openai import OpenAI

        try:
            # Connect to Qdrant
            qdrant_host = os.getenv('QDRANT_HOST', 'localhost')
            qdrant_port = int(os.getenv('QDRANT_PORT', '6333'))
            qdrant = QdrantClient(host=qdrant_host, port=qdrant_port)

            # Connect to OpenAI for embeddings
            openai_client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
            embedding_model = os.getenv('OPENAI_EMBEDDING_MODEL', 'text-embedding-3-small')

            # Use a broad query to get diverse results
            query = "blog posts" if not category else f"{category} blog posts"
            response = openai_client.embeddings.create(input=query, model=embedding_model)
            query_embedding = response.data[0].embedding

            # Build filter
            must_conditions = []
            if category:
                must_conditions.append({
                    "key": "category",
                    "match": {"value": category}
                })

            query_filter = {"must": must_conditions} if must_conditions else None

            # Search Qdrant
            search_results = qdrant.search(
                collection_name="rumi_content",
                query_vector=query_embedding,
                limit=limit,
                query_filter=query_filter
            )

            if not search_results:
                return "No blog posts found."

            # Format results
            category_text = f"{category}-related " if category else ""
            output = f"Recent {category_text}blog posts:\n\n"

            for i, hit in enumerate(search_results, 1):
                metadata = hit.payload
                output += f"{i}. {metadata['title']} ({metadata['published'][:10]})\n"
                output += f"   Summary: {metadata['summary']}\n"
                output += f"   Tags: {', '.join(metadata['tags'][:3])}\n\n"

            return output

        except Exception as e:
            import traceback
            return f"Error listing posts: {str(e)}\n{traceback.format_exc()}"
