"""Inspect a registered tool to see its schema."""

from src.agents.letta_client import RumiLettaClient
import json

client = RumiLettaClient()

# Get all tools
tools = client.client.tools.list()

# Find our custom tool
search_tool = next((t for t in tools if t.name == "search_blog_posts"), None)

if search_tool:
    print("=" * 80)
    print("SEARCH_BLOG_POSTS TOOL")
    print("=" * 80)
    print(f"ID: {search_tool.id}")
    print(f"Name: {search_tool.name}")
    print(f"Description: {search_tool.description}")
    print(f"\njson_schema: {search_tool.json_schema}")
    print(f"\nFull tool object:")
    print(json.dumps(search_tool.model_dump(), indent=2, default=str))
else:
    print("Tool not found!")
