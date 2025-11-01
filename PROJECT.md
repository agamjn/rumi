# Rumi - Personal Content AI Assistant - Implementation Guide

## Instructions for Claude Code

You are Claude Code, an AI coding assistant. This document provides a structured implementation plan for building **Rumi**, a Personal Content AI Assistant. Follow these instructions carefully:

### Your Role
- Implement each task one at a time
- Wait for approval before proceeding to the next task
- Explain your technical decisions clearly
- Ask questions when requirements are ambiguous
- Write clean, well-documented code
- Create tests for each component

### How to Use This Document
1. Read the task description completely
2. Review the "Tech Stack Decision Point" section
3. Propose your implementation approach
4. Wait for user approval
5. Implement the task
6. Verify success criteria are met
7. Document what you built
8. Move to next task only when approved

---

## Architecture Decisions (Approved)

**Strategy**: Start simple with EC2, use managed services where beneficial

### Core Architecture (Phase 1 - POC)
```
┌─────────────────────────────────────────────────────┐
│ EC2 SERVER (t3.small)                               │
├─────────────────────────────────────────────────────┤
│ - Letta agent                                       │
│ - FastAPI backend                                   │
│ - Scraping scripts (cron scheduled)                 │
│ - Browser-use for LinkedIn/Twitter                 │
└─────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────┐
│ AWS MANAGED SERVICES                                │
├─────────────────────────────────────────────────────┤
│ - Bedrock Knowledge Base (content storage)         │
│ - DynamoDB (state tracking)                        │
│ - CloudWatch (logs)                                 │
│ - Secrets Manager (API keys)                       │
└─────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────┐
│ FRONTEND                                            │
├─────────────────────────────────────────────────────┤
│ - Vercel (Next.js hosting)                         │
└─────────────────────────────────────────────────────┘
```

### Key Decisions
- **Compute**: EC2 (simple, debuggable, good for learning)
- **Agent**: Letta (flexible, full control)
- **State Management**: DynamoDB (managed, accessible everywhere)
- **Content Storage**: Bedrock Knowledge Base (purpose-built for RAG)
- **Scheduling**: Cron on EC2 (simple to start)
- **Logs**: CloudWatch (managed, searchable)
- **Frontend**: Vercel (zero-config Next.js deployment)

### Why This Approach
- ✅ Easy to debug (SSH into EC2)
- ✅ Simple mental model (one server)
- ✅ Managed services for complex parts
- ✅ Can optimize to serverless later if needed
- ✅ Cost: ~$20-30/month

---

## Phase 0: Foundation & Setup

### Task 0.1: Project Structure Setup
**Your Task**: Create the basic project structure and development environment for Rumi

**Requirements**:
- Set up a Python project with proper structure
- Configure virtual environment
- Add basic configuration files
- Make it production-ready (not just local development)

**Expected Structure**:
````
rumi/
├── README.md                 # Final GitHub README (create at end)
├── OVERVIEW.md              # User-facing description of Rumi
├── PROJECT.md               # This implementation guide
├── requirements.txt         # Python dependencies
├── .env.example            # Example environment variables
├── .gitignore              # Git ignore patterns
├── pyproject.toml          # Package configuration
├── .claude/
│   └── instructions.md     # Instructions for Claude Code
├── src/
│   ├── __init__.py
│   ├── config/             # Configuration management
│   │   ├── __init__.py
│   │   ├── settings.py
│   │   └── logger.py
│   ├── ingestion/          # Content scrapers and fetchers
│   │   ├── __init__.py
│   │   ├── blog.py
│   │   ├── linkedin.py
│   │   ├── twitter.py
│   │   ├── fathom.py
│   │   ├── browser.py
│   │   └── auth.py
│   ├── processing/         # Classification and enrichment
│   │   ├── __init__.py
│   │   ├── classifier.py
│   │   └── enricher.py
│   ├── storage/            # Bedrock KB and state management
│   │   ├── __init__.py
│   │   ├── bedrock_client.py
│   │   └── state_manager.py
│   ├── agent/              # Letta agent and tools
│   │   ├── __init__.py
│   │   ├── letta_agent.py
│   │   └── custom_tools.py
│   └── api/                # FastAPI backend
│       ├── __init__.py
│       └── main.py
├── frontend/               # Next.js frontend
│   ├── app/
│   ├── components/
│   └── package.json
├── tests/                  # Unit and integration tests
│   ├── __init__.py
│   ├── test_ingestion/
│   ├── test_processing/
│   ├── test_storage/
│   └── test_agent/
├── scripts/                # Utility scripts
│   ├── sync_blog.py
│   ├── sync_linkedin.py
│   ├── sync_twitter.py
│   ├── sync_fathom.py
│   ├── curate_consumption.py
│   ├── create_voice_profiles.py
│   └── run_nightly_sync.py
└── logs/                   # Application logs
````

**Success Criteria**:
- [ ] Project structure created with all directories
- [ ] Virtual environment configured and activated
- [ ] Can run `python -m src.config.settings` without errors
- [ ] .gitignore properly excludes .env, __pycache__, etc.
- [ ] OVERVIEW.md exists with project description
- [ ] .claude/instructions.md exists with Claude Code rules

**Tech Stack Decision Point**:
- **Python version**: Recommend 3.11+ (latest stable)
- **Project layout**: Use `src/` layout (better for packages)
- **Dependency management**: Propose your preference and explain why
  - pip + requirements.txt (simple, standard)
  - poetry (modern, dependency resolution)
  - uv (fastest, newest)

**Questions for User**:
1. Which dependency management tool do you prefer?
2. Any specific Python version requirements?

---

### Task 0.2: Environment Configuration
**Your Task**: Set up secure configuration management for API keys and deployment settings

**Requirements**:
- Load configuration from environment variables
- Support multiple environments (local, staging, production)
- Validate required settings on startup
- Never commit secrets to git
- Work across local development and AWS EC2 deployment

**Implementation Details**:
Create `src/config/settings.py` that handles:
- Anthropic API key
- AWS credentials and region
- Bedrock Knowledge Base ID
- Letta configuration
- Browser-use settings
- Database paths (for state manager)

**Success Criteria**:
- [ ] Can load config from `.env` file locally
- [ ] Can load config from environment variables (for EC2)
- [ ] Config validates all required settings on import
- [ ] Clear error messages for missing configuration
- [ ] `.env.example` documents all required variables

