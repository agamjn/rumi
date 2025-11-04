"""
Blog RSS feed parser and fetcher.

Fetches and parses blog posts from RSS feeds.
"""

import feedparser
from typing import List, Dict
from src.config.logger import get_logger

logger = get_logger(__name__)


def fetch_blog_posts(rss_url: str) -> List[Dict]:
    """
    Fetch and parse blog posts from an RSS feed.

    Args:
        rss_url: URL of the RSS feed (e.g., "https://agamjn.com/feed")

    Returns:
        List of dicts, each containing:
            - title: Post title
            - content: Post content (HTML)
            - published: Publication date (ISO format string)
            - url: URL to the post
            - summary: Short summary if available

    Example:
        >>> posts = fetch_blog_posts("https://agamjn.com/feed")
        >>> print(f"Found {len(posts)} posts")
        >>> print(posts[0]['title'])
    """
    logger.info(f"Fetching RSS feed from {rss_url}")

    try:
        # Parse the RSS feed
        feed = feedparser.parse(rss_url)

        # Check if feed was fetched successfully
        if feed.bozo:  # bozo=1 means there was an error
            logger.warning(f"Feed parsing had issues: {feed.bozo_exception}")

        posts = []
        for entry in feed.entries:
            # Extract content (try different fields, some feeds use different names)
            content = ""
            if hasattr(entry, "content"):
                content = entry.content[0].value  # content is a list
            elif hasattr(entry, "description"):
                content = entry.description
            elif hasattr(entry, "summary"):
                content = entry.summary

            # Build structured post dict
            post = {
                "title": entry.get("title", "Untitled"),
                "content": content,
                "published": entry.get("published", ""),
                "url": entry.get("link", ""),
                "summary": entry.get("summary", ""),
            }

            posts.append(post)

        logger.info(f"Successfully fetched {len(posts)} posts from RSS feed")
        return posts

    except Exception as e:
        logger.error(f"Failed to fetch RSS feed: {str(e)}")
        raise
