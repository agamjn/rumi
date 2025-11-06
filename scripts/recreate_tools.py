"""Delete old tools and create new ones with correct source code."""

from src.agents.letta_client import RumiLettaClient
import inspect
from src.agents import qdrant_tools

client = RumiLettaClient()

print("Recreating Qdrant tools...")

# Get all tools
all_tools = client.client.tools.list()
blog_tool_names = ['search_blog_posts', 'list_recent_posts', 'get_blog_post_content']

# Delete old tools
print("\n1. Deleting old tools...")
for tool in all_tools:
    if tool.name in blog_tool_names:
        try:
            client.client.tools.delete(tool_id=tool.id)
            print(f"   ✓ Deleted {tool.name}")
        except Exception as e:
            print(f"   ! Error deleting {tool.name}: {e}")

# Create new tools with function source
print("\n2. Creating new tools...")

from letta_client.types import PipRequirement

for tool_name in blog_tool_names:
    try:
        func = getattr(qdrant_tools, tool_name)
        source_code = inspect.getsource(func)
        description = func.__doc__.strip() if func.__doc__ else f"Tool: {tool_name}"

        # Create tool with source code and pip requirements
        new_tool = client.client.tools.create(
            source_code=source_code,
            description=description,
            source_type="python",
            tags=["blog", "qdrant"],
            pip_requirements=[
                PipRequirement(name="qdrant-client"),
                PipRequirement(name="openai")
            ]
        )
        print(f"   ✓ Created {tool_name} (ID: {new_tool.id})")
    except Exception as e:
        print(f"   ! Error creating {tool_name}: {e}")

print("\n✓ Done! New tools created.")

# List all tools to verify
print("\nAvailable blog tools:")
all_tools = client.client.tools.list()
blog_tools = [t for t in all_tools if t.name in blog_tool_names]

for tool in blog_tools:
    print(f"  • {tool.name} (ID: {tool.id})")