**Tech Stack Decision Point**:
- **Environment loading**: python-dotenv (standard) or other?
- **Validation**: pydantic-settings (type-safe) or manual validation?

**Questions for User**:
1. Do you want type-safe config with pydantic?
2. Do you need different configs for dev/staging/prod?

---

### Task 0.3: Logging Setup
**Your Task**: Implement centralized logging for debugging and monitoring

**DECISION MADE**: Using Python's standard `logging` module + **AWS CloudWatch** for production

**Requirements**:
- Consistent logging across all modules
- Log to console (local development)
- Log to CloudWatch (EC2 production)
- Different log levels (DEBUG, INFO, WARNING, ERROR)
- Structured format for easier parsing
- Works on both local and EC2

**Implementation Details**:
Create `src/config/logger.py` that provides:
- Formatted console output (colorized for local dev)
- CloudWatch integration for EC2 (via watchtower library)
- Automatic environment detection (local vs EC2)
- Structured log format with context

**Example Usage**:
````python
from src.config.logger import get_logger

logger = get_logger(__name__)
logger.info("Starting blog sync", extra={"source": "blog", "count": 10})
logger.error("Failed to fetch", extra={"url": "...", "error": "..."})
````

**Success Criteria**:
- [ ] All modules can import and use logger
- [ ] Logs appear in console during local development
- [ ] Logs sent to CloudWatch when running on EC2
- [ ] Can change log level via environment variable
- [ ] Timestamps and context in all log messages
- [ ] Easy to search logs in CloudWatch console

**Tech Stack**:
- **Logging library**: Standard Python `logging` (built-in, well-understood)
- **CloudWatch integration**: `watchtower` library (handles CloudWatch streaming)
- **Local development**: Console output with colors (via `colorlog` optional)

**CloudWatch Setup**:
- Log Group: `/rumi/application`
- Retention: 30 days (configurable)
- No additional code needed - watchtower handles streaming

---

## Phase 1: State Management & Deduplication

### Task 1.1: State Manager Design & Implementation
**Your Task**: Create a system to track what content has been synced to avoid duplicates

**DECISION MADE**: Using **DynamoDB for state tracking** + **Bedrock KB handles deduplication**

