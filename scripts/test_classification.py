#!/usr/bin/env python3
"""
Test blog post classification with OpenAI.

Usage:
    python scripts/test_classification.py
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.ingestion.blog import fetch_blog_posts
from src.processing.classifier import classify_content
from src.config.logger import get_logger

logger = get_logger(__name__)


def main():
    """Test classification on actual blog posts."""
    print("\n" + "=" * 70)
    print("Testing Blog Post Classification with OpenAI")
    print("=" * 70 + "\n")

    # Step 1: Fetch blog posts
    rss_url = "https://agamjn.com/feed"
    print(f"📥 Fetching posts from: {rss_url}\n")

    try:
        posts = fetch_blog_posts(rss_url)
        print(f"✅ Fetched {len(posts)} blog posts\n")
    except Exception as e:
        print(f"❌ Failed to fetch posts: {e}")
        sys.exit(1)

    # Step 2: Classify first 3 posts (to save API costs)
    print("=" * 70)
    print("Classifying First 3 Posts (to save costs)")
    print("=" * 70 + "\n")

    classified_posts = []

    for i, post in enumerate(posts[:3], 1):
        print(f"🤖 Classifying Post {i}/{3}: {post['title'][:50]}...")

        try:
            # Classify the post
            classification = classify_content(
                content=post["content"],
                platform="blog",
                title=post["title"],
                date=post["published"],
            )

            # Combine post data with classification
            classified_post = {**post, **classification}
            classified_posts.append(classified_post)

            # Show results
            print(f"   ✅ Category: {classification['category']}")
            print(f"   ✅ Tags: {', '.join(classification['tags'])}")
            print(f"   ✅ Summary: {classification['summary']}")
            print()

        except Exception as e:
            print(f"   ❌ Classification failed: {e}")
            logger.exception(f"Failed to classify post: {post['title']}")
            print()
            continue

    # Step 3: Summary
    print("=" * 70)
    print("Classification Summary")
    print("=" * 70 + "\n")

    if classified_posts:
        work_posts = [p for p in classified_posts if p["category"] == "work"]
        personal_posts = [p for p in classified_posts if p["category"] == "personal"]

        print(f"📊 Work posts: {len(work_posts)}")
        print(f"📊 Personal posts: {len(personal_posts)}\n")

        print("All Classified Posts:")
        print("-" * 70)
        for post in classified_posts:
            category_emoji = "💼" if post["category"] == "work" else "🧘"
            print(f"{category_emoji} [{post['category'].upper()}] {post['title']}")
            print(f"   Tags: {', '.join(post['tags'])}")
            print(f"   Summary: {post['summary']}")
            print()

        print("=" * 70)
        print("✅ Classification Test Complete!")
        print("=" * 70)
        print("\nNext steps:")
        print("  - Classify all 10 posts (remove [:3] limit)")
        print("  - Task 2.4: Add metadata enrichment (word count, read time)")
        print("  - Task 3.3: Store classified posts in Bedrock KB")

    else:
        print("❌ No posts were successfully classified")
        sys.exit(1)


if __name__ == "__main__":
    main()
