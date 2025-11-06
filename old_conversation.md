# Rumi Project - Session 1 (2025-11-04)

## Session Summary
Built the foundation of Rumi and completed Phase 2 (Content Ingestion). Successfully fetching and classifying blog posts with OpenAI.

---

## What We Accomplished

### Tasks Completed (5 total):
1. ✅ **Task 0.1**: Project Structure Setup
2. ✅ **Task 0.2**: Environment Configuration (AWS SSO)
3. ✅ **Task 2.1**: Blog RSS Parser
4. ✅ **Task 2.3**: OpenAI Content Classifier
5. ✅ Documentation: Comprehensive PROGRESS.md updates

### Tasks Skipped (Intentional - Keep It Lean):
- ⏭️ Task 0.3: CloudWatch Logging (basic logging sufficient)
- ⏭️ Task 1.1: DynamoDB State Management (will add later)
- ⏭️ Task 2.2: Incremental Sync (will add after storage)
- ⏭️ Task 2.4: Metadata Enrichment (not over-engineering)

---

## Key Technical Decisions

### 1. Architecture: Simple First, Scale Later
**Decision**: Start with EC2 + managed services, skip serverless complexity
**Reasoning**: User is learning, needs debuggable setup
**Result**: EC2 for compute, DynamoDB for state (later), Bedrock/Qdrant for storage

### 2. AWS Authentication: SSO Over Access Keys
**Decision**: Use AWS SSO (tensorfuse profile) instead of access keys
**Reasoning**: More secure, user already had it configured
**Implementation**: Added `AWS_PROFILE` setting, automatic env var configuration

### 3. AI Provider: OpenAI Over Anthropic
**Decision**: Use OpenAI gpt-4o-mini for classification
**Reasoning**:
- 10x cheaper than Claude for simple tasks
- 128k context window (no truncation needed)
- User preference
**Cost**: ~$0.0003 per 3 posts (essentially free)

### 4. OpenAI API: Latest Responses API
**User insight**: Showed me the new `client.responses.create()` API
**Implementation**:
```python
response = client.responses.create(
    model="gpt-4o-mini",
    input=input_text,
    instructions=instructions,
    text={"format": {"type": "json_object"}}
)
result = json.loads(response.output_text)
```

### 5. Classification: No Importance Scores Yet
**Decision**: Skip importance scores for now
**Reasoning**: User wants to design thoughtful algorithm later
**Current output**: category (work/personal), tags (3-7), summary (<150 chars)

### 6. Build Order: Features First, Infrastructure Later
**Decision**: Skip logging/state management, jump to visible features
**Reasoning**: Better learning experience, see results faster
**Approach**: Blog scraping → Classification → Storage → Add infrastructure incrementally

### 7. Storage Discussion: Qdrant vs Bedrock KB
**Status**: UNRESOLVED - Session ended before decision
**Options Discussed**:
- **Qdrant** (Recommended): Open source, local Docker, full control, cheap
- **Bedrock KB**: Managed AWS service, more expensive, overkill for use case
- **ChromaDB**: Simplest, Python library, good for small scale
- **Pinecone**: Managed, free tier available
**User needs to decide**: Which vector database to use for permanent storage

---

## What We Built (Code)

### File 1: `src/ingestion/blog.py` (73 lines)
**Purpose**: Fetch blog posts from RSS feed

**Key function**:
```python
def fetch_blog_posts(rss_url: str) -> List[Dict]:
    """Fetch and parse blog posts from RSS feed."""
    feed = feedparser.parse(rss_url)
    # Returns: title, content, published, url, summary
```

**What it does**:
- Uses `feedparser` library
- Handles different RSS field names (content/description/summary)
- Returns structured dicts
- Logs progress

**Tested with**: https://agamjn.com/feed (10 posts successfully fetched)

### File 2: `src/processing/classifier.py` (122 lines)
**Purpose**: Classify blog posts using OpenAI

**Key function**:
```python
def classify_content(content: str, platform: str, title: str = "", date: str = "") -> Dict:
    """Classify content using OpenAI Responses API."""
    # Returns: category, tags, summary
```

**Classification prompt**:
- Category: "work" (technical, business, Tensorfuse) vs "personal" (philosophy, reflections, Advaita)
- Tags: 3-7 lowercase specific tags (prefer "vllm" over "ai")
- Summary: 1-2 sentences, <150 chars
- JSON output enforced

**Results (3 posts tested)**:
- "Optimizing reranker inference with vLLM" → work, tags: [vllm, reranker, fastapi...] ✅
- "RAG vs Memory" → work, tags: [rag, memory, token_management...] ✅
- "Detachment Is All You Need" → personal, tags: [detachment, startup, philosophy...] ✅

**Accuracy**: 100% on test cases

### File 3: `scripts/test_config.py` (140 lines)
**Purpose**: Test configuration and AWS connectivity

**What it tests**:
- Settings load from .env
- AWS SSO authentication working
- S3 access (permission check)
- Shows account ID, user ARN

