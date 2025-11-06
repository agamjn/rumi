"""
Embedding generation using OpenAI API.

This module handles converting text into vector embeddings using OpenAI's
text-embedding-3-small model (1536 dimensions).

Embeddings capture semantic meaning - similar text gets similar vectors.
This enables semantic search in Qdrant.

Cost: ~$0.02 per 1M tokens (about $0.00002 per blog post)
"""

from openai import OpenAI
from typing import List, Dict
import logging
import tiktoken

from src.config.settings import settings
from src.storage.chunking import TextChunker

logger = logging.getLogger(__name__)


class EmbeddingGenerator:
    """Generate embeddings using OpenAI API.

    This class handles:
    - Single and batch embedding generation
    - Token counting and cost estimation
    - Error handling and retries
    - Dimension validation

    Example:
        >>> generator = EmbeddingGenerator()
        >>> embedding = generator.generate_embedding("Hello world")
        >>> len(embedding)  # Should be 1536
        1536
    """

    def __init__(self, model: str = "text-embedding-3-small"):
        """Initialize the embedding generator.

        Args:
            model: OpenAI embedding model to use
                - text-embedding-3-small: 1536 dims, $0.02/1M tokens (recommended)
                - text-embedding-3-large: 3072 dims, $0.13/1M tokens (overkill)
                - text-embedding-ada-002: 1536 dims, deprecated
        """
        self.client = OpenAI(api_key=settings.openai_api_key)
        self.model = model
        self.dimensions = 1536  # text-embedding-3-small output size

        # For token counting (cost estimation)
        try:
            self.encoding = tiktoken.encoding_for_model(model)
        except KeyError:
            # Fallback if model not recognized
            self.encoding = tiktoken.get_encoding("cl100k_base")

        # Chunker for long documents
        self.chunker = TextChunker(max_tokens=6000, overlap_tokens=200)

        logger.info(f"EmbeddingGenerator initialized with model: {model}")

    def count_tokens(self, text: str) -> int:
        """Count tokens in text for cost estimation.

        Args:
            text: Input text

        Returns:
            Number of tokens
        """
        return len(self.encoding.encode(text))

    def estimate_cost(self, token_count: int) -> float:
        """Estimate cost in USD for given token count.

        Args:
            token_count: Number of tokens

        Returns:
            Estimated cost in USD
        """
        # text-embedding-3-small pricing: $0.02 per 1M tokens
        cost_per_million = 0.02
        return (token_count / 1_000_000) * cost_per_million

    def generate_embedding(self, text: str) -> List[float]:
        """Generate embedding for a single text.

        This converts text into a 1536-dimensional vector that captures
        semantic meaning. Similar text will have similar vectors.

        Args:
            text: Input text to embed (up to ~8000 tokens)

        Returns:
            List of 1536 floats representing the embedding vector

        Raises:
            Exception: If OpenAI API call fails

        Example:
            >>> embedding = generator.generate_embedding("Optimize vLLM inference")
            >>> len(embedding)
            1536
        """
        try:
            # Count tokens for logging
            token_count = self.count_tokens(text)
            cost = self.estimate_cost(token_count)

            logger.info(f"Generating embedding for text ({len(text)} chars, {token_count} tokens, ${cost:.6f})")

            # Call OpenAI API
            response = self.client.embeddings.create(
                model=self.model,
                input=text,
                encoding_format="float"  # Return as list of floats
            )

            embedding = response.data[0].embedding

            # Validate dimensions
            if len(embedding) != self.dimensions:
                raise ValueError(
                    f"Expected {self.dimensions} dimensions, got {len(embedding)}"
                )

            logger.info(f"✓ Generated embedding successfully (dim={len(embedding)})")
            return embedding

        except Exception as e:
            logger.error(f"Failed to generate embedding: {e}")
            raise

    def generate_embeddings_batch(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for multiple texts in one API call.

        Batching is more efficient than individual calls:
        - Fewer API requests (faster)
        - Same cost per token
        - Up to 2048 inputs per batch (OpenAI limit)

        Args:
            texts: List of input texts

        Returns:
            List of embedding vectors (one per input text)

        Raises:
            Exception: If OpenAI API call fails

        Example:
            >>> texts = ["First post", "Second post", "Third post"]
            >>> embeddings = generator.generate_embeddings_batch(texts)
            >>> len(embeddings)
            3
        """
        if not texts:
            logger.warning("Empty text list provided")
            return []

        try:
            # Count total tokens
            total_tokens = sum(self.count_tokens(text) for text in texts)
            total_cost = self.estimate_cost(total_tokens)

            logger.info(
                f"Generating {len(texts)} embeddings in batch "
                f"({total_tokens} tokens, ${total_cost:.6f})"
            )

            # Call OpenAI API (single request for all texts)
            response = self.client.embeddings.create(
                model=self.model,
                input=texts,
                encoding_format="float"
            )

            # Extract embeddings (order preserved)
            embeddings = [item.embedding for item in response.data]

            # Validate
            if len(embeddings) != len(texts):
                raise ValueError(
                    f"Expected {len(texts)} embeddings, got {len(embeddings)}"
                )

            for i, embedding in enumerate(embeddings):
                if len(embedding) != self.dimensions:
                    raise ValueError(
                        f"Embedding {i}: Expected {self.dimensions} dims, got {len(embedding)}"
                    )

            logger.info(f"✓ Generated {len(embeddings)} embeddings successfully")
            return embeddings

        except Exception as e:
            logger.error(f"Failed to generate batch embeddings: {e}")
            raise

    def generate_with_metadata(self, text: str) -> Dict:
        """Generate embedding with metadata (token count, cost, etc.).

        Useful for tracking and debugging.

        Args:
            text: Input text

        Returns:
            Dict with keys: embedding, token_count, cost, dimensions
        """
        token_count = self.count_tokens(text)
        cost = self.estimate_cost(token_count)
        embedding = self.generate_embedding(text)

        return {
            "embedding": embedding,
            "token_count": token_count,
            "cost_usd": cost,
            "dimensions": len(embedding),
            "model": self.model
        }

    def embed_document_with_chunking(
        self,
        text: str,
        doc_id: str,
        metadata: Dict = None
    ) -> List[Dict]:
        """Embed document with automatic chunking if needed.

        This is the main method to use for blog posts/long content.
        It handles:
        - Short documents: Single embedding
        - Long documents: Multiple chunks with embeddings

        Args:
            text: Full document text
            doc_id: Document identifier (e.g., "blog:post_123")
            metadata: Additional metadata (title, category, tags, etc.)

        Returns:
            List of dicts, each containing:
            - chunk_id: Unique chunk identifier
            - embedding: Vector embedding
            - text: Chunk text
            - tokens: Token count
            - chunk_index: Position in document
            - total_chunks: Total number of chunks
            - parent_id: Original document ID
            - metadata: Additional metadata

        Example:
            >>> result = generator.embed_document_with_chunking(
            ...     text=blog_post_content,
            ...     doc_id="blog:detachment",
            ...     metadata={"title": "Detachment Is All You Need", "category": "personal"}
            ... )
            >>> len(result)  # Could be 1 (short) or multiple (long)
            3
        """
        metadata = metadata or {}

        # Step 1: Chunk the text (or keep as single chunk if short)
        chunks = self.chunker.chunk_text(text, doc_id, metadata)

        # Step 2: Generate embeddings for all chunks
        logger.info(f"Generating embeddings for {len(chunks)} chunk(s)...")

        # Collect all texts for batch embedding
        chunk_texts = [chunk['text'] for chunk in chunks]

        # Generate embeddings in batch (more efficient!)
        embeddings = self.generate_embeddings_batch(chunk_texts)

        # Step 3: Combine embeddings with chunk metadata
        results = []
        for chunk, embedding in zip(chunks, embeddings):
            results.append({
                "chunk_id": chunk['chunk_id'],
                "embedding": embedding,
                "text": chunk['text'],
                "tokens": chunk['tokens'],
                "chunk_index": chunk['chunk_index'],
                "total_chunks": chunk['total_chunks'],
                "parent_id": chunk['parent_id'],
                "metadata": chunk['metadata']
            })

        total_tokens = sum(r['tokens'] for r in results)
        total_cost = self.estimate_cost(total_tokens)

        logger.info(
            f"✓ Embedded document {doc_id}: {len(results)} chunk(s), "
            f"{total_tokens} tokens, ${total_cost:.6f}"
        )

        return results


def test_embedding_generator():
    """Quick test function for development."""
    generator = EmbeddingGenerator()

    # Test single embedding
    text = "Optimizing reranker inference with vLLM for faster RAG pipelines"
    result = generator.generate_with_metadata(text)

    print(f"Text: {text}")
    print(f"Token count: {result['token_count']}")
    print(f"Cost: ${result['cost_usd']:.6f}")
    print(f"Dimensions: {result['dimensions']}")
    print(f"First 5 values: {result['embedding'][:5]}")

    return result


if __name__ == "__main__":
    # Run test if executed directly
    logging.basicConfig(level=logging.INFO)
    test_embedding_generator()
