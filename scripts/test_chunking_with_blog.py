"""
Test chunking and embedding with real blog posts.

This script demonstrates the full chunking + embedding workflow:
1. Fetches real blog posts
2. Chunks them if needed (>6000 tokens)
3. Generates embeddings for each chunk
4. Shows how retrieval would work
"""

from src.ingestion.blog import fetch_blog_posts
from src.storage.embeddings import EmbeddingGenerator
import logging

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)


def main():
    """Test chunking with real blog posts."""

    logger.info("=" * 70)
    logger.info("TESTING: Full Content Embedding with Smart Chunking")
    logger.info("=" * 70)

    # Step 1: Fetch blog posts
    logger.info("\n1. Fetching blog posts...")
    rss_url = "https://agamjn.com/feed"
    posts = fetch_blog_posts(rss_url)[:3]  # Test with first 3

    logger.info(f"   ✓ Fetched {len(posts)} posts\n")

    # Step 2: Initialize embedding generator
    generator = EmbeddingGenerator()

    # Step 3: Process each post
    all_chunks = []
    total_cost = 0

    for i, post in enumerate(posts, 1):
        logger.info(f"\n{'='*70}")
        logger.info(f"POST {i}: {post['title']}")
        logger.info(f"{'='*70}")

        # Prepare full text (title + content)
        full_text = f"Title: {post['title']}\n\nContent: {post['content']}"

        # Count tokens
        token_count = generator.count_tokens(full_text)
        logger.info(f"Full text: {len(full_text)} chars, {token_count} tokens")

        # Check if chunking needed
        if token_count > 6000:
            logger.info(f"⚠️  Needs chunking (>{6000} tokens limit)")
        else:
            logger.info(f"✓ Fits in single chunk (<{6000} tokens)")

        # Generate embeddings with chunking
        doc_id = f"blog:{post['url'].split('/')[-1]}"
        metadata = {
            "title": post['title'],
            "url": post['url'],
            "published": post['published']
        }

        chunks = generator.embed_document_with_chunking(
            text=full_text,
            doc_id=doc_id,
            metadata=metadata
        )

        # Display chunk info
        logger.info(f"\nChunks created: {len(chunks)}")
        for chunk in chunks:
            logger.info(
                f"  • Chunk {chunk['chunk_index']}: "
                f"{chunk['tokens']} tokens, "
                f"ID={chunk['chunk_id']}"
            )
            logger.info(f"    Preview: {chunk['text'][:100]}...")

        all_chunks.extend(chunks)
        cost = generator.estimate_cost(sum(c['tokens'] for c in chunks))
        total_cost += cost

    # Step 4: Summary
    logger.info(f"\n{'='*70}")
    logger.info("📊 SUMMARY")
    logger.info(f"{'='*70}")
    logger.info(f"Posts processed: {len(posts)}")
    logger.info(f"Total chunks created: {len(all_chunks)}")
    logger.info(f"Total tokens: {sum(c['tokens'] for c in all_chunks)}")
    logger.info(f"Total cost: ${total_cost:.6f}")

    # Estimate for full blog
    avg_cost_per_post = total_cost / len(posts)
    logger.info(f"\nEstimate for 100 posts: ${avg_cost_per_post * 100:.4f}")

    # Chunking stats
    multi_chunk_posts = sum(1 for p in posts if any(
        c['total_chunks'] > 1 for c in all_chunks if c['parent_id'].endswith(p['url'].split('/')[-1])
    ))

    logger.info(f"\nChunking stats:")
    logger.info(f"  Single-chunk posts: {len(posts) - multi_chunk_posts}")
    logger.info(f"  Multi-chunk posts: {multi_chunk_posts}")
    logger.info(f"  Avg chunks per post: {len(all_chunks) / len(posts):.1f}")

    # Example retrieval scenario
    logger.info(f"\n{'='*70}")
    logger.info("🔍 HOW RETRIEVAL WORKS")
    logger.info(f"{'='*70}")
    logger.info("Example query: 'What was the teaching in detachment blog?'")
    logger.info("\n1. Query gets embedded → vector")
    logger.info("2. Qdrant finds most similar chunks:")

    # Show what chunks would be stored
    detachment_chunks = [
        c for c in all_chunks
        if 'detachment' in c['metadata'].get('title', '').lower()
    ]

    if detachment_chunks:
        logger.info(f"\n   Detachment blog has {len(detachment_chunks)} chunk(s):")
        for chunk in detachment_chunks:
            logger.info(f"   • {chunk['chunk_id']}")
            logger.info(f"     Text preview: {chunk['text'][:150]}...")

        logger.info("\n3. Letta receives relevant chunks with full text")
        logger.info("4. Letta can answer: 'The teaching is...' (from actual content!)")
    else:
        logger.info("   (Detachment blog not in test set)")

    logger.info(f"\n✓ Ready for Task 3.3 (Qdrant integration)!")


if __name__ == "__main__":
    main()
