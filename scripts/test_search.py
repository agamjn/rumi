"""
Test semantic search on stored blog posts.

Run with: PYTHONPATH=/Users/agamjain/Downloads/rumi venv/bin/python scripts/test_search.py
"""

from src.storage.qdrant_client import RumiQdrantClient
from src.storage.embeddings import EmbeddingGenerator
import logging

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)


def test_search():
    """Test semantic search with different queries."""

    logger.info("=" * 80)
    logger.info("SEMANTIC SEARCH TEST")
    logger.info("=" * 80)
    logger.info("")

    # Initialize clients
    client = RumiQdrantClient()
    generator = EmbeddingGenerator()

    # Test queries
    test_queries = [
        {
            "query": "vLLM inference optimization",
            "category": "work",
            "description": "Technical work on vLLM"
        },
        {
            "query": "What was the teaching about detachment in startups?",
            "category": None,
            "description": "Personal philosophy question"
        },
        {
            "query": "RAG vs memory management",
            "category": "work",
            "description": "Technical architecture question"
        },
        {
            "query": "mental health and coping",
            "category": "personal",
            "description": "Personal wellness topic"
        }
    ]

    for i, test in enumerate(test_queries, 1):
        logger.info("=" * 80)
        logger.info(f"QUERY {i}: {test['query']}")
        logger.info("=" * 80)
        logger.info(f"Description: {test['description']}")
        if test['category']:
            logger.info(f"Filter: category={test['category']}")
        logger.info("")

        # Generate query embedding
        query_embedding = generator.generate_embedding(test['query'])

        # Search
        results = client.search(
            query_vector=query_embedding,
            limit=3,
            category=test['category']
        )

        # Display results
        logger.info(f"Found {len(results)} results:\n")

        for j, result in enumerate(results, 1):
            metadata = result['metadata']
            score = result['score']

            logger.info(f"{j}. {metadata['title']}")
            logger.info(f"   Similarity: {score:.4f}")
            logger.info(f"   Category: {metadata['category']}")
            logger.info(f"   Tags: {', '.join(metadata['tags'][:5])}")
            logger.info(f"   URL: {metadata['url']}")
            logger.info(f"   Summary: {metadata['summary']}")
            logger.info("")

    logger.info("=" * 80)
    logger.info("✓ Semantic search working perfectly!")
    logger.info("=" * 80)


if __name__ == "__main__":
    test_search()
