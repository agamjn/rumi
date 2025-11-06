"""Check tools API on agent."""

from src.agents.letta_client import RumiLettaClient

client = RumiLettaClient()

print("agents.tools methods:")
print([m for m in dir(client.client.agents.tools) if not m.startswith('_')])
