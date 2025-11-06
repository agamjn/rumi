"""
LLM-agnostic Letta client wrapper for Rumi.

This module provides a unified interface for working with Letta agents
across different LLM providers (OpenAI, Anthropic, Ollama, etc.).

Features:
- Automatic provider detection from settings
- Easy model switching
- Consistent API regardless of provider
"""

from typing import Optional, Dict, List
import logging

try:
    from letta_client import Letta
except ImportError:
    Letta = None

from src.config.settings import settings

logger = logging.getLogger(__name__)


class LettaConfig:
    """Configuration helper for LLM providers and models."""

    @staticmethod
    def get_llm_model(provider: Optional[str] = None) -> str:
        """Get the LLM model string for Letta based on provider.

        Args:
            provider: LLM provider ('openai', 'anthropic', 'ollama').
                     If None, uses settings.llm_provider.

        Returns:
            Model string in Letta format (e.g., "openai/gpt-4o-mini")
        """
        provider = provider or settings.llm_provider

        if provider == "openai":
            return f"openai/{settings.openai_llm_model}"
        elif provider == "anthropic":
            return f"anthropic/{settings.anthropic_llm_model}"
        elif provider == "ollama":
            return f"ollama/{settings.ollama_llm_model}"
        else:
            raise ValueError(
                f"Unknown provider: {provider}. "
                f"Supported: openai, anthropic, ollama"
            )

    @staticmethod
    def get_embedding_model(provider: Optional[str] = None) -> str:
        """Get the embedding model string for Letta based on provider.

        Args:
            provider: LLM provider ('openai', 'anthropic', 'ollama').
                     If None, uses settings.llm_provider.

        Returns:
            Embedding model string in Letta format
        """
        provider = provider or settings.llm_provider

        if provider == "openai":
            return f"openai/{settings.openai_embedding_model}"
        elif provider == "anthropic":
            # Anthropic doesn't have native embeddings, fall back to OpenAI
            logger.warning(
                "Anthropic doesn't provide embeddings, using OpenAI embeddings"
            )
            return f"openai/{settings.openai_embedding_model}"
        elif provider == "ollama":
            return f"ollama/{settings.ollama_embedding_model}"
        else:
            raise ValueError(
                f"Unknown provider: {provider}. "
                f"Supported: openai, anthropic, ollama"
            )

    @staticmethod
    def get_available_providers() -> Dict[str, bool]:
        """Check which providers are configured with API keys.

        Returns:
            Dict mapping provider name to availability
        """
        return {
            "openai": bool(settings.openai_api_key),
            "anthropic": bool(settings.anthropic_api_key),
            "ollama": True,  # Ollama is always available if running locally
        }

    @staticmethod
    def validate_provider(provider: str) -> bool:
        """Check if a provider is configured and available.

        Args:
            provider: Provider name to validate

        Returns:
            True if provider is available, False otherwise
        """
        available = LettaConfig.get_available_providers()
        return available.get(provider, False)


