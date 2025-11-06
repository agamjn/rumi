"""Test the fresh agent v2 with blog search."""

from src.agents.letta_client import RumiLettaClient

client = RumiLettaClient()
agent_id = "agent-fd5518cd-41eb-412c-9ffb-32c14ec8b9b9"

print("Testing agent with query: 'What did Agam write about vLLM?'")
print("=" * 80)

response = client.send_message(agent_id, "What did Agam write about vLLM?")

for msg in response:
    print(f"\n[{msg.message_type}]")

    if msg.message_type == "tool_call_message" and hasattr(msg, 'tool_call'):
        print(f"Tool: {msg.tool_call.name}")
        print(f"Args: {msg.tool_call.arguments}")

    elif msg.message_type == "tool_return_message" and hasattr(msg, 'tool_return'):
        print(f"Result:\n{msg.tool_return}")

    elif msg.message_type == "assistant_message" and hasattr(msg, 'content'):
        print(f"Assistant: {msg.content}")

    elif msg.message_type == "reasoning_message" and hasattr(msg, 'reasoning'):
        print(f"Reasoning: {msg.reasoning}")

print("\n" + "=" * 80)
