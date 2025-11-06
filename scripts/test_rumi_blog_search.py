"""Test Rumi's ability to search blog content."""

from src.agents.letta_client import RumiLettaClient
import logging

logging.basicConfig(level=logging.INFO, format='%(message)s')

def test_blog_search():
    """Test that Rumi can search and retrieve blog content."""

    print("\n" + "=" * 80)
    print("TESTING RUMI BLOG SEARCH")
    print("=" * 80 + "\n")

    client = RumiLettaClient()

    # Find Rumi
    agents = client.list_agents()
    rumi = next((a for a in agents if a.name == "rumi"), None)

    if not rumi:
        print("✗ Rumi not found!")
        return

    print(f"✓ Found Rumi (ID: {rumi.id})\n")

    # Test queries that should trigger blog search
    test_queries = [
        "What did I write about vLLM?",
        "List my recent blog posts",
        "What was my detachment blog about?"
    ]

    for i, query in enumerate(test_queries, 1):
        print("=" * 80)
        print(f"TEST {i}")
        print("=" * 80)
        print(f"You: {query}\n")

        response = client.send_message(rumi.id, query)

        print("Rumi:")
        for msg in response:
            content = getattr(msg, 'content', getattr(msg, 'text', None))
            if content:
                print(f"  {content}")
        print("\n")

    print("=" * 80)
    print("✓ Blog search test complete!")
    print("=" * 80 + "\n")

if __name__ == "__main__":
    test_blog_search()
