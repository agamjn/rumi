"""Create a fresh test agent to verify tools work."""

from src.agents.letta_client import RumiLettaClient
import logging

logging.basicConfig(level=logging.INFO, format='%(message)s')

client = RumiLettaClient()

# Create test agent
memory_blocks = [
    {
        "label": "human",
        "value": "Name: Agam Jain\nRole: Founder of Tensorfuse"
    },
    {
        "label": "persona",
        "value": "You are a test assistant. Use search_blog_posts when asked about blog content."
    }
]

agent = client.create_agent(
    name="test_agent",
    memory_blocks=memory_blocks,
    system="You are a test assistant with blog search tools. Use them when asked."
)

print(f"✓ Created test agent: {agent.id}")

# Attach tools
tools = client.client.tools.list()
blog_tools = [t for t in tools if t.name in ['search_blog_posts', 'list_recent_posts', 'get_blog_post_content']]

for tool in blog_tools:
    client.client.agents.tools.attach(agent_id=agent.id, tool_id=tool.id)
    print(f"  ✓ Attached: {tool.name}")

print(f"\n✓ Test agent ready!")
print(f"Agent ID: {agent.id}")
