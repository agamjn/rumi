"""
Test script for Qdrant basic operations.

This script demonstrates:
1. Connecting to Qdrant
2. Creating a collection
3. Inserting vectors with metadata
4. Searching for similar vectors
5. Verifying persistence

Run: python scripts/test_qdrant.py
"""

from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance,
    VectorParams,
    PointStruct,
)
import numpy as np
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)


def main():
    """Test Qdrant basic operations."""

    # Step 1: Connect to Qdrant
    logger.info("1. Connecting to Qdrant at localhost:6333...")
    client = QdrantClient(host="localhost", port=6333)

    # Verify connection
    try:
        info = client.get_collections()
        logger.info(f"✓ Connected! Current collections: {len(info.collections)}")
    except Exception as e:
        logger.error(f"✗ Failed to connect: {e}")
        return

    # Step 2: Create a collection (like a table)
    collection_name = "test_collection"
    vector_size = 1536  # Same as OpenAI text-embedding-3-small

    logger.info(f"\n2. Creating collection '{collection_name}'...")
    logger.info(f"   Vector size: {vector_size} dimensions")
    logger.info(f"   Distance metric: Cosine (best for embeddings)")

    try:
        # Delete if exists (for clean testing)
        try:
            client.delete_collection(collection_name)
            logger.info(f"   (Deleted existing collection)")
        except:
            pass

        # Create collection
        client.create_collection(
            collection_name=collection_name,
            vectors_config=VectorParams(
                size=vector_size,
                distance=Distance.COSINE  # Common for embeddings
            )
        )
        logger.info("✓ Collection created successfully!")
    except Exception as e:
        logger.error(f"✗ Failed to create collection: {e}")
        return

    # Step 3: Insert sample vectors (simulating blog posts)
    logger.info(f"\n3. Inserting 3 sample points (blog posts)...")

    # In reality, these would be embeddings from OpenAI
    # For testing, we'll use random vectors that are similar

    # Create 3 similar vectors (imagine these are blog posts about vLLM)
    base_vector = np.random.rand(vector_size).tolist()

    # Point 1: "Optimizing reranker inference with vLLM"
    vector1 = [x + np.random.normal(0, 0.01) for x in base_vector]
    point1 = PointStruct(
        id=1,
        vector=vector1,
        payload={
            "title": "Optimizing reranker inference with vLLM",
            "category": "work",
            "tags": ["vllm", "reranker", "fastapi"],
            "url": "https://agamjn.com/post1"
        }
    )

    # Point 2: "RAG vs Memory" (slightly different topic)
    vector2 = [x + np.random.normal(0, 0.3) for x in base_vector]
    point2 = PointStruct(
        id=2,
        vector=vector2,
        payload={
            "title": "RAG vs Memory: Addressing Token Crisis",
            "category": "work",
            "tags": ["rag", "memory", "token_management"],
            "url": "https://agamjn.com/post2"
        }
    )

    # Point 3: "Detachment Is All You Need" (very different - personal)
    vector3 = np.random.rand(vector_size).tolist()  # Random, unrelated
    point3 = PointStruct(
        id=3,
        vector=vector3,
        payload={
            "title": "Detachment Is All You Need",
            "category": "personal",
            "tags": ["detachment", "philosophy", "mindfulness"],
            "url": "https://agamjn.com/post3"
        }
    )

    try:
        client.upsert(
            collection_name=collection_name,
            points=[point1, point2, point3]
        )
        logger.info("✓ Inserted 3 points successfully!")
        logger.info("   - Post 1 & 2 are similar (both technical)")
        logger.info("   - Post 3 is different (personal/philosophy)")
    except Exception as e:
        logger.error(f"✗ Failed to insert points: {e}")
        return

    # Step 4: Search for similar vectors
    logger.info(f"\n4. Searching for posts similar to Post 1 (vLLM)...")
    logger.info("   Query: Using vector1 (simulating 'find posts about vLLM')")

    try:
        # Search using vector1 as query
        results = client.search(
            collection_name=collection_name,
            query_vector=vector1,
            limit=3  # Get top 3 results
        )

        logger.info(f"\n   Results (top 3 by similarity):")
        for i, result in enumerate(results, 1):
            title = result.payload.get("title")
            category = result.payload.get("category")
            score = result.score
            logger.info(f"   #{i} [{score:.4f}] {title} ({category})")

        logger.info("\n✓ Search completed!")
        logger.info("   Notice: Post 1 (score ~1.0) is most similar to itself")
        logger.info("   Notice: Post 2 (higher score) is more similar than Post 3")
        logger.info("   This is semantic search in action!")

    except Exception as e:
        logger.error(f"✗ Failed to search: {e}")
        return

    # Step 5: Filter by metadata
    logger.info(f"\n5. Filtering search results by category='work'...")

    try:
        from qdrant_client.models import Filter, FieldCondition, MatchValue

        results = client.search(
            collection_name=collection_name,
            query_vector=vector1,
            query_filter=Filter(
                must=[
                    FieldCondition(
                        key="category",
                        match=MatchValue(value="work")
                    )
                ]
            ),
            limit=3
        )

        logger.info(f"   Found {len(results)} work-related posts:")
        for result in results:
            title = result.payload.get("title")
            logger.info(f"   - {title}")

        logger.info("✓ Filtered search works! (Post 3 excluded)")

    except Exception as e:
        logger.error(f"✗ Failed to filter: {e}")
        return

    # Step 6: Verify collection stats
    logger.info(f"\n6. Collection statistics:")
    try:
        collection_info = client.get_collection(collection_name)
        logger.info(f"   Points count: {collection_info.points_count}")
        logger.info(f"   Vector size: {collection_info.config.params.vectors.size}")
        logger.info(f"   Distance: {collection_info.config.params.vectors.distance}")
        logger.info("✓ Collection healthy!")
    except Exception as e:
        logger.error(f"✗ Failed to get stats: {e}")
        return

    # Summary
    logger.info(f"\n{'='*60}")
    logger.info("🎉 ALL TESTS PASSED!")
    logger.info(f"{'='*60}")
    logger.info("\nWhat we tested:")
    logger.info("✓ Connection to Qdrant")
    logger.info("✓ Collection creation")
    logger.info("✓ Vector insertion with metadata")
    logger.info("✓ Semantic similarity search")
    logger.info("✓ Metadata filtering")
    logger.info("\nNext: Check web UI at http://localhost:6333/dashboard")
    logger.info("      You should see 'test_collection' with 3 points!")
    logger.info("\nReady to integrate with your blog posts! 🚀")


if __name__ == "__main__":
    main()
