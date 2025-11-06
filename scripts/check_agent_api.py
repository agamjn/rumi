"""Check agent API methods."""

from src.agents.letta_client import RumiLettaClient

client = RumiLettaClient()

print("Agent client methods:")
print([m for m in dir(client.client.agents) if not m.startswith('_')])
print("")

# Get Rumi agent
agents = client.list_agents()
rumi = next((a for a in agents if a.name == "rumi"), None)

if rumi:
    print(f"Rumi agent attributes:")
    print([attr for attr in dir(rumi) if not attr.startswith('_')])
