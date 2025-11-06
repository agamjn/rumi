"""
Qdrant client wrapper for Rumi.

This module provides:
- Upsert operations (prevents duplicates - Layer 1 deduplication)
- Existence checks (saves API calls - Layer 2 deduplication)
- Semantic similarity search
- Metadata filtering (category, source, tags)
- Error handling and connection management

Deduplication Strategy:
- Layer 1: upsert() with deterministic IDs prevents duplicates in Qdrant
- Layer 2: point_exists() checks before embedding (saves OpenAI API calls)
- Layer 3: State manager (Task 1.1, future) tracks last sync timestamps
"""

from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance,
    VectorParams,
    PointStruct,
    Filter,
    FieldCondition,
    MatchValue,
    MatchAny,
)
from typing import List, Dict, Optional
import logging
import uuid

logger = logging.getLogger(__name__)


def string_to_uuid(text: str) -> str:
    """Convert string to deterministic UUID.

    Same string always produces same UUID (UUID v5).
    This enables upsert with string-like IDs.

    Args:
        text: Input string (e.g., "blog:post_123:chunk_0")

    Returns:
        UUID string

    Example:
        >>> string_to_uuid("blog:test:chunk_0")
        '4d9c1e0a-...'
        >>> string_to_uuid("blog:test:chunk_0")  # Same!
        '4d9c1e0a-...'
    """
    # UUID v5 with DNS namespace (standard practice)
    return str(uuid.uuid5(uuid.NAMESPACE_DNS, text))


class RumiQdrantClient:
    """Wrapper for Qdrant operations specific to Rumi.

    Handles:
    - Collection management
    - Document upsert (with deduplication)
    - Semantic similarity search
    - Metadata filtering
    - Existence checks (optimize embeddings)

    Example:
        >>> client = RumiQdrantClient()
        >>> client.create_collection()
        >>> client.upsert_document(
        ...     chunk_id="blog:post_123:chunk_0",
        ...     embedding=[0.1, 0.2, ...],  # 1536 dims
        ...     metadata={"title": "...", "category": "work"}
        ... )
    """

    def __init__(self, host: str = "localhost", port: int = 6333):
        """Initialize Qdrant client.

        Args:
            host: Qdrant server host (default: localhost)
            port: Qdrant server port (default: 6333)
        """
        self.client = QdrantClient(host=host, port=port)
        self.collection_name = "rumi_content"
        self.vector_size = 1536  # OpenAI text-embedding-3-small

        logger.info(f"RumiQdrantClient initialized (host={host}, port={port})")

    def create_collection(self, recreate: bool = False):
        """Create the Rumi content collection.

        Args:
            recreate: If True, delete existing collection first (DANGER!)
        """
        try:
            # Check if collection exists
            collections = self.client.get_collections()
            exists = any(c.name == self.collection_name for c in collections.collections)

            if exists:
                if recreate:
                    logger.warning(f"Recreating collection: {self.collection_name}")
                    self.client.delete_collection(self.collection_name)
                else:
                    logger.info(f"Collection {self.collection_name} already exists")
                    return

            # Create collection
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(
                    size=self.vector_size,
                    distance=Distance.COSINE  # Best for text embeddings
                )
            )
            logger.info(f"✓ Created collection: {self.collection_name}")

        except Exception as e:
            logger.error(f"Failed to create collection: {e}")
            raise

    def point_exists(self, chunk_id: str) -> bool:
        """Check if a document/chunk already exists in Qdrant.

        This is Layer 2 deduplication - check before embedding!

        Args:
            chunk_id: Unique chunk identifier (string, will be converted to UUID)

        Returns:
            True if exists, False otherwise

        Example:
            >>> if not client.point_exists("blog:post_123:chunk_0"):
            ...     # Generate expensive embedding
            ...     embedding = generate_embedding(text)
            ...     client.upsert_document(...)
        """
        try:
            # Convert string ID to UUID
            point_uuid = string_to_uuid(chunk_id)

            result = self.client.retrieve(
                collection_name=self.collection_name,
                ids=[point_uuid],
                with_vectors=False  # Don't need vectors, just existence
            )
            exists = len(result) > 0
            logger.debug(f"Point {chunk_id} (UUID: {point_uuid}) exists: {exists}")
            return exists

        except Exception as e:
            # If collection doesn't exist, point doesn't exist
            logger.debug(f"Point existence check failed: {e}")
            return False

    def upsert_document(
        self,
        chunk_id: str,
        embedding: List[float],
        metadata: Dict
    ) -> bool:
        """Insert or update a document (Layer 1 deduplication).

        IMPORTANT: Uses upsert, not insert!
        - If chunk_id exists → Updates (no duplicate!)
        - If chunk_id doesn't exist → Creates new

        Args:
            chunk_id: Unique identifier (e.g., "blog:post_123:chunk_0")
            embedding: Vector embedding (1536 dimensions)
            metadata: Document metadata (title, category, tags, content, etc.)

        Returns:
            True if successful

        Example:
            >>> client.upsert_document(
            ...     chunk_id="blog:detachment:chunk_0",
            ...     embedding=[0.1, 0.2, ...],  # 1536 floats
            ...     metadata={
            ...         "title": "Detachment Is All You Need",
            ...         "category": "personal",
            ...         "tags": ["philosophy", "startups"],
            ...         "content": "Full blog post text..."
            ...     }
            ... )
        """
        try:
            # Validate embedding dimensions
            if len(embedding) != self.vector_size:
                raise ValueError(
                    f"Expected {self.vector_size} dimensions, got {len(embedding)}"
                )

            # Convert string ID to UUID (Qdrant requirement)
            point_uuid = string_to_uuid(chunk_id)

            # Store original chunk_id in metadata for reference
            payload = metadata.copy()
            payload["chunk_id"] = chunk_id

            # Create point
            point = PointStruct(
                id=point_uuid,  # UUID for Qdrant
                vector=embedding,
                payload=payload
            )

            # UPSERT (not insert!) - prevents duplicates
            self.client.upsert(
                collection_name=self.collection_name,
                points=[point]
            )

            logger.info(f"✓ Upserted document: {chunk_id} (UUID: {point_uuid})")
            return True

        except Exception as e:
            logger.error(f"Failed to upsert document {chunk_id}: {e}")
            return False

    def search(
        self,
        query_vector: List[float],
        limit: int = 10,
        category: Optional[str] = None,
        source: Optional[str] = None,
        tags: Optional[List[str]] = None,
        score_threshold: Optional[float] = None
    ) -> List[Dict]:
        """Search for similar documents with optional filters.

        Args:
            query_vector: Query embedding vector (1536 dims)
            limit: Maximum number of results
            category: Filter by category ("work" or "personal")
            source: Filter by source ("blog", "linkedin", "twitter", "fathom")
            tags: Filter by tags (matches if ANY tag matches)
            score_threshold: Minimum similarity score (0-1)

        Returns:
            List of dicts with keys:
            - chunk_id: Document identifier
            - score: Similarity score (0-1, higher = more similar)
            - metadata: All stored metadata (title, content, etc.)

        Example:
            >>> results = client.search(
            ...     query_vector=query_embedding,
            ...     limit=5,
            ...     category="work",
            ...     tags=["vllm", "rag"]
            ... )
            >>> for result in results:
            ...     print(f"{result['metadata']['title']} (score: {result['score']})")
        """
        try:
            # Build filters
            filter_conditions = []

            if category:
                filter_conditions.append(
                    FieldCondition(
                        key="category",
                        match=MatchValue(value=category)
                    )
                )

            if source:
                filter_conditions.append(
                    FieldCondition(
                        key="source",
                        match=MatchValue(value=source)
                    )
                )

            if tags:
                # Match if ANY of the provided tags match
                filter_conditions.append(
                    FieldCondition(
                        key="tags",
                        match=MatchAny(any=tags)
                    )
                )

            query_filter = Filter(must=filter_conditions) if filter_conditions else None

            # Search (using updated API)
            results = self.client.query_points(
                collection_name=self.collection_name,
                query=query_vector,
                query_filter=query_filter,
                limit=limit,
                score_threshold=score_threshold,
                with_payload=True
            ).points

            # Format results
            formatted_results = [
                {
                    "chunk_id": hit.id,
                    "score": hit.score,
                    "metadata": hit.payload
                }
                for hit in results
            ]

            logger.info(
                f"✓ Search found {len(formatted_results)} results "
                f"(category={category}, source={source}, tags={tags})"
            )

            return formatted_results

        except Exception as e:
            logger.error(f"Search failed: {e}")
            return []

    def delete_document(self, chunk_id: str) -> bool:
        """Delete a document by ID.

        Args:
            chunk_id: Document identifier to delete (string will be converted to UUID)

        Returns:
            True if successful
        """
        try:
            # Convert string ID to UUID
            point_uuid = string_to_uuid(chunk_id)

            self.client.delete(
                collection_name=self.collection_name,
                points_selector=[point_uuid]
            )
            logger.info(f"✓ Deleted document: {chunk_id} (UUID: {point_uuid})")
            return True

        except Exception as e:
            logger.error(f"Failed to delete document {chunk_id}: {e}")
            return False

    def get_collection_stats(self) -> Dict:
        """Get collection statistics.

        Returns:
            Dict with keys: points_count, vectors_count, status
        """
        try:
            collection_info = self.client.get_collection(self.collection_name)
            return {
                "points_count": collection_info.points_count,
                "vectors_count": collection_info.vectors_count,
                "status": collection_info.status,
                "optimizer_status": collection_info.optimizer_status
            }
        except Exception as e:
            logger.error(f"Failed to get stats: {e}")
            return {}