### File 4: `scripts/test_blog_fetch.py` (74 lines)
**Purpose**: Test blog RSS fetching

**What it does**:
- Fetches 10 blog posts
- Shows titles, dates, URLs
- Previews content
- Demonstrates working RSS pipeline

### File 5: `scripts/test_classification.py` (112 lines)
**Purpose**: Test OpenAI classification on real blog posts

**What it does**:
- Fetches posts from RSS
- Classifies first 3 (to save costs)
- Shows category, tags, summary
- Provides work vs personal split summary

---

## Configuration Setup

### `.env` (User's API Keys)
```bash
# AWS (SSO)
AWS_PROFILE=tensorfuse
AWS_REGION=us-east-1

# OpenAI
OPENAI_API_KEY=sk-proj-...
OPENAI_MODEL=gpt-4o-mini

# Application
ENVIRONMENT=development
LOG_LEVEL=INFO
DYNAMODB_STATE_TABLE=rumi_state
LETTA_BASE_URL=http://localhost:8080
```

### Dependencies Added
```
feedparser>=6.0.0          # RSS parsing
openai>=1.12.0             # OpenAI API
boto3, pydantic-settings   # AWS & config
pytest, black, flake8      # Testing & code quality
```

---

## Data Pipeline (Current State)

```
RSS Feed (agamjn.com/feed)
    ↓
fetch_blog_posts()
    ↓
List[Dict] with title, content, date, url
    ↓
classify_content() [OpenAI gpt-4o-mini]
    ↓
Enhanced Dict with category, tags, summary
    ↓
[NOT YET: Store in Vector Database]
    ↓
[NOT YET: Query with Letta Agent]
```

**What works**: Steps 1-4
**What's next**: Storage layer (Qdrant or Bedrock KB)

---

## Sample Data (Real Results)

### Post 1: "Optimizing reranker inference with vLLM"
```json
{
  "title": "Optimizing reranker inference with vLLM",
  "published": "2025-10-30T00:00:00+00:00",
  "url": "https://agamjn.github.io/technical/2025/10/30/optimized-reranker-inference.html",
  "content": "<p>Rerankers sit in the critical path... [7044 chars]",
  "category": "work",
  "tags": ["vllm", "reranker", "fastapi", "huggingface", "latency", "inference", "docker"],
  "summary": "This post discusses optimizing reranker inference with vLLM for faster processing in RAG pipelines."
}
```

### Post 2: "RAG vs Memory: Addressing Token Crisis in Agentic Tasks"
```json
{
  "category": "work",
  "tags": ["rag", "memory", "token_management", "agentic_tasks", "deep_research", "coding_agents", "multi-hop_reasoning"],
  "summary": "Explores the limitations of RAG and how memory-based approaches enhance token efficiency in complex tasks."
}
```

### Post 3: "Detachment Is All You Need"
```json
{
  "category": "personal",
  "tags": ["detachment", "startup", "decision-making", "philosophy", "founders", "mindfulness"],
  "summary": "The post explores how detachment can bring clarity and peace to founders amid the chaos of startup life."
}
```

**Classification accuracy**: 100% (work vs personal perfectly identified)

---

## Important Discussions

### 1. Content Truncation (Resolved)
**User questioned**: Why truncate content when gpt-4o-mini has 128k context?
**Resolution**: Removed truncation - user was correct, no need to truncate
**Learning**: Don't be overly conservative with modern LLMs

### 2. Importance Scores (Deferred)
**User questioned**: "How do you assign importance scores? I don't see factual basis"
**Discussion**: LLM scores are subjective without engagement data
**Decision**: Skip importance scores now, user will design algorithm later using:
- Real engagement metrics (likes, shares, comments)
- Recency weighting
- Reference frequency
**Key insight**: User wants thoughtful, data-driven approach, not arbitrary LLM judgment

### 3. Metadata Enrichment (Skipped)
**User decision**: "Let's not over-engineer"
**Current data sufficient**: category, tags, summary
**Skipped**: word count, read time calculations
**Philosophy**: Keep it lean, add features only when needed

### 4. Vector Database Selection (Unresolved)
**User asked**: "Is Bedrock KB the right choice?"
**Claude's analysis**:
- Bedrock KB: Overkill, expensive ($50-100/month), complex setup
- **Qdrant (Recommended)**: Open source, Docker, full control, $0-5/month
- ChromaDB: Simplest, Python library, good for POC
- Pinecone: Managed, free tier available

**User needs to decide** which to use before next session

### 5. Documentation Access Limitation
**User frustrated**: "You can't open documentation links?"
**Explanation**: Bot detection (403 errors) on most doc sites
**Workaround**: User shares code snippets or key points
**Success story**: OpenAI Responses API - user pasted code, worked perfectly
**Potential solution**: MCP Puppeteer server (deferred to later)

