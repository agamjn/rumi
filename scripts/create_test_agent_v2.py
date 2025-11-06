"""Create a completely fresh test agent with new tools."""

from src.agents.letta_client import RumiLettaClient
from src.config.settings import settings

client = RumiLettaClient()

print("Creating fresh test agent...")

# Create agent
memory_blocks = [
    {"label": "human", "value": "Name: Agam Jain"},
    {"label": "persona", "value": "Test assistant. Use blog search tools when asked."}
]

agent = client.create_agent(
    name="test_v2",
    memory_blocks=memory_blocks,
    system="Test assistant with blog tools"
)

print(f"✓ Created test agent: {agent.id}")

# Configure environment variables for tool execution
env_vars = {
    'OPENAI_API_KEY': settings.openai_api_key,
    'OPENAI_EMBEDDING_MODEL': settings.openai_embedding_model,
    'QDRANT_HOST': 'host.docker.internal',
    'QDRANT_PORT': '6333'
}

client.client.agents.modify(
    agent_id=agent.id,
    tool_exec_environment_variables=env_vars
)
print(f"✓ Configured environment variables")

# Attach new tools
tools = client.client.tools.list()
blog_tools = [t for t in tools if t.name in ['search_blog_posts', 'list_recent_posts', 'get_blog_post_content']]

for tool in blog_tools:
    client.client.agents.tools.attach(agent_id=agent.id, tool_id=tool.id)
    print(f"  ✓ Attached: {tool.name}")

print(f"\n✓ Agent ready!")
print(f"Agent ID: {agent.id}")
print("\nTest with:")
print(f"  python -c \"from src.agents.letta_client import RumiLettaClient; c = RumiLettaClient(); r = c.send_message('{agent.id}', 'What did Agam write about vLLM?'); print(r)\"")