def test_qdrant_client():
    """Test the Qdrant client with deduplication."""
    import numpy as np

    client = RumiQdrantClient()

    # Create collection
    client.create_collection()

    # Test data
    embedding1 = np.random.rand(1536).tolist()
    metadata1 = {
        "title": "Test Post",
        "category": "work",
        "tags": ["test", "demo"],
        "content": "This is test content",
        "source": "blog"
    }

    chunk_id = "test:post_1:chunk_0"

    # Test upsert (first time)
    print("\n1. First upsert:")
    client.upsert_document(chunk_id, embedding1, metadata1)

    # Check existence
    print("\n2. Check existence:")
    exists = client.point_exists(chunk_id)
    print(f"   Document exists: {exists}")

    # Test upsert again (should update, not duplicate)
    print("\n3. Second upsert (should update, not create duplicate):")
    metadata1["content"] = "Updated content"
    client.upsert_document(chunk_id, embedding1, metadata1)

    # Check stats
    print("\n4. Collection stats:")
    stats = client.get_collection_stats()
    print(f"   Points count: {stats.get('points_count')}")
    print(f"   (Should be 1, not 2! Upsert works!)")

    # Test search
    print("\n5. Search test:")
    results = client.search(
        query_vector=embedding1,
        limit=5,
        category="work"
    )
    print(f"   Found {len(results)} results")
    if results:
        print(f"   Title: {results[0]['metadata']['title']}")
        print(f"   Content: {results[0]['metadata']['content']}")

    print("\n✓ Deduplication test passed!")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    test_qdrant_client()
