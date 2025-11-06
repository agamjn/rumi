"""Check Letta API to understand tool creation."""

from src.agents.letta_client import RumiLettaClient
import logging

logging.basicConfig(level=logging.INFO)

client = RumiLettaClient()

# Check what methods are available for tools
print("Tools client methods:")
print(dir(client.client.tools))
print("")

# Try to list existing tools
print("Listing existing tools:")
tools = client.client.tools.list()
print(f"Found {len(tools)} tools")
for tool in tools[:5]:  # Show first 5
    print(f"  - {tool.name if hasattr(tool, 'name') else tool}")
