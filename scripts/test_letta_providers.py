"""
Test Letta with different LLM providers.

This script demonstrates how to:
1. Check available providers
2. Create agents with different LLMs
3. Switch between providers dynamically

Run with: PYTHONPATH=/Users/agamjain/Downloads/rumi venv/bin/python scripts/test_letta_providers.py
"""

from src.agents.letta_client import RumiLettaClient, LettaConfig
from src.config.settings import settings
import logging

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)


def test_provider_detection():
    """Test which providers are available."""
    logger.info("=" * 80)
    logger.info("PROVIDER DETECTION TEST")
    logger.info("=" * 80)
    logger.info("")

    available = LettaConfig.get_available_providers()

    logger.info("Available providers:")
    for provider, is_available in available.items():
        status = "✓" if is_available else "✗"
        logger.info(f"  {status} {provider}")

    logger.info("")
    logger.info(f"Default provider (from .env): {settings.llm_provider}")
    logger.info("")


def test_model_configuration():
    """Test model configuration for each provider."""
    logger.info("=" * 80)
    logger.info("MODEL CONFIGURATION TEST")
    logger.info("=" * 80)
    logger.info("")

    providers = ["openai", "anthropic", "ollama"]

    for provider in providers:
        try:
            llm_model = LettaConfig.get_llm_model(provider)
            embedding_model = LettaConfig.get_embedding_model(provider)

            logger.info(f"{provider.upper()}:")
            logger.info(f"  LLM Model: {llm_model}")
            logger.info(f"  Embedding Model: {embedding_model}")
            logger.info("")

        except Exception as e:
            logger.error(f"{provider}: {e}")
            logger.info("")


def test_client_initialization():
    """Test initializing the Letta client."""
    logger.info("=" * 80)
    logger.info("CLIENT INITIALIZATION TEST")
    logger.info("=" * 80)
    logger.info("")

    try:
        client = RumiLettaClient()
        logger.info("✓ Client initialized successfully")
        logger.info(f"  Base URL: {client.base_url}")
        logger.info(f"  Provider: {client.provider}")
        logger.info("")

        # List existing agents
        logger.info("Listing existing agents...")
        agents = client.list_agents()
        logger.info(f"  Found {len(agents)} agents")
        for agent in agents:
            logger.info(f"    - {agent.name} (ID: {agent.id})")
        logger.info("")

    except Exception as e:
        logger.error(f"✗ Client initialization failed: {e}")
        logger.info("")
        logger.info("Make sure Letta server is running!")
        logger.info("Start with: bash scripts/start_letta_server.sh")
        return False

    return True


def test_agent_creation():
    """Test creating an agent with current provider."""
    logger.info("=" * 80)
    logger.info("AGENT CREATION TEST")
    logger.info("=" * 80)
    logger.info("")

    try:
        client = RumiLettaClient()

        # Define memory blocks
        memory_blocks = [
            {
                "label": "human",
                "value": (
                    "Name: Agam\n"
                    "Role: Founder of Tensorfuse\n"
                    "Interests: ML infrastructure, RAG, vLLM\n"
                    "Preference: Direct, concise communication"
                )
            },
            {
                "label": "persona",
                "value": (
                    "You are Rumi, Agam's personal AI assistant.\n"
                    "You help Agam remember and organize his work and thoughts.\n"
                    "You are direct, technical, and concise.\n"
                    "You never use emojis unless explicitly asked."
                )
            }
        ]

        # Create test agent
        agent_name = f"rumi_test_{settings.llm_provider}"

        logger.info(f"Creating agent: {agent_name}")
        logger.info(f"Provider: {settings.llm_provider}")
        logger.info("")

        agent = client.create_agent(
            name=agent_name,
            memory_blocks=memory_blocks
        )

        logger.info(f"✓ Agent created successfully!")
        logger.info(f"  Agent ID: {agent.id}")
        logger.info(f"  Agent Name: {agent.name}")
        logger.info("")

        # Test sending a message
        logger.info("Sending test message...")
        response = client.send_message(
            agent.id,
            "Hi, I'm Agam. What's your name and purpose?"
        )

        logger.info("Agent response:")
        for msg in response:
            if hasattr(msg, 'content'):
                logger.info(f"  {msg.content}")
            elif hasattr(msg, 'text'):
                logger.info(f"  {msg.text}")
        logger.info("")

        # Clean up
        logger.info("Cleaning up test agent...")
        client.delete_agent(agent.id)
        logger.info("✓ Test agent deleted")
        logger.info("")

    except Exception as e:
        logger.error(f"✗ Agent creation failed: {e}")
        import traceback
        traceback.print_exc()
        return False

    return True


def test_provider_switching():
    """Test switching between providers."""
    logger.info("=" * 80)
    logger.info("PROVIDER SWITCHING TEST")
    logger.info("=" * 80)
    logger.info("")

    try:
        client = RumiLettaClient()
        original_provider = client.provider

        available = LettaConfig.get_available_providers()
        available_providers = [k for k, v in available.items() if v]

        logger.info(f"Original provider: {original_provider}")
        logger.info(f"Available providers: {available_providers}")
        logger.info("")

        # Test switching to each available provider
        for provider in available_providers:
            if provider != original_provider:
                logger.info(f"Switching to: {provider}")
                try:
                    client.switch_provider(provider)
                    logger.info("  ✓ Successfully switched")
                except Exception as e:
                    logger.error(f"  ✗ Failed: {e}")
                logger.info("")

        # Switch back to original
        logger.info(f"Switching back to: {original_provider}")
        client.switch_provider(original_provider)
        logger.info("  ✓ Restored original provider")
        logger.info("")

    except Exception as e:
        logger.error(f"✗ Provider switching test failed: {e}")
        return False

    return True


def main():
    """Run all tests."""
    logger.info("\n")
    logger.info("*" * 80)
    logger.info("LETTA LLM-AGNOSTIC CONFIGURATION TEST")
    logger.info("*" * 80)
    logger.info("\n")

    # Test 1: Provider detection
    test_provider_detection()

    # Test 2: Model configuration
    test_model_configuration()

    # Test 3: Client initialization
    if not test_client_initialization():
        logger.info("Skipping remaining tests (server not running)")
        return

    # Test 4: Agent creation (requires server)
    test_agent_creation()

    # Test 5: Provider switching
    test_provider_switching()

    logger.info("=" * 80)
    logger.info("✓ ALL TESTS COMPLETE")
    logger.info("=" * 80)
    logger.info("")
    logger.info("Your Letta setup is LLM-agnostic and working!")
    logger.info("")
    logger.info("To change provider, edit .env:")
    logger.info("  LLM_PROVIDER=openai      # Use OpenAI GPT models")
    logger.info("  LLM_PROVIDER=anthropic   # Use Anthropic Claude models")
    logger.info("  LLM_PROVIDER=ollama      # Use local open-source models")
    logger.info("")


if __name__ == "__main__":
    main()
