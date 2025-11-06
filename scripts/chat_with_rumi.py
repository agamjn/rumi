"""
Interactive chat interface for Rumi.

Start a conversation with your personal AI assistant that has access
to all your blog posts and remembers everything across sessions.

Run with: PYTHONPATH=/Users/agamjain/Downloads/rumi venv/bin/python scripts/chat_with_rumi.py
"""

from src.agents.letta_client import RumiLettaClient
import logging
import sys

logging.basicConfig(level=logging.WARNING)  # Quiet logs for chat
logger = logging.getLogger(__name__)


def print_header():
    """Print chat header."""
    print("\n" + "=" * 80)
    print("RUMI - Your Personal AI Assistant")
    print("=" * 80)
    print("")
    print("I have access to your blog posts and remember our conversations.")
    print("")
    print("Commands:")
    print("  • Type your message and press Enter")
    print("  • 'exit' or 'quit' to end conversation")
    print("  • 'clear' to clear screen")
    print("  • 'memory' to view my memory blocks")
    print("")
    print("=" * 80)
    print("")


def print_memory(client: RumiLettaClient, agent_id: str):
    """Print agent's memory blocks."""
    try:
        agent = client.get_agent(agent_id)
        print("\n" + "=" * 80)
        print("RUMI'S MEMORY")
        print("=" * 80)

        if hasattr(agent, 'memory') and agent.memory:
            for block in agent.memory:
                if hasattr(block, 'label') and hasattr(block, 'value'):
                    print(f"\n[{block.label.upper()}]")
                    print(block.value)
        else:
            print("\nMemory blocks not available in this format.")
            print("(Memory is still working, just can't display it here)")

        print("\n" + "=" * 80)
        print("")
    except Exception as e:
        print(f"⚠️  Couldn't retrieve memory: {e}")


def chat():
    """Main chat loop."""

    print_header()

    # Initialize client
    try:
        print("Connecting to Rumi...")
        client = RumiLettaClient()
    except Exception as e:
        print(f"✗ Failed to connect to Letta server: {e}")
        print("\nMake sure Letta server is running:")
        print("  bash scripts/start_letta_server.sh")
        sys.exit(1)

    # Find Rumi agent
    try:
        agents = client.list_agents()
        rumi_agent = None

        for agent in agents:
            if agent.name == "rumi":
                rumi_agent = agent
                break

        if not rumi_agent:
            print("✗ Rumi agent not found!")
            print("\nCreate Rumi first:")
            print("  PYTHONPATH=/Users/agamjain/Downloads/rumi venv/bin/python scripts/create_rumi_agent.py")
            sys.exit(1)

        agent_id = rumi_agent.id
        print(f"✓ Connected to Rumi (ID: {agent_id})")
        print("")

    except Exception as e:
        print(f"✗ Failed to find Rumi agent: {e}")
        sys.exit(1)

    # Chat loop
    print("You can start chatting now!\n")

    while True:
        try:
            # Get user input
            user_input = input("You: ").strip()

            if not user_input:
                continue

            # Handle commands
            if user_input.lower() in ["exit", "quit", "q"]:
                print("\nGoodbye! I'll remember our conversation for next time.\n")
                break

            if user_input.lower() == "clear":
                print("\033[2J\033[H")  # Clear screen
                print_header()
                continue

            if user_input.lower() == "memory":
                print_memory(client, agent_id)
                continue

            # Send message to Rumi
            try:
                response = client.send_message(agent_id, user_input)

                # Print Rumi's response
                print("")
                for msg in response:
                    # Handle different message formats
                    content = None
                    if hasattr(msg, 'content'):
                        content = msg.content
                    elif hasattr(msg, 'text'):
                        content = msg.text
                    elif isinstance(msg, dict):
                        content = msg.get('content') or msg.get('text')

                    if content:
                        print(f"Rumi: {content}")

                print("")

            except Exception as e:
                print(f"\n⚠️  Error communicating with Rumi: {e}")
                print("")

        except KeyboardInterrupt:
            print("\n\nGoodbye! I'll remember our conversation for next time.\n")
            break

        except Exception as e:
            print(f"\n⚠️  Unexpected error: {e}")
            print("")


def main():
    """Entry point."""
    try:
        chat()
    except Exception as e:
        logger.error(f"Chat failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
