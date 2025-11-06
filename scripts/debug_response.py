"""Debug the full response from Letta to see tool calls."""

from src.agents.letta_client import RumiLettaClient
import json

client = RumiLettaClient()
agents = client.list_agents()
rumi = next((a for a in agents if a.name == 'rumi'), None)

print("Sending: What did I write about vLLM?")
print("=" * 80)

response = client.send_message(rumi.id, "What did I write about vLLM?")

print(f"\nResponse contains {len(response)} messages\n")

for i, msg in enumerate(response, 1):
    print(f"Message {i}:")
    print(f"  Type: {type(msg).__name__}")

    # Try to get all attributes
    if hasattr(msg, 'model_dump'):
        dump = msg.model_dump()
        print(f"  Role: {dump.get('role', 'N/A')}")
        print(f"  Content: {dump.get('content', 'N/A')[:100] if dump.get('content') else 'N/A'}...")

        # Check for tool calls
        if 'tool_calls' in dump:
            print(f"  Tool calls: {dump['tool_calls']}")

        # Check for tool call ID
        if dump.get('tool_call_id'):
            print(f"  Tool call ID: {dump['tool_call_id']}")

        print(f"\n  Full dump:")
        print(json.dumps(dump, indent=4, default=str)[:500])

    print("\n" + "-" * 80 + "\n")
