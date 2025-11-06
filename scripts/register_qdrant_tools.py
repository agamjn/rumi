"""Register Qdrant tools with Letta server."""

from src.agents.letta_client import RumiLettaClient
from src.agents.qdrant_tools import (
    search_blog_posts,
    get_blog_post_content,
    list_recent_posts
)
from src.config.settings import settings

client = RumiLettaClient()

print("Registering Qdrant tools with Letta...")

# Register search tool
print("\n1. Registering search_blog_posts...")
try:
    search_tool = client.client.tools.create(
        func=search_blog_posts,
        name="search_blog_posts",
        tags=["blog", "search", "qdrant"]
    )
    print(f"   ✓ Registered: {search_tool.id}")
except Exception as e:
    print(f"   ! Tool may already exist: {e}")

# Register get content tool
print("\n2. Registering get_blog_post_content...")
try:
    content_tool = client.client.tools.create(
        func=get_blog_post_content,
        name="get_blog_post_content",
        tags=["blog", "content", "qdrant"]
    )
    print(f"   ✓ Registered: {content_tool.id}")
except Exception as e:
    print(f"   ! Tool may already exist: {e}")

# Register list tool
print("\n3. Registering list_recent_posts...")
try:
    list_tool = client.client.tools.create(
        func=list_recent_posts,
        name="list_recent_posts",
        tags=["blog", "list", "qdrant"]
    )
    print(f"   ✓ Registered: {list_tool.id}")
except Exception as e:
    print(f"   ! Tool may already exist: {e}")

print("\n✓ All tools registered!")

# List all tools to verify
print("\nAvailable blog tools:")
all_tools = client.client.tools.list()
blog_tools = [t for t in all_tools if t.name in ['search_blog_posts', 'list_recent_posts', 'get_blog_post_content']]

for tool in blog_tools:
    print(f"  • {tool.name} (ID: {tool.id})")

print("\nNow you can attach these tools to an agent using:")
print("  client.client.agents.tools.attach(agent_id=agent.id, tool_id=tool.id)")
