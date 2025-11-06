"""Check what tools Rumi agent has access to."""

from src.agents.letta_client import RumiLettaClient
import json

client = RumiLettaClient()

# Find Rumi
agents = client.list_agents()
rumi = next((a for a in agents if a.name == "rumi"), None)

if not rumi:
    print("Rumi not found!")
    exit(1)

print("=" * 80)
print(f"RUMI AGENT: {rumi.id}")
print("=" * 80)

# Get full agent details
agent = rumi  # The list_agents() already returns the full agent object

print(f"\nAgent name: {agent.name}")
print(f"LLM: {agent.llm_config.model}")
print(f"Embedding: {agent.embedding_config.embedding_model}")

print(f"\n\nAttached Tools ({len(agent.tool_ids) if hasattr(agent, 'tool_ids') else 0}):")
print("=" * 80)

if hasattr(agent, 'tool_ids') and agent.tool_ids:
    for i, tool_id in enumerate(agent.tool_ids, 1):
        tool = client.client.tools.get(tool_id=tool_id)
        print(f"{i}. {tool.name}")
        print(f"   ID: {tool.id}")
        print(f"   Has json_schema: {tool.json_schema is not None}")
        if tool.json_schema:
            print(f"   Schema name: {tool.json_schema.get('name')}")
            print(f"   Required params: {tool.json_schema.get('parameters', {}).get('required', [])}")
        print("")
else:
    print("No tools attached!")

print("\n" + "=" * 80)
print("Full agent config (tool_ids):")
print(agent.tool_ids if hasattr(agent, 'tool_ids') else "No tool_ids attribute")
