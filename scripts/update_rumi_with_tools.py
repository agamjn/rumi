"""Update existing Rumi agent with new blog search tools."""

from src.agents.letta_client import RumiLettaClient
from src.config.settings import settings

client = RumiLettaClient()

# Find Rumi
agents = client.list_agents()
rumi = next((a for a in agents if a.name == 'rumi'), None)

if not rumi:
    print("✗ Rumi not found!")
    exit(1)

print(f"Updating Rumi agent: {rumi.id}")

# Configure environment variables for tool execution
env_vars = {
    'OPENAI_API_KEY': settings.openai_api_key,
    'OPENAI_EMBEDDING_MODEL': settings.openai_embedding_model,
    'QDRANT_HOST': 'host.docker.internal',
    'QDRANT_PORT': '6333'
}

client.client.agents.modify(
    agent_id=rumi.id,
    tool_exec_environment_variables=env_vars
)
print(f"✓ Configured environment variables")

# Get new tools
tools = client.client.tools.list()
blog_tools = [t for t in tools if t.name in ['search_blog_posts', 'list_recent_posts', 'get_blog_post_content']]

# Attach tools
for tool in blog_tools:
    try:
        client.client.agents.tools.attach(agent_id=rumi.id, tool_id=tool.id)
        print(f"  ✓ Attached: {tool.name}")
    except Exception as e:
        print(f"  ! {tool.name}: {e}")

print(f"\n✓ Rumi updated and ready!")
print(f"\nStart chatting with:")
print(f"  PYTHONPATH=/Users/agamjain/Downloads/rumi venv/bin/python scripts/chat_with_rumi.py")