**Approach**:
- Use unique document IDs when inserting to Bedrock (e.g., `linkedin:abc123`, `blog:fastpull-optimization`)
- Track "last synced timestamp" in DynamoDB for efficient querying (don't re-process old content)
- If Bedrock rejects a duplicate, just log and continue
- This gives us both safety and efficiency

**DynamoDB Table Structure**:
````python
# Table: rumi_state
# Primary Key: source (String)

{
    "source": "blog",
    "last_sync_time": "2024-11-01T10:30:00Z",
    "last_item_id": "https://agamjn.com/post/fastpull-optimization",
    "last_updated": "2024-11-01T10:35:00Z",
    "item_count": 42
}

{
    "source": "linkedin",
    "last_sync_time": "2024-11-01T11:00:00Z",
    "last_item_id": "post_abc123",
    "last_updated": "2024-11-01T11:05:00Z",
    "item_count": 156
}
````

**Requirements**:
- Track sync state for each source (blog, linkedin, twitter, fathom)
- Prevent duplicate ingestion via Bedrock doc IDs
- Survive server restarts (DynamoDB is always available)
- Be queryable (when did we last sync X?)
- Be resettable for testing (just delete/update the item)

**Implementation Details**:
Create `src/storage/state_manager.py`:
````python
import boto3
from datetime import datetime
from typing import Optional, Dict

class StateManager:
    def __init__(self, table_name: str = "rumi_state"):
        self.table_name = table_name
        self.dynamodb = boto3.resource('dynamodb')
        self.table = self.dynamodb.Table(table_name)

    def get_last_sync(self, source: str) -> Optional[Dict]:
        """Get last sync info for a source."""
        pass

    def update_last_sync(self, source: str, item_id: str, sync_time: str):
        """Update last sync info for a source."""
        pass

    def reset_state(self, source: str):
        """Reset state for testing."""
        pass
````

**Success Criteria**:
- [ ] DynamoDB table created (manually via console or boto3)
- [ ] Can store and retrieve state for each source
- [ ] State persists across application restarts
- [ ] Can reset state for testing
- [ ] Accessible from EC2 and local development
- [ ] Unit tests with mocked DynamoDB

**Tech Stack**:
- **Storage**: AWS DynamoDB (on-demand billing, free tier covers POC usage)
- **SDK**: boto3 (AWS Python SDK)
- **Testing**: moto library for mocking DynamoDB

---

## Phase 2: Content Ingestion - Blog (Simplest Source First)

### Task 2.1: Blog RSS Parser
**Your Task**: Fetch and parse blog posts from RSS feed at agamjn.com

**Requirements**:
- Fetch RSS feed from user's blog
- Parse feed entries into structured data
- Extract: title, content, publication date, URL
- Handle common RSS/Atom feed formats
- Graceful error handling (network failures, malformed XML)

**Implementation Details**:
Create `src/ingestion/blog.py` with function:
````python
def fetch_blog_posts(rss_url: str) -> List[Dict]:
    """
    Fetch and parse blog RSS feed.
    
    Returns:
        List of dicts with keys: title, content, date, url
    """
    pass
````

**Success Criteria**:
- [ ] Can fetch RSS feed from agamjn.com
- [ ] Parses all posts correctly
- [ ] Returns structured data (list of dicts)
- [ ] Handles network errors without crashing
- [ ] Unit test with mock RSS feed

**Tech Stack Decision Point**:
- **RSS parsing**: `feedparser` (most popular) or alternatives?
- **HTTP requests**: `requests` or `httpx`?

**Questions for User**:
1. What is the RSS feed URL for your blog?
2. Any specific date format or content quirks to handle?

---

### Task 2.2: Blog Incremental Sync
**Your Task**: Only fetch NEW blog posts using state manager

**Requirements**:
- Integrate with state manager from Task 1.1
- Get last synced date/ID
- Only fetch posts newer than last sync
- Update state after successful sync
- Handle first run (no previous state)

**Implementation Details**:
Enhance `src/ingestion/blog.py`:
````python
def fetch_new_blog_posts(rss_url: str, state_manager: StateManager) -> List[Dict]:
    """
    Fetch only new blog posts since last sync.
    """
    last_sync = state_manager.get_last_sync("blog")
    all_posts = fetch_blog_posts(rss_url)
    new_posts = filter_posts_after(all_posts, last_sync)
    return new_posts
````

**Success Criteria**:
- [ ] First run fetches all posts
- [ ] Second run (no new posts) returns empty list
- [ ] Adding new post triggers fetch on next run
- [ ] State updated after successful fetch
- [ ] Integration test verifying incremental behavior

**Questions for User**:
1. Should state update happen in this module or separately?

---

### Task 2.3: Blog Content Classifier
**Your Task**: Use Claude API to classify blog posts and extract metadata

**Requirements**:
- Call Anthropic API to classify each post
- Determine category: "work" or "personal"
- Extract relevant tags (3-7 tags per post)
- Calculate importance score (0-10)
- Generate brief summary (2-3 sentences)
- Return structured JSON

**Implementation Details**:
Create `src/processing/classifier.py`:
````python
def classify_content(content: str, platform: str) -> Dict:
    """
    Classify content using Claude API.
    
    Returns:
        {
            "category": "work" or "personal",
            "tags": ["tag1", "tag2", ...],
            "importance_score": 7.5,
            "summary": "Brief summary..."
        }
    """
    pass
````

**Prompt Engineering**:
You'll need to craft a prompt that:
- Understands work vs personal distinction
- Knows about Fastpull, Tensorfuse, etc. (work)
- Knows about Advaita, consciousness, etc. (personal)
- Extracts technical and thematic tags
- Scores importance based on uniqueness and depth

**Success Criteria**:
- [ ] Correctly classifies sample work blog posts
- [ ] Correctly classifies sample personal blog posts
- [ ] Extracts relevant tags
- [ ] Importance scores are reasonable
- [ ] Handles API errors gracefully
- [ ] Returns valid JSON structure

**Tech Stack Decision Point**:
- **Anthropic SDK**: Use official `anthropic` package
- **Model**: Claude 3.5 Sonnet (fast + smart)
- **JSON mode**: Use Anthropic's JSON schema feature?

**Questions for User**:
1. Review the classification prompt I draft - is it accurate?
2. Should I provide example classifications to improve accuracy?

---

### Task 2.4: Blog Metadata Enrichment
**Your Task**: Add computed metadata to blog posts

**Requirements**:
- Calculate word count from content
- Estimate read time (assume 200-250 words/minute)
- Format timestamps to ISO 8601
- Add ingestion timestamp

**Implementation Details**:
Create `src/processing/enricher.py`:
````python
def enrich_metadata(post: Dict) -> Dict:
    """
    Add computed metadata fields.
    """
    post["word_count"] = count_words(post["content"])
    post["read_time_minutes"] = estimate_read_time(post["word_count"])
    post["created_at"] = format_timestamp(post["date"])
    post["ingested_at"] = current_timestamp()
    return post
````

**Success Criteria**:
- [ ] Accurate word counts
- [ ] Reasonable read time estimates
- [ ] Timestamps in ISO 8601 format
- [ ] All metadata fields added
- [ ] Unit tests for edge cases

**Questions for User**:
1. Preferred reading speed for estimates? (200-250 WPM?)

---

## Phase 3: AWS Bedrock Knowledge Base Setup

### Task 3.1: AWS Bedrock KB Setup
**Your Task**: Set up AWS Bedrock Knowledge Base and document the process

**Requirements**:
- Create AWS Bedrock Knowledge Base for Rumi
- Configure S3 data source
- Set up IAM permissions
- Test access from local machine
- Document setup steps for future reference

**Steps to Complete**:
1. Log into AWS Console
2. Navigate to Amazon Bedrock
3. Create Knowledge Base:
   - Choose embedding model (Titan recommended)
   - Create S3 bucket for data source
   - Configure IAM roles
4. Test connectivity with boto3 locally
5. Document KB ID, data source ID, S3 bucket name in PROJECT.md

**Success Criteria**:
- [ ] Knowledge Base created and active
- [ ] Can access KB from AWS Console
- [ ] boto3 can authenticate successfully
- [ ] Know KB ID and data source ID
- [ ] Setup documented in PROJECT.md

**Tech Stack Decision Point**:
- **AWS Region**: Recommend us-east-1 or us-west-2 (Bedrock availability)
- **Embedding Model**: Titan Embeddings G1 or other?
- **Storage**: S3 Standard or Intelligent Tiering?

**Questions for User**:
1. Which AWS region do you prefer?
2. Do you have AWS credentials configured locally already?
3. Do you want me to guide you through console, or use boto3/CloudFormation?

---

### Task 3.2: Bedrock KB Python Client
**Your Task**: Create a Python client to interact with Bedrock Knowledge Base

**Requirements**:
- Wrapper class for Bedrock KB operations
- Insert documents with metadata
- Search documents with filters
- Delete documents by ID
- Handle errors and rate limits

**Implementation Details**:
Create `src/storage/bedrock_client.py`:
````python
class BedrockKBClient:
    def __init__(self, kb_id: str, region: str):
        self.kb_id = kb_id
        self.region = region
        self.client = boto3.client('bedrock-agent-runtime', region_name=region)
    
    def ingest_document(self, doc_id: str, content: str, metadata: Dict) -> bool:
        """Insert document into KB with metadata."""
        pass
    
    def search(self, query: str, filters: Dict = None, max_results: int = 10) -> List[Dict]:
        """Search KB with optional metadata filters."""
        pass
    
    def delete_document(self, doc_id: str) -> bool:
        """Delete document from KB."""
        pass
````

**Success Criteria**:
- [ ] Can insert a test document
- [ ] Can search and retrieve it
- [ ] Metadata properly attached and filterable
- [ ] Can delete document
- [ ] Error handling for API failures
- [ ] Integration test with actual Bedrock KB

**Questions for User**:
1. Should document IDs be auto-generated or user-provided?
2. How should we handle large documents (chunking)?

---

### Task 3.3: Blog to Bedrock Pipeline
**Your Task**: Connect all blog ingestion pieces into end-to-end pipeline

**Requirements**:
- Orchestrate all previous tasks (fetch, classify, enrich, store)
- Handle errors at each step gracefully
- Log progress and failures
- Update state only on success
- Can be run as a standalone script

**Implementation Details**:
Create `scripts/sync_blog.py`:
````python
def sync_blog_to_bedrock():
    """
    Full pipeline for blog ingestion.
    
    Steps:
    1. Fetch new blog posts (Task 2.2)
    2. For each post:
       a. Classify (Task 2.3)
       b. Enrich metadata (Task 2.4)
       c. Generate document ID
       d. Ingest to Bedrock KB (Task 3.2)
    3. Update state manager (Task 1.1)
    4. Log summary
    """
    pass
````

**Success Criteria**:
- [ ] Can run script and ingest all blog posts
- [ ] Running again doesn't create duplicates
- [ ] All metadata visible in Bedrock KB console
- [ ] Can search and find blog posts by keyword
- [ ] Can filter by category (work/personal)
- [ ] Logs show clear progress
- [ ] Errors don't crash entire pipeline

**Questions for User**:
1. Should failed posts be retried or just logged?
2. Should there be a dry-run mode for testing?

---

## Phase 4: Letta Agent Setup

### Task 4.1: Letta Installation & Basic Setup
**Your Task**: Install Letta and create your first agent for Rumi

**Requirements**:
- Install Letta locally for testing
- Create agent with basic configuration
- Test agent via CLI
- Understand memory blocks and archival memory
- Document Letta configuration

**Steps to Complete**:
1. `pip install letta`
2. `letta configure` (set up with Claude)
3. Create agent via Letta API
4. Test basic conversation
5. Insert test memory

**Success Criteria**:
- [ ] Letta installed and configured
- [ ] Agent created successfully
- [ ] Can chat with agent via `letta run`
- [ ] Agent remembers information across sessions
- [ ] Configuration documented

**Tech Stack Decision Point**:
- **Letta backend**: Local SQLite or hosted?
- **LLM provider**: Claude (Anthropic) configured

**Questions for User**:
1. Do you want Letta to use the same Anthropic API key as the rest of the system?
2. Should Letta data be stored locally or in a database?

---

### Task 4.2: Voice Profile Creation
**Your Task**: Create memory blocks containing your writing voice for each platform

**Requirements**:
- Analyze example posts from each platform
- Extract style patterns
- Create memory blocks in Letta
- Test voice matching by generating sample content

**Implementation Details**:
Create `scripts/create_voice_profiles.py`:
````python
def create_voice_profiles(agent_id: str):
    """
    Create memory blocks for LinkedIn, Twitter, and Blog voices.
    
    Each memory block contains:
    - 3-5 example posts
    - Style guide (tone, structure, patterns)
    - Common phrases and terminology
    """
    pass
````

**User Action Required**:
You'll need to provide:
- 3-5 best LinkedIn posts
- 3-5 best tweets
- 2-3 blog post excerpts

**Success Criteria**:
- [ ] Memory blocks created in Letta
- [ ] Agent can access voice profiles
- [ ] Test generation in each voice
- [ ] Generated content sounds like you
- [ ] Clear style differences between platforms

**Questions for User**:
1. Which posts should I use as voice examples?
2. Should I analyze your existing content automatically to extract patterns?

---

### Task 4.3: Custom Bedrock Search Tool
**Your Task**: Create custom tool for Letta to search Bedrock KB

**Requirements**:
- Define tool function for Bedrock search
- Register tool with Letta agent
- Handle tool parameters (query, filters)
- Return formatted results to agent

**Implementation Details**:
Create `src/agent/custom_tools.py`:
````python
@tool
def search_content(
    query: str,
    category: Optional[str] = None,
    source: Optional[str] = None,
    max_results: int = 10
) -> str:
    """
    Search your personal content knowledge base.
    
    Args:
        query: What to search for
        category: Filter by "work" or "personal"
        source: Filter by "created" or "consumed"
        max_results: Number of results to return
        
    Returns:
        Formatted search results with metadata
    """
    # Call BedrockKBClient.search()
    # Format results for agent consumption
    pass
````

**Success Criteria**:
- [ ] Tool registered with Letta agent
- [ ] Agent can call tool successfully
- [ ] Search returns relevant results
- [ ] Metadata included in results
- [ ] Test query: "find my blog posts about Fastpull"

**Questions for User**:
1. How should search results be formatted for the agent?
2. Should the tool return full content or summaries?

---

### Task 4.4: End-to-End Test: Blog Query
**Your Task**: Test complete pipeline from ingestion to content generation

**Requirements**:
- Verify blog posts are in Bedrock KB
- Create Letta agent with voice profiles and custom tool
- Test querying for specific content
- Test generating new content using retrieved context
- Document the workflow

**Test Scenarios**:
1. "What have I written about Fastpull?"
2. "Find my recent work blog posts"
3. "Write a LinkedIn post about container optimization using my past work"

**Success Criteria**:
- [ ] All test queries return relevant results
- [ ] Agent retrieves correct blog posts
- [ ] Generated content matches your voice
- [ ] Generated content references your actual work
- [ ] End-to-end latency is acceptable (<10s)

**Questions for User**:
1. What specific queries should I test?
2. How will you evaluate if generated content is good?

---

## Phase 5: Browser-Use Setup & Social Media Ingestion

### Task 5.1: Browser-Use Installation & Testing
**Your Task**: Install browser-use and test basic automation

**Requirements**:
- Install browser-use library
- Set up headless browser (Playwright or Selenium)
- Test basic navigation and interaction
- Verify it works on AWS EC2 (headless environment)

**Implementation Details**:
````bash
pip install browser-use
# Install playwright browsers
playwright install
````

Create `scripts/test_browser_use.py`:
````python
from browser_use import Agent

async def test_basic_navigation():
    """Test that browser-use can navigate and extract data."""
    agent = Agent(
        task="Go to google.com and search for 'test'",
        llm=claude_instance
    )
    result = await agent.run()
    print(result)
````

**Success Criteria**:
- [ ] browser-use installed successfully
- [ ] Can launch browser programmatically
- [ ] Can navigate to websites
- [ ] Works in headless mode (for EC2)
- [ ] Test script runs successfully

**Tech Stack Decision Point**:
- **Browser backend**: Playwright (recommended) or Selenium?
- **Headless**: Always headless or headed for local testing?

**Questions for User**:
1. Should I set up both local (headed) and server (headless) configs?

---

### Task 5.2: LinkedIn Authentication Setup
**Your Task**: Set up persistent LinkedIn login for automation

**Requirements**:
- Log into LinkedIn once through browser-use
- Save browser session/cookies
- Reuse session in future runs (no re-login)
- Handle session expiry gracefully

**Implementation Details**:
Create `src/ingestion/auth.py`:
````python
class BrowserSession:
    def __init__(self, platform: str, session_file: str):
        self.platform = platform
        self.session_file = session_file
    
    def login(self):
        """Interactive login, save session."""
        pass
    
    def load_session(self):
        """Load saved session."""
        pass
    
    def is_logged_in(self) -> bool:
        """Check if session is still valid."""
        pass
````

**User Action Required**:
You'll need to manually log into LinkedIn once when prompted.

**Success Criteria**:
- [ ] Can log into LinkedIn through browser-use
- [ ] Session saved to file
- [ ] Future runs reuse session (no login prompt)
- [ ] Detects expired session and prompts re-login
- [ ] Works on EC2 (headless)

**Questions for User**:
1. Where should session files be stored? (local, S3, encrypted?)
2. Should 2FA be handled automatically or manually?

---

### Task 5.3: LinkedIn Post Scraper
**Your Task**: Use browser-use to scrape your LinkedIn posts

**Requirements**:
- Navigate to your LinkedIn profile using saved session
- Scroll through posts to load them
- Extract post data using browser-use LLM
- Handle infinite scroll pagination
- Return structured data

**Implementation Details**:
Create `src/ingestion/linkedin.py`:
````python
async def scrape_linkedin_posts(session: BrowserSession, max_posts: int = 50) -> List[Dict]:
    """
    Scrape posts from LinkedIn profile.
    
    Returns:
        List of dicts with:
        - post_text: str
        - post_date: datetime
        - likes: int
        - comments: int
        - shares: int
        - post_url: str
    """
    agent = Agent(
        task=f"""
        1. Go to my LinkedIn profile
        2. Scroll through posts and extract data for last {max_posts} posts
        3. For each post, extract: text, date, likes, comments, shares, URL
        4. Return as structured JSON list
        """,
        llm=claude_instance
    )
    result = await agent.run()
    return parse_result(result)
````

**Success Criteria**:
- [ ] Navigates to your LinkedIn profile
- [ ] Extracts at least 10 recent posts
- [ ] All fields captured correctly
- [ ] Handles LinkedIn's UI quirks
- [ ] No manual intervention needed
- [ ] Runs successfully in headless mode

**Questions for User**:
1. What's your LinkedIn profile URL?
2. Should it scrape only original posts or also reposts/comments?

---

### Task 5.4: LinkedIn Incremental Sync
**Your Task**: Only scrape NEW LinkedIn posts using state manager

**Requirements**:
- Get last synced post date from state manager
- Instruct browser-use to only extract newer posts
- Stop scrolling when reaching old posts
- Update state after successful scrape

**Implementation Details**:
Enhance `src/ingestion/linkedin.py`:
````python
async def scrape_new_linkedin_posts(session: BrowserSession, state_manager: StateManager) -> List[Dict]:
    """
    Scrape only new posts since last sync.
    """
    last_sync = state_manager.get_last_sync("linkedin")
    
    agent = Agent(
        task=f"""
        1. Go to my LinkedIn profile
        2. Extract posts newer than {last_sync}
        3. Stop when you reach posts older than {last_sync}
        4. Return as JSON list
        """,
        llm=claude_instance
    )
    
    new_posts = await agent.run()
    return parse_result(new_posts)
````

**Success Criteria**:
- [ ] First run gets all available posts
- [ ] Second run gets zero posts (if no new posts)
- [ ] State updated with latest post date
- [ ] Doesn't unnecessarily scroll through old posts
- [ ] Efficient (stops early when possible)

---

### Task 5.5: LinkedIn to Bedrock Pipeline
**Your Task**: Complete end-to-end LinkedIn ingestion pipeline

**Requirements**:
- Orchestrate: scrape → classify → enrich → ingest
- Handle errors gracefully
- Log progress
- Update state on success

**Implementation Details**:
Create `scripts/sync_linkedin.py`:
````python
async def sync_linkedin_to_bedrock():
    """
    Full pipeline for LinkedIn ingestion.
    """
    # 1. Load session
    session = BrowserSession("linkedin", "linkedin_session.json")
    
    # 2. Scrape new posts
    new_posts = await scrape_new_linkedin_posts(session, state_manager)
    
    # 3. Process each post
    for post in new_posts:
        classification = classify_content(post["post_text"], "linkedin")
        enriched = enrich_metadata(post)
        doc_id = generate_doc_id("linkedin", post)
        bedrock_client.ingest_document(doc_id, post, {**enriched, **classification})
    
    # 4. Update state
    state_manager.update_last_sync("linkedin", latest_post_date)
````

**Success Criteria**:
- [ ] All LinkedIn posts ingested to Bedrock KB
- [ ] No duplicates created
- [ ] Engagement data preserved
- [ ] Can search posts via Letta
- [ ] Can query "show my high-performing LinkedIn posts"

---

### Task 5.6: Twitter/X Authentication Setup
**Your Task**: Set up persistent Twitter login for automation

**Requirements**:
- Same as Task 5.2 but for Twitter/X
- Handle Twitter's authentication flow
- Save and reuse session

**Success Criteria**:
- [ ] Can log into Twitter through browser-use
- [ ] Session persists between runs
- [ ] Works in headless mode

---

### Task 5.7: Twitter/X Post Scraper
**Your Task**: Use browser-use to scrape your tweets

**Requirements**:
- Navigate to your Twitter profile
- Extract tweets with engagement metrics
- Handle Twitter's infinite scroll
- Return structured data

**Implementation Details**:
Create `src/ingestion/twitter.py` similar to LinkedIn scraper.

**Success Criteria**:
- [ ] Extracts recent tweets correctly
- [ ] All engagement metrics captured (likes, retweets, replies, views)
- [ ] Handles threads appropriately
- [ ] No manual intervention needed

**Questions for User**:
1. What's your Twitter/X username?
2. Should threads be kept as single items or split?

---

### Task 5.8: Twitter Incremental Sync
**Your Task**: Only scrape NEW tweets using state manager

**Requirements**:
- Same pattern as LinkedIn incremental sync
- Efficient scrolling (stop when reaching old tweets)

**Success Criteria**:
- [ ] First run gets all tweets
- [ ] Subsequent runs only get new tweets
- [ ] State updated correctly

---

### Task 5.9: Twitter to Bedrock Pipeline
**Your Task**: Complete Twitter ingestion pipeline

**Requirements**:
- Full pipeline: scrape → classify → enrich → ingest
- Same structure as LinkedIn pipeline

**Implementation Details**:
Create `scripts/sync_twitter.py`

**Success Criteria**:
- [ ] All tweets in Bedrock KB
- [ ] Can query via Letta
- [ ] Twitter voice distinct from LinkedIn

---

## Phase 6: Fathom Transcripts Ingestion

### Task 6.1: Fathom API Setup
**Your Task**: Connect to Fathom API and test transcript retrieval

**Requirements**:
- Get Fathom API credentials
- Test authentication
- Fetch list of meetings
- Retrieve one transcript

**Implementation Details**:
Create `src/ingestion/fathom.py`:
````python
class FathomClient:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.fathom.video"
    
    def list_meetings(self, start_date: str, end_date: str) -> List[Dict]:
        """List meetings in date range."""
        pass
    
    def get_transcript(self, meeting_id: str) -> Dict:
        """Get full transcript for a meeting."""
        pass
````

**Success Criteria**:
- [ ] Can authenticate with Fathom API
- [ ] Can list recent meetings
- [ ] Can fetch full transcript
- [ ] Metadata included (participants, date, duration)

**Questions for User**:
1. Do you have Fathom API access already?
2. Should we use webhooks or polling?

---

### Task 6.2: Fathom Metadata Extraction
**Your Task**: Extract rich metadata from meeting transcripts

**Requirements**:
- Use Claude to analyze transcript
- Extract customer names and companies
- Identify key topics discussed
- Extract important quotes/insights
- Summarize action items

**Implementation Details**:
Enhance `src/processing/classifier.py`:
````python
def extract_meeting_metadata(transcript: str) -> Dict:
    """
    Analyze meeting transcript for metadata.
    
    Returns:
        {
            "participants": ["John Doe", "Jane Smith"],
            "customer_company": "Acme Corp",
            "key_topics": ["cold start", "pricing", "integration"],
            "insights": ["Customer loves feature X", ...],
            "action_items": ["Send pricing proposal", ...]
        }
    """
    pass
````

**Success Criteria**:
- [ ] Accurately identifies participants
- [ ] Extracts relevant topics
- [ ] Summarizes key insights
- [ ] Handles long transcripts (chunking if needed)

---

### Task 6.3: Fathom to Bedrock Pipeline
**Your Task**: Complete Fathom ingestion pipeline

**Requirements**:
- Full pipeline: fetch → extract metadata → classify → ingest
- Special handling for customer information
- Privacy considerations

**Implementation Details**:
Create `scripts/sync_fathom.py`

**Success Criteria**:
- [ ] All transcripts in Bedrock KB
- [ ] Customer metadata searchable
- [ ] Can query "what did customers say about X?"
- [ ] Privacy concerns addressed

**Questions for User**:
1. Any customer data that should be redacted?
2. How should we handle very long transcripts?

---

## Phase 7: Browser Consumption Tracking

### Task 7.1: Browser History Access
**Your Task**: Read Chrome browser history programmatically

**Requirements**:
- Access Chrome history database (SQLite)
- Extract URLs with timestamps
- Filter out noise (Gmail, Slack, etc.)
- Return substantive content URLs

**Implementation Details**:
Create `src/ingestion/browser.py`:
````python
def get_browser_history(hours: int = 24) -> List[Dict]:
    """
    Get browser history from last N hours.
    
    Returns:
        List of dicts with: url, title, visit_time, visit_duration
    """
    # Find Chrome history DB location
    # Query for recent visits
    # Filter out transactional sites
    pass
````

**Success Criteria**:
- [ ] Can read Chrome history database
- [ ] Extracts last 24 hours of visits
- [ ] Filters out Gmail, Slack, etc.
- [ ] Returns only articles/videos
- [ ] Works on macOS and Linux

**Questions for User**:
1. Which browser do you primarily use? (Chrome, Firefox, Safari?)
2. Any specific sites to always exclude?

---

### Task 7.2: Content Extraction from URLs
**Your Task**: Extract article/video content from URLs

**Requirements**:
- Given URL, extract main content
- Handle articles (extract text)
- Handle videos (extract title, description)
- Handle paywalls gracefully
- Return clean, structured content

**Implementation Details**:
Enhance `src/ingestion/browser.py`:
````python
def extract_url_content(url: str) -> Optional[Dict]:
    """
    Extract content from URL.
    
    Returns:
        {
            "url": str,
            "title": str,
            "content": str,
            "content_type": "article" or "video",
            "author": str (optional),
            "published_date": str (optional)
        }
    """
    pass
````

**Success Criteria**:
- [ ] Extracts clean text from common sites
- [ ] Handles YouTube videos
- [ ] Handles Medium articles
- [ ] Gracefully handles paywalls
- [ ] Returns None for non-content pages

**Tech Stack Decision Point**:
- **Content extraction**: newspaper3k, trafilatura, or beautiful soup?

---

### Task 7.3: Consumption Curation System
**Your Task**: Analyze browser history and suggest content to remember

**Requirements**:
- Process yesterday's browser history
- Score each URL by relevance
- Use pattern analysis (topics you frequently read)
- Generate top 10 suggestions with reasoning
- Present for user approval

**Implementation Details**:
Create `scripts/curate_consumption.py`:
````python
def generate_curation_suggestions(history: List[Dict]) -> List[Dict]:
    """
    Analyze history and suggest content to remember.
    
    For each URL:
    1. Extract content
    2. Classify relevance (using Claude)
    3. Score based on:
       - Dwell time
       - Topic relevance to your work
       - Pattern matching (repeated topics)
    4. Return top 10 with reasoning
    """
    pass
````

**Success Criteria**:
- [ ] Suggestions are actually relevant
- [ ] Clear explanation for each suggestion
- [ ] Easy to approve/reject
- [ ] Runs nightly automatically
- [ ] Presents results in morning digest

**Questions for User**:
1. What makes content worth remembering in your view?
2. Should certain topics be prioritized?

---

### Task 7.4: Consumption to Bedrock Pipeline
**Your Task**: Store approved consumption content

**Requirements**:
- Take approved items from curation
- Classify and enrich like created content
- Tag as "consumed" source
- Assign importance score (typically lower than created)
- Ingest to Bedrock KB

**Implementation Details**:
Integrate with existing pipeline, just mark source="consumed"

**Success Criteria**:
- [ ] Approved content stored in Bedrock
- [ ] Tagged as "consumed"
- [ ] Searchable but distinct from created content
- [ ] Can query "what have I been reading about X?"

---

## Phase 8: Scheduled Automation

### Task 8.1: Job Scheduler Setup
**Your Task**: Set up scheduled tasks for nightly ingestion

**Requirements**:
- Configure jobs to run automatically
- Schedule at appropriate times
- Log execution and errors
- Send notifications on failure (optional)

**Implementation Details**:
Create systemd timer units or cron jobs:
````bash
# Cron schedule
0 23 * * * /path/to/venv/bin/python /path/to/rumi/scripts/sync_linkedin.py
5 23 * * * /path/to/venv/bin/python /path/to/rumi/scripts/sync_twitter.py
10 23 * * * /path/to/venv/bin/python /path/to/rumi/scripts/sync_blog.py
15 23 * * * /path/to/venv/bin/python /path/to/rumi/scripts/curate_consumption.py
0 * * * * /path/to/venv/bin/python /path/to/rumi/scripts/sync_fathom.py
````

**Success Criteria**:
- [ ] Jobs run automatically at scheduled times
- [ ] Logs show successful execution
- [ ] Errors are logged and visible
- [ ] Can manually trigger jobs for testing

**Tech Stack Decision Point**:
- **Scheduler**: cron (simple) or systemd timers (more control)?
- **Orchestration**: Keep jobs separate or use task queue (Celery)?

**Questions for User**:
1. Should failed jobs retry automatically?
2. Do you want notifications on success/failure?

---

### Task 8.2: AWS EC2 Deployment
**Your Task**: Deploy all Rumi components to AWS EC2

**DECISION MADE**: **t3.small instance (~$15/month)** with Ubuntu, CloudWatch logging, systemd for service management

**Requirements**:
- Set up EC2 instance (t3.small, Ubuntu 22.04 LTS)
- Install all dependencies (Python 3.11+, browsers, etc.)
- Deploy code to server
- Configure scheduled jobs (cron)
- Set up CloudWatch logging
- Ensure browser-use works headlessly
- Run Letta agent persistently
- Run FastAPI backend as service

**Implementation Details**:
I'll provide a step-by-step deployment script and guide you through:

1. **Launch EC2 instance** (via AWS Console)
   - Instance type: t3.small (2 vCPU, 2GB RAM)
   - OS: Ubuntu 22.04 LTS
   - Storage: 20GB gp3
   - Security group: Allow SSH (22), HTTP (80), HTTPS (443), API (8000)

2. **Setup script** (I'll create `scripts/ec2_setup.sh`):
````bash
#!/bin/bash
# Install Python 3.11+
# Install Playwright and browsers
# Install CloudWatch agent
# Clone repo from GitHub
# Set up virtual environment
# Install dependencies
# Configure environment variables (from Secrets Manager)
# Set up systemd services for FastAPI and Letta
# Set up cron jobs for scrapers
````

3. **Systemd services**:
   - `rumi-api.service` (FastAPI backend)
   - `rumi-letta.service` (Letta agent)

4. **Cron schedule**:
````cron
0 23 * * * /home/ubuntu/rumi/venv/bin/python /home/ubuntu/rumi/scripts/sync_blog.py
5 23 * * * /home/ubuntu/rumi/venv/bin/python /home/ubuntu/rumi/scripts/sync_linkedin.py
10 23 * * * /home/ubuntu/rumi/venv/bin/python /home/ubuntu/rumi/scripts/sync_twitter.py
0 * * * * /home/ubuntu/rumi/venv/bin/python /home/ubuntu/rumi/scripts/sync_fathom.py
````

**Success Criteria**:
- [ ] EC2 instance launched and accessible via SSH
- [ ] All dependencies installed correctly
- [ ] Code deployed from GitHub
- [ ] Letta agent running as systemd service
- [ ] FastAPI backend running and accessible
- [ ] Scheduled jobs configured in cron
- [ ] Browser-use works in headless mode
- [ ] CloudWatch receiving logs
- [ ] Services auto-restart on failure (systemd)
- [ ] Services auto-start on reboot (systemd)

**Security**:
- [ ] API keys stored in AWS Secrets Manager (not in code)
- [ ] Security group configured (minimal ports)
- [ ] SSH key-based authentication only
- [ ] IAM role attached to EC2 (for AWS service access)

**Deployment Process**:
I'll guide you through each step with screenshots/commands as needed. We'll do this together so you understand the setup.

---

## Phase 9: Chat Interface

### Task 9.1: Backend API Design
**Your Task**: Design REST API for Rumi chat interface

**Requirements**:
- Define API endpoints
- Document request/response formats
- Consider WebSocket for real-time chat
- Plan error handling

**API Specification**:
````
POST /chat/message
  Request: { "message": "string", "session_id": "string" }
  Response: { "response": "string", "sources": [...] }

GET /chat/history
  Response: { "messages": [...] }

GET /digest
  Response: { "new_content": [...], "ideas": [...], "curation": [...] }

POST /curation/approve
  Request: { "item_id": "string" }
  Response: { "success": true }
````

**Success Criteria**:
- [ ] Clear API contract defined
- [ ] All endpoints documented (OpenAPI spec)
- [ ] Error responses defined
- [ ] Authentication considered

**Questions for User**:
1. Should the API be public or require authentication?
2. WebSocket for real-time chat or polling?

---

### Task 9.2: Backend Implementation
**Your Task**: Build FastAPI backend for Rumi

**Requirements**:
- Implement all API endpoints
- Integrate with Letta agent
- Handle sessions and history
- Error handling and validation
- CORS configured for frontend

**Implementation Details**:
Create `src/api/main.py`:
````python
from fastapi import FastAPI
from letta import LettaClient

app = FastAPI()
letta_client = LettaClient()

@app.post("/chat/message")
async def chat(message: str, session_id: str):
    """Send message to Letta agent and return response."""
    response = letta_client.send_message(agent_id, message)
    return {"response": response}

# ... other endpoints
````

**Success Criteria**:
- [ ] FastAPI server runs successfully
- [ ] All endpoints implemented
- [ ] Can send message and get response
- [ ] Letta agent properly invoked
- [ ] Errors handled gracefully
- [ ] API documentation auto-generated

---

### Task 9.3: Frontend Setup
**Your Task**: Create Next.js frontend with chat interface for Rumi

**Requirements**:
- Next.js 14+ app
- Chat UI component
- Message history display
- Connect to backend API
- Responsive design

**Implementation Details**:
````typescript
// app/page.tsx
export default function ChatPage() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  
  const sendMessage = async () => {
    const response = await fetch('/api/chat/message', {
      method: 'POST',
      body: JSON.stringify({ message: input })
    });
    const data = await response.json();
    setMessages([...messages, { user: input, assistant: data.response }]);
  };
  
  return <ChatInterface messages={messages} onSend={sendMessage} />;
}
````

**Success Criteria**:
- [ ] Next.js app runs successfully
- [ ] Chat UI is functional and clean
- [ ] Can type and send messages
- [ ] Responses display correctly
- [ ] Message history persists in session
- [ ] Loading states handled

**Questions for User**:
1. Any specific design preferences?
2. Should chat history persist across sessions?

---

### Task 9.4: Morning Digest UI
**Your Task**: Add digest view to Rumi interface

**Requirements**:
- Component to display digest
- Show new content summary
- Show content ideas
- Show curation suggestions
- Interactive approval for curation

**Implementation Details**:
````typescript
// components/Digest.tsx
export function Digest() {
  const { data } = useSWR('/api/digest');
  
  return (
    <div>
      <NewContentSummary items={data.new_content} />
      <ContentIdeas ideas={data.ideas} />
      <CurationReview items={data.curation} onApprove={handleApprove} />
    </div>
  );
}
````

**Success Criteria**:
- [ ] Digest component renders correctly
- [ ] Loads data from backend on startup
- [ ] Can approve/reject curation items
- [ ] Clicking content ideas opens chat with context
- [ ] Updates after actions taken

---

## Phase 10: Testing & Refinement

### Task 10.1: Voice Tuning
**Your Task**: Refine voice profiles for better content generation

**Requirements**:
- Test generation with current voice profiles
- Identify voice mismatches
- Iterate on voice prompts and examples
- Compare generated vs actual content

**Process**:
1. Generate 10 LinkedIn posts in your voice
2. Compare to your actual posts
3. Identify discrepancies (tone, structure, word choice)
4. Update voice profiles
5. Repeat until satisfied

**Success Criteria**:
- [ ] Generated LinkedIn content sounds like you
- [ ] Generated tweets sound like you
- [ ] Generated blog content sounds like you
- [ ] Minimal editing needed
- [ ] Platform differences preserved

---

### Task 10.2: End-to-End Testing
**Your Task**: Test all Rumi workflows comprehensively

**Test Cases**:
1. **Ingestion cycle**: Run all scrapers, verify content in Bedrock
2. **Query accuracy**: Test various searches, verify relevance
3. **Content generation**: Generate content, evaluate quality
4. **Curation workflow**: Review suggestions, approve/reject, verify storage
5. **Incremental sync**: Verify no duplicates on repeated runs
6. **Error handling**: Simulate failures at each step

**Success Criteria**:
- [ ] All test cases pass
- [ ] No critical bugs found
- [ ] Performance acceptable
- [ ] Error messages clear and helpful
- [ ] Logs show detailed execution flow

---

### Task 10.3: Documentation
**Your Task**: Write comprehensive documentation for Rumi

**Required Documentation**:
1. **README.md**: User-facing overview for GitHub (final step)
2. **SETUP.md**: Step-by-step setup instructions
3. **ARCHITECTURE.md**: System design and components
4. **API.md**: API endpoint documentation
5. **TROUBLESHOOTING.md**: Common issues and solutions
6. **DEPLOYMENT.md**: EC2 deployment guide

**Success Criteria**:
- [ ] All documentation complete and clear
- [ ] Someone else could set up the system
- [ ] Common issues documented
- [ ] Architecture diagrams included

---

## Task Execution Template

For each task, follow this process:

### 1. Pre-Implementation
````markdown
## Task X.Y: [Task Name]

### Technical Approach
I propose implementing this using:
- [Library/tool choice] because [reason]
- [Architecture decision] because [reason]
- [Alternative considered] but rejected because [reason]

### Questions Before Starting
1. [Question 1]
2. [Question 2]

### Estimated Complexity
- Time: [hours/days]
- Dependencies: [other tasks needed first]
- Risks: [potential issues]

**Waiting for approval to proceed...**
````

### 2. Implementation
````markdown
### Implementation Log

**Started**: [date/time]

**Changes Made**:
- Created `path/to/file.py`
- Modified `path/to/other.py`
- Added dependency: package-name

**Code Snippets**: [key functions]

**Challenges**:
- [Challenge 1]: [how solved]
````

### 3. Testing
````markdown
### Test Results

**Test Commands Run**:
```bash
python -m pytest tests/test_module.py
python scripts/test_integration.py
```

**Success Criteria Status**:
- [x] Criterion 1: Passed
- [x] Criterion 2: Passed
- [ ] Criterion 3: Failed - [explanation]

**Next Steps**: [what needs fixing]
````

### 4. Completion
````markdown
### Task Complete

**Files Modified**:
- `src/module/file.py`
- `tests/test_file.py`
- `requirements.txt`

**Learnings**:
- [What worked well]
- [What was challenging]
- [What would I do differently]

**Ready for Next Task**: [Yes/No]
````

---

## Getting Started

**Your First Action**:
1. Read this entire document
2. Ask any clarifying questions about the overall approach
3. Start with Task 0.1: Project Structure Setup
4. Wait for user approval before each task
5. Document everything as you go

**Remember**:
- Never make assumptions - ask when unclear
- Explain your technical decisions
- Test thoroughly before moving on
- Keep the user informed of progress
- It's okay to suggest better approaches

**Let's build Rumi together!**