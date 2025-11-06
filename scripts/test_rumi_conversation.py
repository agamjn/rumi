"""Quick test of Rumi conversation."""

from src.agents.letta_client import RumiLettaClient
import logging

logging.basicConfig(level=logging.INFO, format='%(message)s')

def test_conversation():
    """Test basic conversation with Rumi."""

    print("\n" + "=" * 80)
    print("TESTING RUMI CONVERSATION")
    print("=" * 80 + "\n")

    client = RumiLettaClient()

    # Find Rumi
    agents = client.list_agents()
    rumi = next((a for a in agents if a.name == "rumi"), None)

    if not rumi:
        print("✗ Rumi not found!")
        return

    print(f"✓ Found Rumi (ID: {rumi.id})\n")

    # Test messages
    test_messages = [
        "Hi Rumi, who are you?",
        "What do you know about me?",
        "What can you help me with?"
    ]

    for i, message in enumerate(test_messages, 1):
        print(f"\n[Test {i}]")
        print(f"You: {message}\n")

        response = client.send_message(rumi.id, message)

        print("Rumi:")
        for msg in response:
            content = getattr(msg, 'content', getattr(msg, 'text', None))
            if content:
                print(f"  {content}")
        print("")

    print("=" * 80)
    print("✓ Conversation test complete!")
    print("=" * 80 + "\n")

if __name__ == "__main__":
    test_conversation()
