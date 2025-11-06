"""Test the fresh agent with blog search."""

from src.agents.letta_client import RumiLettaClient
import json

client = RumiLettaClient()

agent_id = "agent-3207281a-9fa7-40dc-9d73-b3c0968fb16f"

print("Sending test query to fresh agent...")
print("Query: 'What did Agam write about vLLM?'\n")

response = client.send_message(agent_id, "What did Agam write about vLLM?")

print("=" * 80)
print("RESPONSE:")
print("=" * 80)

for msg in response:
    print(f"\n[{msg.message_type}]")

    # Show all attributes for debugging
    if msg.message_type == "tool_call_message":
        if hasattr(msg, 'tool_call'):
            print(f"Tool: {msg.tool_call.name}")
            print(f"Args: {msg.tool_call.arguments}")
        elif hasattr(msg, 'function_call'):
            print(f"Function: {msg.function_call.name}")
            print(f"Args: {msg.function_call.arguments}")

    elif msg.message_type == "tool_return_message":
        if hasattr(msg, 'tool_return'):
            print(f"Tool Result:\n{msg.tool_return}")
        elif hasattr(msg, 'function_return'):
            print(f"Function Result:\n{msg.function_return}")

    elif msg.message_type == "assistant_message":
        if hasattr(msg, 'assistant_message') and msg.assistant_message:
            print(f"Assistant: {msg.assistant_message}")
        elif hasattr(msg, 'text') and msg.text:
            print(f"Text: {msg.text}")

    elif msg.message_type == "reasoning_message":
        if hasattr(msg, 'reasoning'):
            print(f"Reasoning: {msg.reasoning}")
        elif hasattr(msg, 'internal_monologue'):
            print(f"Thinking: {msg.internal_monologue}")

    # Debug: show all attributes
    print(f"  Attributes: {[attr for attr in dir(msg) if not attr.startswith('_')]}")

print("\n" + "=" * 80)
