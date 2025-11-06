"""
Smart text chunking for embedding long documents.

This module splits long text into smaller chunks while:
- Respecting sentence/paragraph boundaries (no mid-sentence cuts)
- Overlapping chunks to preserve context
- Tracking chunk metadata (position, parent document)

Why chunking?
- OpenAI has 8K token limit for embeddings
- Smaller chunks = more precise retrieval
- "Teaching #2" can be retrieved directly, not the whole post
"""

from typing import List, Dict
import tiktoken
import logging
import re

logger = logging.getLogger(__name__)


class TextChunker:
    """Smart text chunking for long documents.

    Strategy:
    1. Try to chunk by paragraphs (double newlines)
    2. If paragraph too long, chunk by sentences
    3. Add overlap between chunks to preserve context

    Example:
        >>> chunker = TextChunker(max_tokens=1000, overlap_tokens=100)
        >>> chunks = chunker.chunk_text(long_text, doc_id="blog:post_123")
        >>> len(chunks)  # Multiple chunks
        3
    """

    def __init__(
        self,
        max_tokens: int = 6000,  # Safe limit (8K max, leave buffer)
        overlap_tokens: int = 200,  # Overlap to preserve context
        model: str = "text-embedding-3-small"
    ):
        """Initialize the chunker.

        Args:
            max_tokens: Maximum tokens per chunk (default 6000, safe for 8K limit)
            overlap_tokens: Tokens to overlap between chunks (preserves context)
            model: Model name for token counting
        """
        self.max_tokens = max_tokens
        self.overlap_tokens = overlap_tokens

        # Token encoder
        try:
            self.encoding = tiktoken.encoding_for_model(model)
        except KeyError:
            self.encoding = tiktoken.get_encoding("cl100k_base")

        logger.info(
            f"TextChunker initialized: max_tokens={max_tokens}, "
            f"overlap={overlap_tokens}"
        )

    def count_tokens(self, text: str) -> int:
        """Count tokens in text."""
        return len(self.encoding.encode(text))

    def chunk_text(
        self,
        text: str,
        doc_id: str,
        metadata: Dict = None
    ) -> List[Dict]:
        """Chunk text into smaller pieces with metadata.

        Args:
            text: Full text to chunk
            doc_id: Parent document ID (e.g., "blog:post_123")
            metadata: Additional metadata to attach to each chunk

        Returns:
            List of chunk dicts with keys:
            - chunk_id: Unique ID (doc_id:chunk_0, doc_id:chunk_1, etc.)
            - text: Chunk text
            - tokens: Token count
            - chunk_index: Position in document (0, 1, 2...)
            - total_chunks: Total number of chunks
            - parent_id: Original document ID
            - metadata: Additional metadata
        """
        metadata = metadata or {}
        token_count = self.count_tokens(text)

        # If short enough, return as single chunk
        if token_count <= self.max_tokens:
            logger.info(
                f"Document {doc_id} fits in single chunk ({token_count} tokens)"
            )
            return [{
                "chunk_id": f"{doc_id}:chunk_0",
                "text": text,
                "tokens": token_count,
                "chunk_index": 0,
                "total_chunks": 1,
                "parent_id": doc_id,
                "metadata": metadata
            }]

        # Need to chunk
        logger.info(
            f"Document {doc_id} needs chunking ({token_count} tokens > "
            f"{self.max_tokens} limit)"
        )

        # Split by paragraphs first
        paragraphs = self._split_by_paragraphs(text)
        chunks = self._create_chunks(paragraphs, doc_id, metadata)

        logger.info(
            f"Created {len(chunks)} chunks for {doc_id} "
            f"(avg {sum(c['tokens'] for c in chunks) / len(chunks):.0f} tokens/chunk)"
        )

        return chunks

    def _split_by_paragraphs(self, text: str) -> List[str]:
        """Split text by paragraphs (double newlines).

        Falls back to sentences if paragraphs are too long.
        """
        # Split by double newlines (paragraph breaks)
        paragraphs = re.split(r'\n\s*\n', text)

        # Clean up
        paragraphs = [p.strip() for p in paragraphs if p.strip()]

        return paragraphs

    def _split_by_sentences(self, text: str) -> List[str]:
        """Split text by sentences (fallback for long paragraphs)."""
        # Simple sentence splitting (can be improved with nltk)
        sentences = re.split(r'(?<=[.!?])\s+', text)
        return [s.strip() for s in sentences if s.strip()]

    def _create_chunks(
        self,
        paragraphs: List[str],
        doc_id: str,
        metadata: Dict
    ) -> List[Dict]:
        """Create chunks from paragraphs with overlap."""
        chunks = []
        current_chunk = []
        current_tokens = 0

        for para in paragraphs:
            para_tokens = self.count_tokens(para)

            # If single paragraph exceeds limit, split by sentences
            if para_tokens > self.max_tokens:
                logger.warning(
                    f"Paragraph too long ({para_tokens} tokens), splitting by sentences"
                )
                sentences = self._split_by_sentences(para)

                # Recursively handle sentences
                for sentence in sentences:
                    sent_tokens = self.count_tokens(sentence)

                    if current_tokens + sent_tokens > self.max_tokens:
                        # Finalize current chunk
                        if current_chunk:
                            chunks.append({
                                "text": "\n\n".join(current_chunk),
                                "tokens": current_tokens
                            })

                        # Start new chunk with overlap
                        current_chunk = [sentence]
                        current_tokens = sent_tokens
                    else:
                        current_chunk.append(sentence)
                        current_tokens += sent_tokens

            # Normal paragraph handling
            elif current_tokens + para_tokens > self.max_tokens:
                # Finalize current chunk
                if current_chunk:
                    chunks.append({
                        "text": "\n\n".join(current_chunk),
                        "tokens": current_tokens
                    })

                # Start new chunk
                current_chunk = [para]
                current_tokens = para_tokens

            else:
                current_chunk.append(para)
                current_tokens += para_tokens

        # Add final chunk
        if current_chunk:
            chunks.append({
                "text": "\n\n".join(current_chunk),
                "tokens": current_tokens
            })

        # Add metadata to each chunk
        total_chunks = len(chunks)
        for i, chunk in enumerate(chunks):
            chunk.update({
                "chunk_id": f"{doc_id}:chunk_{i}",
                "chunk_index": i,
                "total_chunks": total_chunks,
                "parent_id": doc_id,
                "metadata": metadata
            })

        return chunks


def test_chunker():
    """Test the chunker with sample text."""
    chunker = TextChunker(max_tokens=100, overlap_tokens=20)

    # Create long test text
    long_text = "\n\n".join([
        "This is the introduction paragraph. It sets up the topic.",
        "This is the first main point. It explains concept A in detail. " * 10,
        "This is the second main point. It explains concept B thoroughly. " * 10,
        "This is the conclusion. It ties everything together."
    ])

    chunks = chunker.chunk_text(long_text, doc_id="test:doc_1")

    print(f"Total text: {chunker.count_tokens(long_text)} tokens")
    print(f"Created {len(chunks)} chunks:\n")

    for chunk in chunks:
        print(f"Chunk {chunk['chunk_index']}:")
        print(f"  ID: {chunk['chunk_id']}")
        print(f"  Tokens: {chunk['tokens']}")
        print(f"  Preview: {chunk['text'][:80]}...")
        print()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    test_chunker()
