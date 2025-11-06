"""
Register custom Qdrant search tools with Letta.

This script registers the blog search tools with Letta so Rumi can use them.

Run with: PYTHONPATH=/Users/agamjain/Downloads/rumi venv/bin/python scripts/register_tools_with_letta.py
"""

from src.agents.letta_client import RumiLettaClient
from src.agents.tools import SearchBlogPostsTool, GetBlogPostContentTool, ListRecentPostsTool
import logging

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)


def register_custom_tools():
    """Register custom tools with Letta server."""

    logger.info("=" * 80)
    logger.info("REGISTERING CUSTOM TOOLS WITH LETTA")
    logger.info("=" * 80)
    logger.info("")

    client = RumiLettaClient()

    # Get the tool instances (BaseTool classes)
    tools_to_register = [
        SearchBlogPostsTool(),
        ListRecentPostsTool(),
        GetBlogPostContentTool()
    ]

    logger.info("Tools to register:")
    for tool in tools_to_register:
        logger.info(f"  • {tool.name}")
    logger.info("")

    # Register each tool
    registered_tools = []
    for tool_instance in tools_to_register:
        try:
            logger.info(f"Registering {tool_instance.name}...")

            # Create tool from BaseTool instance
            tool = client.client.tools.add(tool=tool_instance)

            logger.info(f"  ✓ Registered: {tool.name} (ID: {tool.id})")
            registered_tools.append(tool)

        except Exception as e:
            if "already exists" in str(e).lower() or "conflict" in str(e).lower():
                logger.info(f"  ⚠ Tool already registered: {tool_instance.name}")
                # Try to get the existing tool
                all_tools = client.client.tools.list()
                existing = next((t for t in all_tools if t.name == tool_instance.name), None)
                if existing:
                    registered_tools.append(existing)
            else:
                logger.error(f"  ✗ Failed to register {tool_instance.name}: {e}")
                import traceback
                traceback.print_exc()

    logger.info("")
    logger.info("=" * 80)
    logger.info(f"✓ Registered {len(registered_tools)} tools")
    logger.info("=" * 80)
    logger.info("")

    return registered_tools


def attach_tools_to_rumi():
    """Attach the custom tools to the Rumi agent."""

    logger.info("=" * 80)
    logger.info("ATTACHING TOOLS TO RUMI AGENT")
    logger.info("=" * 80)
    logger.info("")

    client = RumiLettaClient()

    # Find Rumi agent
    agents = client.list_agents()
    rumi = next((a for a in agents if a.name == "rumi"), None)

    if not rumi:
        logger.error("✗ Rumi agent not found!")
        return False

    logger.info(f"Found Rumi agent (ID: {rumi.id})")
    logger.info("")

    # List all available tools
    logger.info("Listing available tools...")
    all_tools = client.client.tools.list()

    # Find our custom tools
    custom_tool_names = ["search_blog_posts", "list_recent_posts", "get_blog_post_content"]
    custom_tools = [t for t in all_tools if t.name in custom_tool_names]

    if not custom_tools:
        logger.error("✗ Custom tools not found! Run register_custom_tools() first.")
        return False

    logger.info(f"Found {len(custom_tools)} custom tools:")
    for tool in custom_tools:
        logger.info(f"  • {tool.name}")
    logger.info("")

    # Update agent to include these tools
    try:
        logger.info("Updating Rumi agent with custom tools...")

        # Attach each tool to the agent
        tools_added = 0
        for tool in custom_tools:
            try:
                client.client.agents.tools.attach(
                    agent_id=rumi.id,
                    tool_id=tool.id
                )
                logger.info(f"  ✓ Attached tool: {tool.name}")
                tools_added += 1
            except Exception as e:
                if "already" in str(e).lower() or "exists" in str(e).lower():
                    logger.info(f"  ⚠ Tool already attached: {tool.name}")
                else:
                    logger.error(f"  ✗ Failed to attach {tool.name}: {e}")

        logger.info("")
        if tools_added > 0:
            logger.info(f"✓ Added {tools_added} new tools to Rumi")
        else:
            logger.info("⚠ All tools were already attached")

        logger.info("")
        logger.info("=" * 80)
        logger.info("✓ Rumi can now search your blog posts!")
        logger.info("=" * 80)
        logger.info("")

        return True

    except Exception as e:
        logger.error(f"✗ Failed to attach tools: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Register tools and attach to Rumi."""

    try:
        # Step 1: Register custom tools
        registered_tools = register_custom_tools()

        # Step 2: Attach tools to Rumi
        success = attach_tools_to_rumi()

        if success:
            logger.info("=" * 80)
            logger.info("🎉 SUCCESS!")
            logger.info("=" * 80)
            logger.info("")
            logger.info("Rumi can now:")
            logger.info("  • Search your blog posts")
            logger.info("  • List recent posts")
            logger.info("  • Get full post content")
            logger.info("")
            logger.info("Try asking Rumi:")
            logger.info("  'What did I write about vLLM?'")
            logger.info("  'List my recent blog posts'")
            logger.info("  'What was my detachment blog about?'")
            logger.info("")
            logger.info("Start chatting:")
            logger.info("  PYTHONPATH=/Users/agamjain/Downloads/rumi venv/bin/python scripts/chat_with_rumi.py")
            logger.info("")

    except Exception as e:
        logger.error(f"✗ Tool registration failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
