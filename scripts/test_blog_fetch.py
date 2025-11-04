#!/usr/bin/env python3
"""
Test blog RSS fetching.

Usage:
    python scripts/test_blog_fetch.py
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.ingestion.blog import fetch_blog_posts
from src.config.logger import get_logger

logger = get_logger(__name__)


def main():
    """Test fetching blog posts from RSS feed."""
    print("\n" + "=" * 60)
    print("Testing Blog RSS Feed Fetching")
    print("=" * 60 + "\n")

    # Your blog RSS URL
    rss_url = "https://agamjn.com/feed"

    try:
        # Fetch the posts
        print(f"Fetching posts from: {rss_url}\n")
        posts = fetch_blog_posts(rss_url)

        # Summary
        print(f"✅ Successfully fetched {len(posts)} blog posts!\n")

        # Show details of first 3 posts
        print("=" * 60)
        print("Preview of Blog Posts:")
        print("=" * 60 + "\n")

        for i, post in enumerate(posts[:3], 1):  # Show first 3
            print(f"Post {i}:")
            print(f"  Title: {post['title']}")
            print(f"  Published: {post['published']}")
            print(f"  URL: {post['url']}")
            print(f"  Content length: {len(post['content'])} characters")

            # Show first 150 chars of content
            content_preview = post['content'][:150].replace('\n', ' ')
            print(f"  Preview: {content_preview}...")
            print()

        # Show titles of all posts
        print("=" * 60)
        print(f"All {len(posts)} Post Titles:")
        print("=" * 60)
        for i, post in enumerate(posts, 1):
            print(f"{i}. {post['title']}")

        print("\n" + "=" * 60)
        print("✅ Test Complete!")
        print("=" * 60)
        print("\nNext steps:")
        print("  - Task 2.3: Classify these posts with Claude")
        print("  - Task 3.2: Store them in Bedrock Knowledge Base")
        print("  - Task 2.2: Add incremental sync (only fetch new posts)")

    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        logger.exception("Failed to fetch blog posts")
        sys.exit(1)


if __name__ == "__main__":
    main()
