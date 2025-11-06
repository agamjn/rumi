"""
Full pipeline: Blog RSS → Classification → Embedding → Qdrant Storage

This script demonstrates the complete ingestion workflow:
1. Fetch blog posts from RSS feed
2. Classify each post (category, tags, summary)
3. Check if already stored (Layer 2 deduplication)
4. Generate embeddings with automatic chunking
5. Upsert to Qdrant (Layer 1 deduplication)
6. Summary and visualization instructions

Run with: PYTHONPATH=/Users/agamjain/Downloads/rumi venv/bin/python scripts/sync_blog_to_qdrant.py
"""

from src.ingestion.blog import fetch_blog_posts
from src.processing.classifier import classify_content
from src.storage.embeddings import EmbeddingGenerator
from src.storage.qdrant_client import RumiQdrantClient
import logging
import sys
from datetime import datetime

logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s: %(message)s'
)
logger = logging.getLogger(__name__)


def sync_blog_to_qdrant(rss_url: str, limit: int = None):
    """Sync blog posts to Qdrant with deduplication.

    Args:
        rss_url: Blog RSS feed URL
        limit: Max number of posts to process (None = all)
    """

    logger.info("=" * 80)
    logger.info("BLOG TO QDRANT SYNC PIPELINE")
    logger.info("=" * 80)
    logger.info(f"RSS Feed: {rss_url}")
    logger.info(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("")

    # Initialize clients
    logger.info("Initializing clients...")
    qdrant_client = RumiQdrantClient()
    embedding_generator = EmbeddingGenerator()

    # Ensure collection exists
    logger.info("Setting up Qdrant collection...")
    qdrant_client.create_collection()

    # Get initial stats
    initial_stats = qdrant_client.get_collection_stats()
    initial_count = initial_stats.get('points_count', 0)
    logger.info(f"Initial document count: {initial_count}")
    logger.info("")

    # Fetch blog posts
    logger.info("=" * 80)
    logger.info("STEP 1: Fetching blog posts from RSS")
    logger.info("=" * 80)
    posts = fetch_blog_posts(rss_url)

    if limit:
        posts = posts[:limit]
        logger.info(f"Limited to {limit} posts")

    logger.info(f"✓ Fetched {len(posts)} posts")
    logger.info("")

    # Process each post
    stats = {
        'total_posts': len(posts),
        'skipped_existing': 0,
        'newly_embedded': 0,
        'total_chunks': 0,
        'total_tokens': 0,
        'total_cost': 0.0,
        'categories': {'work': 0, 'personal': 0},
        'errors': 0
    }

    processed_posts = []

    for i, post in enumerate(posts, 1):
        logger.info("=" * 80)
        logger.info(f"PROCESSING POST {i}/{len(posts)}")
        logger.info("=" * 80)
        logger.info(f"Title: {post['title']}")
        logger.info(f"URL: {post['url']}")
        logger.info(f"Published: {post['published']}")
        logger.info("")

        try:
            # Step 1: Classify the post
            logger.info("  → Classifying content...")
            classification = classify_content(
                content=post['content'],
                platform='blog',
                title=post['title'],
                date=post['published']
            )
            logger.info(f"     Category: {classification['category']}")
            logger.info(f"     Tags: {', '.join(classification['tags'])}")
            logger.info(f"     Summary: {classification['summary']}")

            stats['categories'][classification['category']] += 1

            # Step 2: Prepare document ID and metadata
            # Use URL slug as unique identifier
            url_slug = post['url'].split('/')[-1] if '/' in post['url'] else post['url']
            doc_id = f"blog:{url_slug}"

            logger.info(f"     Document ID: {doc_id}")

            # Prepare full text (title + content)
            full_text = f"Title: {post['title']}\n\nContent: {post['content']}"
            token_count = embedding_generator.count_tokens(full_text)
            logger.info(f"     Token count: {token_count}")

            # Step 3: Check if already exists (Layer 2 deduplication)
            logger.info("  → Checking if already stored...")
            chunk_id = f"{doc_id}:chunk_0"  # Check first chunk

            if qdrant_client.point_exists(chunk_id):
                logger.info("     ✓ Already exists - skipping (Layer 2 deduplication)")
                stats['skipped_existing'] += 1

                # Still track it for summary
                processed_posts.append({
                    'title': post['title'],
                    'url': post['url'],
                    'category': classification['category'],
                    'tags': classification['tags'],
                    'doc_id': doc_id,
                    'status': 'existing'
                })
                continue

            # Step 4: Generate embeddings with chunking
            logger.info("  → Generating embeddings...")

            metadata = {
                'title': post['title'],
                'url': post['url'],
                'published': post['published'],
                'category': classification['category'],
                'tags': classification['tags'],
                'summary': classification['summary'],
                'source': 'blog'
            }

            chunks = embedding_generator.embed_document_with_chunking(
                text=full_text,
                doc_id=doc_id,
                metadata=metadata
            )

            logger.info(f"     ✓ Created {len(chunks)} chunk(s)")

            # Step 5: Upsert to Qdrant (Layer 1 deduplication)
            logger.info("  → Storing in Qdrant...")

            for chunk in chunks:
                success = qdrant_client.upsert_document(
                    chunk_id=chunk['chunk_id'],
                    embedding=chunk['embedding'],
                    metadata=chunk['metadata']
                )

                if not success:
                    logger.error(f"     ✗ Failed to store chunk: {chunk['chunk_id']}")
                    stats['errors'] += 1

            # Update stats
            stats['newly_embedded'] += 1
            stats['total_chunks'] += len(chunks)
            stats['total_tokens'] += sum(c['tokens'] for c in chunks)

            chunk_cost = embedding_generator.estimate_cost(
                sum(c['tokens'] for c in chunks)
            )
            stats['total_cost'] += chunk_cost

            processed_posts.append({
                'title': post['title'],
                'url': post['url'],
                'category': classification['category'],
                'tags': classification['tags'],
                'doc_id': doc_id,
                'chunks': len(chunks),
                'tokens': sum(c['tokens'] for c in chunks),
                'cost': chunk_cost,
                'status': 'new'
            })

            logger.info(f"     ✓ Successfully stored!")
            logger.info("")

        except Exception as e:
            logger.error(f"     ✗ Error processing post: {e}")
            stats['errors'] += 1
            continue

    # Get final stats
    logger.info("=" * 80)
    logger.info("SYNC COMPLETE!")
    logger.info("=" * 80)
    logger.info("")

    final_stats = qdrant_client.get_collection_stats()
    final_count = final_stats.get('points_count', 0)

    logger.info("📊 SUMMARY")
    logger.info("=" * 80)
    logger.info(f"Total posts processed:     {stats['total_posts']}")
    logger.info(f"  • Newly embedded:        {stats['newly_embedded']}")
    logger.info(f"  • Skipped (existing):    {stats['skipped_existing']}")
    logger.info(f"  • Errors:                {stats['errors']}")
    logger.info("")
    logger.info(f"Categories:")
    logger.info(f"  • Work:                  {stats['categories']['work']}")
    logger.info(f"  • Personal:              {stats['categories']['personal']}")
    logger.info("")
    logger.info(f"Embedding Stats:")
    logger.info(f"  • Total chunks created:  {stats['total_chunks']}")
    logger.info(f"  • Total tokens:          {stats['total_tokens']:,}")
    logger.info(f"  • Total cost:            ${stats['total_cost']:.6f}")
    logger.info("")
    logger.info(f"Qdrant Collection:")
    logger.info(f"  • Before sync:           {initial_count} documents")
    logger.info(f"  • After sync:            {final_count} documents")
    logger.info(f"  • Added:                 {final_count - initial_count} documents")
    logger.info("")

    # Show some sample posts
    logger.info("=" * 80)
    logger.info("📄 STORED CONTENT SAMPLE")
    logger.info("=" * 80)

    for i, post_info in enumerate(processed_posts[:5], 1):
        logger.info(f"\n{i}. {post_info['title']}")
        logger.info(f"   Category: {post_info['category']}")
        logger.info(f"   Tags: {', '.join(post_info['tags'][:5])}")
        logger.info(f"   Doc ID: {post_info['doc_id']}")
        logger.info(f"   Status: {post_info['status']}")
        if post_info['status'] == 'new':
            logger.info(f"   Chunks: {post_info['chunks']}, Tokens: {post_info['tokens']}, Cost: ${post_info['cost']:.6f}")

    if len(processed_posts) > 5:
        logger.info(f"\n... and {len(processed_posts) - 5} more posts")

    # Visualization instructions
    logger.info("")
    logger.info("=" * 80)
    logger.info("🎨 QDRANT DASHBOARD VISUALIZATION")
    logger.info("=" * 80)
    logger.info("")
    logger.info("1. Open Qdrant Dashboard:")
    logger.info("   http://localhost:6333/dashboard")
    logger.info("")
    logger.info("2. View Collection:")
    logger.info("   • Click on 'rumi_content' collection")
    logger.info("   • You should see all stored documents")
    logger.info("")
    logger.info("3. Explore a Document:")
    logger.info("   • Click on any point ID")
    logger.info("   • View the vector (1536 dimensions)")
    logger.info("   • Check payload/metadata:")
    logger.info("     - title, url, published")
    logger.info("     - category, tags, summary")
    logger.info("     - chunk_id, source")
    logger.info("")
    logger.info("4. Test Search:")
    logger.info("   • Use the 'Search' tab in dashboard")
    logger.info("   • Can filter by metadata (category='work')")
    logger.info("   • Can search by text (needs embedding)")
    logger.info("")
    logger.info("5. Run Test Search from Python:")
    logger.info("   >>> from src.storage.qdrant_client import RumiQdrantClient")
    logger.info("   >>> from src.storage.embeddings import EmbeddingGenerator")
    logger.info("   >>> client = RumiQdrantClient()")
    logger.info("   >>> gen = EmbeddingGenerator()")
    logger.info("   >>> query = gen.generate_embedding('vLLM inference optimization')")
    logger.info("   >>> results = client.search(query, limit=5, category='work')")
    logger.info("   >>> for r in results:")
    logger.info("   ...     print(r['metadata']['title'], r['score'])")
    logger.info("")
    logger.info("=" * 80)
    logger.info("✅ Pipeline complete! Your blog is now searchable in Qdrant!")
    logger.info("=" * 80)

    return stats, processed_posts


if __name__ == "__main__":
    # Configuration
    RSS_URL = "https://agamjn.com/feed"

    # Limit for testing (None = all posts)
    LIMIT = None  # Set to 5 for quick test, None for all posts

    try:
        stats, posts = sync_blog_to_qdrant(RSS_URL, limit=LIMIT)
        sys.exit(0)
    except Exception as e:
        logger.error(f"Pipeline failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
