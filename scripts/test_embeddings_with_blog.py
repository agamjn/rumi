"""
Test embedding generation with real blog posts.

This script:
1. Fetches 3 blog posts from your RSS feed
2. Generates embeddings for each
3. Shows token counts and costs
4. Demonstrates similarity between posts
"""

import sys
from src.ingestion.blog import fetch_blog_posts
from src.storage.embeddings import EmbeddingGenerator
from src.config.settings import settings
import logging
import numpy as np

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)


def cosine_similarity(vec1, vec2):
    """Calculate cosine similarity between two vectors."""
    vec1 = np.array(vec1)
    vec2 = np.array(vec2)
    return np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))


def main():
    """Test embeddings with real blog posts."""

    # Step 1: Fetch blog posts
    logger.info("1. Fetching blog posts...")
    rss_url = "https://agamjn.com/feed"  # Your blog RSS
    posts = fetch_blog_posts(rss_url)

    if not posts:
        logger.error("No posts fetched!")
        return

    # Use first 3 posts for testing
    test_posts = posts[:3]
    logger.info(f"   ✓ Fetched {len(test_posts)} posts for testing")

    for i, post in enumerate(test_posts, 1):
        logger.info(f"   Post {i}: {post['title'][:60]}...")

    # Step 2: Generate embeddings
    logger.info("\n2. Generating embeddings...")
    generator = EmbeddingGenerator()

    embeddings = []
    total_tokens = 0
    total_cost = 0

    for i, post in enumerate(test_posts, 1):
        logger.info(f"\n   Post {i}: {post['title']}")

        # Combine title + summary for embedding (saves tokens vs full content)
        text_to_embed = f"{post['title']} {post['summary']}"

        # Generate embedding with metadata
        result = generator.generate_with_metadata(text_to_embed)
        embeddings.append(result['embedding'])

        total_tokens += result['token_count']
        total_cost += result['cost_usd']

        logger.info(f"      Tokens: {result['token_count']}")
        logger.info(f"      Cost: ${result['cost_usd']:.8f}")
        logger.info(f"      First 3 values: {result['embedding'][:3]}")

    # Step 3: Calculate similarities
    logger.info("\n3. Calculating semantic similarities...")
    logger.info("   (Higher score = more similar topics)\n")

    for i in range(len(test_posts)):
        for j in range(i + 1, len(test_posts)):
            similarity = cosine_similarity(embeddings[i], embeddings[j])
            logger.info(f"   Post {i+1} ↔ Post {j+1}: {similarity:.4f}")
            logger.info(f"      '{test_posts[i]['title'][:40]}...'")
            logger.info(f"      vs")
            logger.info(f"      '{test_posts[j]['title'][:40]}...'\n")

    # Step 4: Summary
    logger.info("=" * 70)
    logger.info("📊 SUMMARY")
    logger.info("=" * 70)
    logger.info(f"Posts processed: {len(test_posts)}")
    logger.info(f"Total tokens: {total_tokens}")
    logger.info(f"Total cost: ${total_cost:.8f}")
    logger.info(f"Cost per post: ${total_cost / len(test_posts):.8f}")
    logger.info(f"\nEstimate for 100 posts: ${(total_cost / len(test_posts)) * 100:.6f}")
    logger.info("\n✓ Ready to integrate with Qdrant!")
    logger.info("  Next: Store these embeddings in vector database")


if __name__ == "__main__":
    main()