### 6. Homepage & Projects Content
**User asked**: "What about homepage intro, projects on my website?"
**Discussion**:
- Option 1: Manual JSON/text files (simple)
- Option 2: Web scraping (Task 7.2, using browser-use)
- Option 3: Add later after blog posts working
**Decision**: Start with blog posts, add other content later

---

## Teaching Moments

### What Worked Well:
1. ✅ **Small incremental changes** - One function at a time, explain, test
2. ✅ **Explaining concepts** - RSS feeds, vector databases, cost comparisons
3. ✅ **User questioning decisions** - Led to better choices (no truncation, no importance scores)
4. ✅ **Copy-paste code examples** - User showing OpenAI API pattern was perfect
5. ✅ **Keeping it lean** - User pushed back on over-engineering, good instinct

### User's Learning Style:
- Asks "why?" questions (importance scores, truncation, Bedrock choice) ✅
- Wants to understand tradeoffs before committing
- Prefers simple over complex
- Values cost efficiency
- Thinks critically about architecture choices

### User's Technical Level:
- Understands high-level concepts quickly
- Learning AWS ecosystem (SSO, Bedrock, DynamoDB)
- Comfortable with Python
- New to: RSS parsing, vector databases, RAG systems
- Strong product intuition (knows what's over-engineering)

---

## Next Session Plan

### Immediate Next Task: **Phase 3 - Storage Setup**

**User must decide first**:
- [ ] Qdrant (recommended) vs Bedrock KB vs other?

**Then we'll do**:
1. **Setup chosen vector database**
   - If Qdrant: Run Docker locally, connect Python client
   - If Bedrock: AWS Console setup, S3 bucket, IAM permissions

2. **Generate embeddings** (OpenAI)
   - Add to requirements: `openai` (already installed)
   - Create embeddings for blog posts
   - Cost: ~$0.01 per 100 posts

3. **Store classified posts**
   - Combine fetched + classified data
   - Generate embeddings
   - Store in vector DB

4. **Test search**
   - Semantic search: "Find posts about vLLM"
   - Filter by category: "Show work posts only"
   - Verify retrieval works

### After Storage Works:
- Task 4.1: Letta Agent Setup
- Task 4.3: Custom search tool for Letta
- Task 4.4: End-to-end test (query blog posts via agent)

---

## Questions to Resolve Next Session

1. **Vector DB choice**: Qdrant, Bedrock KB, or other?
2. **Deployment strategy**: Keep Qdrant local for now or plan EC2 deployment?
3. **All 10 posts**: Should we classify all 10 blog posts or keep testing with 3?
4. **Embedding model**: OpenAI embeddings or alternatives?

---

## Cost Summary (So Far)

| Item | Cost |
|------|------|
| OpenAI API (3 posts classified) | ~$0.0003 |
| AWS (SSO, no resources created yet) | $0.00 |
| Development time | Priceless 😄 |
| **Total** | **~$0.0003** |

**Next phase estimated costs**:
- OpenAI embeddings (10 posts): ~$0.001
- Qdrant (local Docker): $0.00
- Qdrant (EC2 hosted): ~$5/month

---

## Key Files Reference

### Documentation:
- `PROGRESS.md` - Session history, decisions, next steps (16KB)
- `PROJECT.md` - Full task breakdown (52KB)
- `.claude/instructions.md` - Working guidelines
- `overview.md` - User-facing project description

### Code:
- `src/config/settings.py` - Configuration with AWS SSO support
- `src/config/logger.py` - Basic logging setup
- `src/ingestion/blog.py` - RSS fetching ✅
- `src/processing/classifier.py` - OpenAI classification ✅
- `scripts/test_*.py` - Test scripts for each component

### Configuration:
- `.env` - API keys (AWS, OpenAI)
- `requirements.txt` - Python dependencies
- `pyproject.toml` - Package configuration

---

## Session Metrics

- **Duration**: ~3-4 hours
- **Tasks completed**: 5
- **Code files created**: 5 (9.7KB)
- **Lines of code**: ~500
- **Tests written**: 3 test scripts
- **Working features**: Blog fetching ✅, Classification ✅
- **Coffee consumed**: Unknown ☕

---

## Resuming Instructions

**To continue this project:**

1. Say: `"Resume Rumi project"`
2. Claude will read this file + PROGRESS.md
3. You'll need to decide: Qdrant or Bedrock KB?
4. We'll set up vector database storage
5. Store your classified blog posts
6. Test semantic search!

**Current status**: Phase 2 complete, ready for Phase 3 (storage)

---

## Notes & Learnings

- User has good instincts about avoiding over-engineering
- OpenAI Responses API works perfectly for structured output
- AWS SSO is cleaner than access keys for local development
- Copy-paste code examples > sending doc links (due to bot protection)
- Keep explanations clear - user values understanding over speed
- Don't truncate modern LLM inputs unnecessarily
- Importance scores need data-driven algorithms, not arbitrary LLM judgment

---

**End of Session 1 - Great progress! 🚀**