class RumiLettaClient:
    """LLM-agnostic wrapper for Letta client.

    This class provides a consistent interface for creating and managing
    Letta agents across different LLM providers.

    Example:
        >>> client = RumiLettaClient()
        >>> agent = client.create_agent(
        ...     name="rumi",
        ...     persona="You are Rumi, Agam's AI assistant"
        ... )
        >>> response = client.send_message(agent.id, "Hello!")
    """

    def __init__(
        self,
        base_url: Optional[str] = None,
        token: Optional[str] = None,
        provider: Optional[str] = None
    ):
        """Initialize the Letta client.

        Args:
            base_url: Letta server URL (default: from settings)
            token: Authentication token (default: from settings)
            provider: LLM provider to use (default: from settings)
        """
        if Letta is None:
            raise ImportError(
                "letta-client not installed. Install with: pip install letta-client"
            )

        self.base_url = base_url or settings.letta_base_url
        self.token = token or settings.letta_server_password
        self.provider = provider or settings.llm_provider

        # Validate provider
        if not LettaConfig.validate_provider(self.provider):
            available = LettaConfig.get_available_providers()
            raise ValueError(
                f"Provider '{self.provider}' is not configured. "
                f"Available providers: {[k for k, v in available.items() if v]}"
            )

        # Initialize Letta client
        logger.info(f"Connecting to Letta server at {self.base_url}")
        logger.info(f"Using LLM provider: {self.provider}")

        self.client = Letta(
            base_url=self.base_url,
            token=self.token
        )

        logger.info("✓ Letta client initialized successfully")

    def create_agent(
        self,
        name: str,
        memory_blocks: List[Dict[str, str]],
        system: Optional[str] = None,
        tools: Optional[List[str]] = None,
        provider: Optional[str] = None
    ) -> Dict:
        """Create a new Letta agent with specified configuration.

        Args:
            name: Agent name
            memory_blocks: List of memory blocks with 'label' and 'value' keys
            system: System prompt (optional)
            tools: List of tool names to enable (optional)
            provider: Override default provider for this agent

        Returns:
            Agent object from Letta

        Example:
            >>> memory_blocks = [
            ...     {"label": "human", "value": "Name: Agam\\nRole: Founder"},
            ...     {"label": "persona", "value": "You are Rumi, an AI assistant"}
            ... ]
            >>> agent = client.create_agent("rumi", memory_blocks)
        """
        provider = provider or self.provider

        # Get model configurations
        llm_model = LettaConfig.get_llm_model(provider)
        embedding_model = LettaConfig.get_embedding_model(provider)

        logger.info(f"Creating agent '{name}' with:")
        logger.info(f"  LLM: {llm_model}")
        logger.info(f"  Embedding: {embedding_model}")

        agent = self.client.agents.create(
            name=name,
            model=llm_model,
            embedding=embedding_model,
            memory_blocks=memory_blocks,
            system=system,
            tools=tools
        )

        logger.info(f"✓ Agent created: {agent.id}")
        return agent

    def send_message(
        self,
        agent_id: str,
        message: str,
        role: str = "user"
    ) -> List[Dict]:
        """Send a message to an agent and get response.

        Args:
            agent_id: Agent ID
            message: Message text
            role: Message role (default: "user")

        Returns:
            List of response messages from agent
        """
        logger.info(f"Sending message to agent {agent_id}")

        response = self.client.agents.messages.create(
            agent_id=agent_id,
            messages=[{"role": role, "content": message}]  # Changed 'text' to 'content'
        )

        return response.messages

    def list_agents(self) -> List[Dict]:
        """List all agents on the server.

        Returns:
            List of agent objects
        """
        return self.client.agents.list()

    def get_agent(self, agent_id: str) -> Dict:
        """Get agent by ID.

        Args:
            agent_id: Agent ID

        Returns:
            Agent object
        """
        agents = self.client.agents.list()
        agent = next((a for a in agents if a.id == agent_id), None)
        if not agent:
            raise ValueError(f"Agent not found: {agent_id}")
        return agent

    def delete_agent(self, agent_id: str):
        """Delete an agent.

        Args:
            agent_id: Agent ID
        """
        logger.info(f"Deleting agent {agent_id}")
        self.client.agents.delete(agent_id)
        logger.info("✓ Agent deleted")

    def switch_provider(self, provider: str):
        """Switch to a different LLM provider.

        Args:
            provider: New provider ('openai', 'anthropic', 'ollama')
        """
        if not LettaConfig.validate_provider(provider):
            available = LettaConfig.get_available_providers()
            raise ValueError(
                f"Provider '{provider}' is not configured. "
                f"Available providers: {[k for k, v in available.items() if v]}"
            )

        self.provider = provider
        logger.info(f"Switched to provider: {provider}")
        logger.info(f"  LLM: {LettaConfig.get_llm_model(provider)}")
        logger.info(f"  Embedding: {LettaConfig.get_embedding_model(provider)}")


def get_letta_client(provider: Optional[str] = None) -> RumiLettaClient:
    """Convenience function to get a configured Letta client.

    Args:
        provider: LLM provider (default: from settings)

    Returns:
        Configured RumiLettaClient instance
    """
    return RumiLettaClient(provider=provider)
