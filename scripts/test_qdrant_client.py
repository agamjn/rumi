"""Test the Qdrant client with deduplication."""
import numpy as np
import logging
import sys

from src.storage.qdrant_client import RumiQdrantClient

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_deduplication():
    """Test that deduplication works (Layer 1 + Layer 2)."""

    client = RumiQdrantClient()

    # Create collection
    logger.info("\n" + "="*70)
    logger.info("STEP 1: Create collection")
    logger.info("="*70)
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

    # Step 1: First upsert
    logger.info("\n" + "="*70)
    logger.info("STEP 2: First upsert")
    logger.info("="*70)
    client.upsert_document(chunk_id, embedding1, metadata1)

    # Check stats (should be 1 document)
    stats = client.get_collection_stats()
    logger.info(f"   Points count: {stats.get('points_count')}")
    assert stats.get('points_count') == 1, "Should have 1 point after first upsert"

    # Step 2: Check existence (Layer 2 deduplication)
    logger.info("\n" + "="*70)
    logger.info("STEP 3: Check existence (Layer 2 deduplication)")
    logger.info("="*70)
    exists = client.point_exists(chunk_id)
    logger.info(f"   Document exists: {exists}")
    assert exists, "Document should exist"

    # Step 3: Second upsert with updated content (Layer 1 deduplication)
    logger.info("\n" + "="*70)
    logger.info("STEP 4: Second upsert with updated content (Layer 1 deduplication)")
    logger.info("="*70)
    metadata1["content"] = "Updated content - this should replace, not duplicate!"
    client.upsert_document(chunk_id, embedding1, metadata1)

    # Check stats again (should STILL be 1 document, not 2!)
    logger.info("\n" + "="*70)
    logger.info("STEP 5: Verify no duplicates")
    logger.info("="*70)
    stats = client.get_collection_stats()
    logger.info(f"   Points count: {stats.get('points_count')}")
    logger.info(f"   Expected: 1 (upsert should update, not create duplicate)")

    if stats.get('points_count') == 1:
        logger.info("   ✓ DEDUPLICATION WORKS! No duplicate created.")
    else:
        logger.error(f"   ✗ DEDUPLICATION FAILED! Found {stats.get('points_count')} documents instead of 1")
        sys.exit(1)

    # Step 4: Test search to verify updated content
    logger.info("\n" + "="*70)
    logger.info("STEP 6: Search to verify content was updated")
    logger.info("="*70)
    results = client.search(
        query_vector=embedding1,
        limit=5,
        category="work"
    )
    logger.info(f"   Found {len(results)} results")
    if results:
        logger.info(f"   Title: {results[0]['metadata']['title']}")
        logger.info(f"   Content: {results[0]['metadata']['content']}")
        logger.info(f"   Chunk ID: {results[0]['metadata']['chunk_id']}")

        # Verify content was updated
        assert results[0]['metadata']['content'] == "Updated content - this should replace, not duplicate!", \
            "Content should be updated"
        logger.info("   ✓ Content was successfully updated (not duplicated)")

    # Step 5: Test with different chunk from same document
    logger.info("\n" + "="*70)
    logger.info("STEP 7: Add different chunk from same document")
    logger.info("="*70)
    chunk_id_2 = "test:post_1:chunk_1"
    embedding2 = np.random.rand(1536).tolist()
    metadata2 = {
        "title": "Test Post",
        "category": "work",
        "tags": ["test", "demo"],
        "content": "This is chunk 1 content",
        "source": "blog"
    }
    client.upsert_document(chunk_id_2, embedding2, metadata2)

    stats = client.get_collection_stats()
    logger.info(f"   Points count: {stats.get('points_count')}")
    logger.info(f"   Expected: 2 (different chunk IDs)")
    assert stats.get('points_count') == 2, "Should have 2 points for different chunk IDs"

    # Final summary
    logger.info("\n" + "="*70)
    logger.info("✓ ALL DEDUPLICATION TESTS PASSED!")
    logger.info("="*70)
    logger.info("Deduplication Strategy Verified:")
    logger.info("  ✓ Layer 1: upsert() prevents duplicates in Qdrant")
    logger.info("  ✓ Layer 2: point_exists() can check before embedding")
    logger.info("  ✓ Same chunk_id → update, not duplicate")
    logger.info("  ✓ Different chunk_id → separate documents")
    logger.info("")
    logger.info("Ready for Task 3.4: Blog to Qdrant Pipeline!")


if __name__ == "__main__":
    test_deduplication()
