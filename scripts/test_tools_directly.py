"""Test the tools directly to see if they work."""

from src.agents.tools import search_blog_posts, list_recent_posts
import logging

logging.basicConfig(level=logging.INFO)

print("\n" + "=" * 80)
print("TESTING TOOLS DIRECTLY")
print("=" * 80 + "\n")

# Test 1: Search
print("Test 1: search_blog_posts('vLLM')")
print("-" * 80)
result = search_blog_posts("vLLM")
print(result)
print("")

# Test 2: List posts
print("\nTest 2: list_recent_posts(limit=3)")
print("-" * 80)
result = list_recent_posts(limit=3)
print(result)
print("")

print("=" * 80)
print("✓ Direct tool testing complete")
print("=" * 80)
