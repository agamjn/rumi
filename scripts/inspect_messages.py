"""Inspect the actual messages/context sent to LLM."""

from src.agents.letta_client import RumiLettaClient
import json

client = RumiLettaClient()
agents = client.list_agents()
rumi = next((a for a in agents if a.name == 'rumi'), None)

# Get recent messages
print("Getting agent messages...")
print("=" * 80)

# Try to get messages from the agent
try:
    # Get the last few messages
    messages = client.client.agents.messages.list(
        agent_id=rumi.id,
        limit=10
    )

    print(f"Found {len(messages)} messages\n")

    for i, msg in enumerate(messages[:5], 1):
        print(f"Message {i}:")
        dump = msg.model_dump()
        print(f"  Role: {dump.get('role', 'N/A')}")
        print(f"  Type: {dump.get('message_type', 'N/A')}")

        if 'tool_calls' in dump and dump['tool_calls']:
            print(f"  Tool calls: {json.dumps(dump['tool_calls'], indent=4)}")

        content = dump.get('content', dump.get('text', 'N/A'))
        if content and content != 'N/A':
            print(f"  Content: {content[:200]}...")

        print()

except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()

# Try to get agent context/in-context messages
print("\n" + "=" * 80)
print("Trying to get in-context messages...")
print("=" * 80)

try:
    # Check what methods are available
    print("Available methods on agents:")
    print([m for m in dir(client.client.agents) if not m.startswith('_')])

except Exception as e:
    print(f"Error: {e}")
