"""Update existing tool source code with new function implementations."""

from src.agents.letta_client import RumiLettaClient
import inspect

client = RumiLettaClient()

print("Updating tool source code...")

# Get the new function source code
from src.agents import qdrant_tools

# Get all tools
all_tools = client.client.tools.list()
blog_tools = {t.name: t for t in all_tools if t.name in ['search_blog_posts', 'list_recent_posts', 'get_blog_post_content']}

# Update each tool
for tool_name, tool_obj in blog_tools.items():
    print(f"\nUpdating {tool_name}...")

    # Get the new function
    new_func = getattr(qdrant_tools, tool_name)
    new_source = inspect.getsource(new_func)

    try:
        # Update the tool with new source code
        updated_tool = client.client.tools.update(
            tool_id=tool_obj.id,
            source_code=new_source,
            source_type="python"
        )
        print(f"  ✓ Updated {tool_name}")
    except Exception as e:
        print(f"  ! Error updating {tool_name}: {e}")

print("\n✓ All tools updated!")
