"""Fix the json_schema descriptions for custom tools."""

from src.agents.letta_client import RumiLettaClient
import logging

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

def fix_tool_descriptions():
    """Update tool json_schema to have proper descriptions."""

    logger.info("=" * 80)
    logger.info("FIXING TOOL DESCRIPTIONS")
    logger.info("=" * 80)
    logger.info("")

    client = RumiLettaClient()

    # Get existing tools
    tools = client.client.tools.list()

    tool_updates = {
        "search_blog_posts": {
            "description": (
                "Search Agam's blog posts for relevant content using semantic search. "
                "Use this when the user asks about topics, concepts, or specific content "
                "from Agam's blog. Returns the most relevant posts with summaries."
            )
        },
        "list_recent_posts": {
            "description": (
                "List Agam's most recent blog posts. "
                "Use this to give an overview or when the user asks what they've written about."
            )
        },
        "get_blog_post_content": {
            "description": (
                "Get the full content of a specific blog post by title. "
                "Use this when you need more detail about a specific post."
            )
        }
    }

    for tool_name, updates in tool_updates.items():
        # Find the tool
        tool = next((t for t in tools if t.name == tool_name), None)

        if not tool:
            logger.warning(f"Tool not found: {tool_name}")
            continue

        logger.info(f"Updating {tool_name}...")

        # Update the json_schema description
        if tool.json_schema:
            tool.json_schema['description'] = updates['description']

        # Modify the tool
        try:
            updated_tool = client.client.tools.modify(
                tool_id=tool.id,
                json_schema=tool.json_schema,
                description=updates['description']
            )
            logger.info(f"  ✓ Updated {tool_name}")
            logger.info(f"    New description: {updates['description'][:80]}...")
        except Exception as e:
            logger.error(f"  ✗ Failed to update {tool_name}: {e}")

    logger.info("")
    logger.info("=" * 80)
    logger.info("✓ Tool descriptions fixed!")
    logger.info("=" * 80)

if __name__ == "__main__":
    fix_tool_descriptions()
