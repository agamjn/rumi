"""
Content classification using OpenAI API.

Classifies content as work/personal and extracts metadata.
"""

import json
from typing import Dict
from openai import OpenAI

from src.config.settings import settings
from src.config.logger import get_logger

logger = get_logger(__name__)


def classify_content(content: str, platform: str, title: str = "", date: str = "") -> Dict:
    """
    Classify content using OpenAI API.

    Args:
        content: The blog post content (HTML or text)
        platform: Source platform (e.g., "blog", "linkedin", "twitter")
        title: Post title (optional, helps with context)
        date: Publication date (optional)

    Returns:
        Dict containing:
            - category: "work" or "personal"
            - tags: List of 3-7 relevant tags
            - summary: Brief 1-2 sentence summary

    Example:
        >>> classification = classify_content(
        ...     content="<p>Technical post about ML...</p>",
        ...     platform="blog",
        ...     title="Optimizing Rerankers"
        ... )
        >>> print(classification['category'])  # "work"
        >>> print(classification['tags'])  # ["ml", "optimization", "reranker"]
    """
    logger.info(f"Classifying content from {platform}: {title[:50]}...")

    # Note: gpt-4o-mini supports 128k tokens, so no need to truncate
    # Your blog posts (4-9KB) are well within limits (~1-2k tokens each)

    # Build the classification instructions
    instructions = """
You are analyzing a blog post to classify it and extract metadata.

**Classification Guidelines:**

1. **Category**: Classify as either "work" or "personal"
   - "work": Technical posts, business insights, product updates, engineering content
     Examples: ML/AI, infrastructure, startups, Tensorfuse, Fastpull, technical deep-dives
   - "personal": Philosophy, reflections, mental health, life lessons, non-technical thoughts
     Examples: Advaita, consciousness, detachment, personal growth

2. **Tags**: Extract 3-7 relevant tags
   - Use lowercase
   - Be specific (prefer "vllm" over "ai", "reranker" over "ml")
   - Include: technologies, concepts, companies, topics
   - Examples: ["ml", "vllm", "optimization", "rag", "memory"]

3. **Summary**: Write a 1-2 sentence summary (under 150 characters)
   - Capture the main point
   - Technical for work posts, thematic for personal posts

You must respond with valid JSON in this exact format:
{
    "category": "work" or "personal",
    "tags": ["tag1", "tag2", "tag3"],
    "summary": "Brief summary"
}
"""

    # Build the input with context
    input_text = f"""
Title: {title}
Published: {date}
Platform: {platform}

Content:
{content}

Analyze this content and return the classification as JSON.
"""

    try:
        # Initialize OpenAI client
        client = OpenAI(api_key=settings.openai_api_key)

        # Call the responses API
        response = client.responses.create(
            model=settings.openai_model,  # Will use gpt-4o-mini from .env
            input=input_text,
            instructions=instructions,
            text={"format": {"type": "json_object"}},
        )

        # Parse the JSON response
        result = json.loads(response.output_text)

        logger.info(
            f"Classification complete: category={result.get('category')}, "
            f"tags={len(result.get('tags', []))} tags"
        )

        return result

    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse JSON response: {e}")
        logger.debug(f"Raw response: {response.output_text}")
        raise ValueError(f"Invalid JSON response from OpenAI: {e}")

    except Exception as e:
        logger.error(f"Classification failed: {str(e)}")
        raise
