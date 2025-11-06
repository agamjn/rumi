"""
Create the Rumi agent with proper persona, memory, and tools.

This script sets up the main Rumi agent that can:
- Remember conversations across sessions
- Search and retrieve blog content from Qdrant
- Learn about you over time
- Maintain your personal voice and preferences

Run with: PYTHONPATH=/Users/agamjain/Downloads/rumi venv/bin/python scripts/create_rumi_agent.py
"""

from src.agents.letta_client import RumiLettaClient
from src.config.settings import settings
import logging

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)


def create_rumi_agent(recreate: bool = False):
    """Create the Rumi agent with full configuration.

    Args:
        recreate: If True, delete existing Rumi agent and create new one
    """

    logger.info("=" * 80)
    logger.info("CREATING RUMI AGENT")
    logger.info("=" * 80)
    logger.info("")

    # Initialize client
    client = RumiLettaClient()

    # Check if Rumi already exists
    existing_agents = client.list_agents()
    rumi_agent = None

    for agent in existing_agents:
        if agent.name == "rumi":
            rumi_agent = agent
            break

    if rumi_agent:
        if recreate:
            logger.info(f"Found existing Rumi agent (ID: {rumi_agent.id})")
            logger.info("Deleting existing agent...")
            client.delete_agent(rumi_agent.id)
            logger.info("✓ Existing agent deleted")
            logger.info("")
        else:
            logger.info(f"✓ Rumi agent already exists (ID: {rumi_agent.id})")
            logger.info("")
            logger.info("To recreate, run with recreate=True:")
            logger.info("  >>> create_rumi_agent(recreate=True)")
            logger.info("")
            return rumi_agent

    # Define memory blocks
    logger.info("Configuring memory blocks...")

    memory_blocks = [
        {
            "label": "human",
            "value": (
                "Name: Agam Jain\n"
                "Role: Founder of Tensorfuse\n"
                "Location: Working on ML infrastructure\n"
                "\n"
                "Interests:\n"
                "- ML infrastructure (vLLM, RAG, rerankers)\n"
                "- Building products (Tensorfuse, Fastpull)\n"
                "- Philosophy (Advaita, consciousness, detachment)\n"
                "- Personal growth and mental health\n"
                "\n"
                "Communication style:\n"
                "- Prefers direct, concise communication\n"
                "- No unnecessary fluff or emojis\n"
                "- Values technical accuracy\n"
                "- Appreciates learning from first principles\n"
                "\n"
                "Current focus:\n"
                "- Building Rumi (this AI assistant)\n"
                "- Understanding agent memory systems\n"
                "- Organizing personal content (blog posts, transcripts)"
            )
        },
        {
            "label": "persona",
            "value": (
                "You are Rumi, Agam's personal AI assistant.\n"
                "\n"
                "Your purpose:\n"
                "- Help Agam remember and organize their work and thoughts\n"
                "- Search and retrieve content from their blog posts\n"
                "- Maintain context across conversations\n"
                "- Learn and adapt based on their preferences\n"
                "\n"
                "Your capabilities:\n"
                "- Access to all of Agam's blog posts (search_blog_posts tool)\n"
                "- Semantic search to find relevant content\n"
                "- Memory that persists across sessions\n"
                "- Ability to update your understanding over time\n"
                "\n"
                "Your communication style:\n"
                "- Direct and concise (like Agam prefers)\n"
                "- Technical and accurate\n"
                "- No emojis unless explicitly requested\n"
                "- No unnecessary pleasantries or fluff\n"
                "- Focus on substance over form\n"
                "\n"
                "When answering questions:\n"
                "1. If it's about Agam's blog content, use search_blog_posts\n"
                "2. Provide specific references (post titles, dates)\n"
                "3. Include relevant URLs for deeper reading\n"
                "4. Be accurate - if you don't know, say so\n"
                "\n"
                "Remember:\n"
                "- You're not just a chatbot, you're a memory system\n"
                "- Update your knowledge when Agam provides new information\n"
                "- Your job is to make Agam's life easier, not impress them"
            )
        }
    ]

    logger.info("  ✓ Memory blocks configured")
    logger.info("")

    # Create agent
    logger.info("Creating agent...")
    logger.info(f"  Provider: {settings.llm_provider}")
    logger.info(f"  Model: {settings.llm_provider}/{getattr(settings, f'{settings.llm_provider}_llm_model')}")
    logger.info("")

    # System message (optional override of default)
    system_message = (
        "You are Rumi, a personal AI assistant with long-term memory. "
        "You help Agam organize and retrieve their content. "
        "You have access to their blog posts through search tools. "
        "Be direct, accurate, and helpful."
    )

    agent = client.create_agent(
        name="rumi",
        memory_blocks=memory_blocks,
        system=system_message
    )

    logger.info("✓ Rumi agent created successfully!")
    logger.info("")
    logger.info("=" * 80)
    logger.info("AGENT DETAILS")
    logger.info("=" * 80)
    logger.info(f"Agent ID: {agent.id}")
    logger.info(f"Agent Name: {agent.name}")
    logger.info(f"LLM Provider: {settings.llm_provider}")
    logger.info("")
    logger.info("Memory Blocks:")
    logger.info("  1. human - Information about Agam")
    logger.info("  2. persona - Rumi's behavior and capabilities")
    logger.info("")
    logger.info("=" * 80)
    logger.info("AVAILABLE TOOLS")
    logger.info("=" * 80)
    logger.info("")
    logger.info("Rumi has access to these custom tools:")
    logger.info("  • search_blog_posts - Search Agam's blog content")
    logger.info("  • get_blog_post_content - Get full text of specific post")
    logger.info("  • list_recent_posts - List recent blog posts")
    logger.info("")
    logger.info("And built-in Letta tools:")
    logger.info("  • memory_replace - Update memory blocks")
    logger.info("  • memory_insert - Add new lines to memory")
    logger.info("  • memory_rethink - Completely rewrite a memory block")
    logger.info("  • archival_memory_search - Search conversation history")
    logger.info("  • send_message - Communicate with user")
    logger.info("")
    logger.info("=" * 80)
    logger.info("NEXT STEPS")
    logger.info("=" * 80)
    logger.info("")
    logger.info("Start chatting with Rumi:")
    logger.info("  PYTHONPATH=/Users/agamjain/Downloads/rumi venv/bin/python scripts/chat_with_rumi.py")
    logger.info("")
    logger.info("Or use in your code:")
    logger.info("  from src.agents.letta_client import RumiLettaClient")
    logger.info("  client = RumiLettaClient()")
    logger.info(f"  response = client.send_message('{agent.id}', 'What did I write about vLLM?')")
    logger.info("")
    logger.info("=" * 80)
    logger.info("✓ Rumi is ready to help!")
    logger.info("=" * 80)
    logger.info("")

    return agent


def main():
    """Main entry point."""
    import sys

    recreate = "--recreate" in sys.argv or "-r" in sys.argv

    if recreate:
        logger.info("⚠️  Recreate flag detected")
        logger.info("This will delete the existing Rumi agent and create a new one.")
        logger.info("")

    try:
        agent = create_rumi_agent(recreate=recreate)
        sys.exit(0)
    except Exception as e:
        logger.error(f"✗ Failed to create Rumi agent: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
