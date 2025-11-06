"""Create a completely fresh test agent with env vars configured."""

from src.agents.letta_client import RumiLettaClient
from src.config.settings import settings

client = RumiLettaClient()

# Create fresh agent with tool env vars
memory_blocks = [
    {"label": "human", "value": "Name: Agam Jain"},
    {"label": "persona", "value": "Test assistant. Use blog search tools when asked."}
]

# Configure tool environment variables
env_vars = {
    'OPENAI_API_KEY': settings.openai_api_key,
    'OPENAI_EMBEDDING_MODEL': settings.openai_embedding_model,
    'QDRANT_HOST': 'host.docker.internal',
    'QDRANT_PORT': '6333'
}

agent = client.create_agent(
    name="fresh_test",
    memory_blocks=memory_blocks,
    system="Test assistant with blog tools"
)

print(f"✓ Created fresh test agent: {agent.id}")

# Configure environment variables for tool execution
client.client.agents.modify(
    agent_id=agent.id,
    tool_exec_environment_variables=env_vars
)
print(f"✓ Configured environment variables for tool execution")

# Attach tools
tools = client.client.tools.list()
blog_tools = [t for t in tools if t.name in ['search_blog_posts', 'list_recent_posts', 'get_blog_post_content']]

for tool in blog_tools:
    client.client.agents.tools.attach(agent_id=agent.id, tool_id=tool.id)
    print(f"  ✓ Attached: {tool.name}")

print(f"\nAgent ID: {agent.id}")
print("Ready to test!")
