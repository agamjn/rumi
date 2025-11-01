# Claude Code Instructions for Rumi

## Project Context
You are building **Rumi**, a Personal Content AI Assistant. This is an incremental, educational project where the user wants to understand every decision.

## Core Principles

### 1. Follow the Implementation Plan
- All tasks are defined in `PROJECT.md`
- Work through tasks sequentially (Phase 0 → Phase 10)
- **Never skip to the next task without explicit user approval**
- Reference task numbers when discussing work (e.g., "Task 2.3")

### 2. Communication Style
- **Propose before implementing**: Always explain your approach and wait for approval
- **Explain your decisions**: Why you chose library X over library Y
- **Show, don't just tell**: Include code snippets in explanations
- **Be honest about uncertainty**: Say "I'm not sure" rather than guessing
- **Ask clarifying questions**: When requirements are ambiguous

### 3. Code Quality Standards

**Python Style**:
- Follow PEP 8 strictly
- Use type hints for all function signatures
- Google-style docstrings for all functions/classes
- Maximum line length: 100 characters

**Error Handling**:
- Always use try/except blocks for external calls (API, file I/O, network)
- Log errors using the centralized logger
- Provide clear error messages

**Testing**:
- Write tests for every module (use pytest)
- Aim for >80% code coverage
- Test both happy paths and error cases
- No task is complete without tests

**Logging**:
- Use the centralized logger from `src/config/logger.py`
- Log at appropriate levels (DEBUG, INFO, WARNING, ERROR)
- Include context in log messages (function name, key variables)

### 4. File Organization
```
src/          → Reusable application code
scripts/      → Executable scripts (sync jobs, utilities)
tests/        → Test files (mirror src/ structure)
docs/         → Documentation
.claude/      → Claude Code configuration (this file)
```

**Import Rules**:
- Use absolute imports: `from src.config import settings`
- Never use relative imports
- Keep imports organized: stdlib, third-party, local

### 5. Development Workflow

**Before Starting a Task**:
1. Read the full task description in `PROJECT.md`
2. Check "Tech Stack Decision Points"
3. Propose your approach with reasoning
4. Wait for user approval
5. Ask any clarifying questions

**While Implementing**:
1. Create/modify files as needed
2. Write comprehensive docstrings
3. Add logging at key decision points
4. Handle errors gracefully
5. Follow the code quality standards above

**After Implementation**:
1. Write unit tests
2. Run tests: `pytest tests/ -v`
3. Check code style: `black src/ && flake8 src/`
4. Update `requirements.txt` if you added dependencies
5. Document what you built
6. Show the user your work
7. Ask if ready to proceed to next task

### 6. Technical Decisions

**When You Need to Make a Choice**:
- Present options clearly (Option A vs Option B)
- Explain pros/cons of each
- Make a recommendation with reasoning
- Wait for user decision
- Document the decision

**Example**:
```
For state management, I see three options:

Option A: SQLite file
  Pros: Simple, no setup needed, works locally
  Cons: Tied to one server, no built-in replication

Option B: AWS DynamoDB
  Pros: Managed, accessible anywhere, auto-scaling
  Cons: More complex, costs money, overkill for simple state

Option C: Bedrock KB handles deduplication
  Pros: No separate state system, simpler architecture
  Cons: Less control, depends on Bedrock behavior

I recommend Option C because [reasoning].
What do you prefer?
```

### 7. What NOT to Do

❌ Don't skip tests
❌ Don't proceed without approval
❌ Don't make major architectural changes without discussion
❌ Don't use hard-coded values (use config)
❌ Don't commit secrets or `.env` files
❌ Don't leave commented-out code
❌ Don't assume requirements - ask if unclear

### 8. Common Commands
```bash
# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_ingestion/test_blog.py -v

# Check code formatting
black src/ tests/ scripts/
flake8 src/ tests/ scripts/

# Type checking (if using mypy)
mypy src/

# Run a script
python scripts/sync_blog.py

# Install dependencies
pip install -r requirements.txt
```

### 9. External Dependencies

**API Keys Required** (store in `.env`):
- `ANTHROPIC_API_KEY`: For Claude API
- `AWS_ACCESS_KEY_ID` & `AWS_SECRET_ACCESS_KEY`: For Bedrock
- `FATHOM_API_KEY`: For meeting transcripts

**Never commit these to git**

### 10. Project-Specific Context

**About Rumi**:
- Personal content assistant for founders/creators
- Learns from user's own work (not generic knowledge)
- Separates work vs personal content
- Daily digest + chat interface

**Key Technical Components**:
- **Letta**: Agent orchestration and memory blocks
- **AWS Bedrock KB**: Content storage with RAG
- **browser-use**: LLM-powered scraping for LinkedIn/Twitter
- **FastAPI**: Backend API
- **Next.js**: Frontend chat interface

**User's Context** (personalize responses):
- Building Fastpull (lazy-loading snapshotter)
- Founder at Tensorfuse
- Technical background (understands ML/infrastructure)
- Wants to learn, not just get working code

### 11. When Things Go Wrong

**If a test fails**:
- Don't just say "fix the test"
- Investigate why it failed
- Explain the root cause
- Propose a fix
- Verify the fix works

**If you're stuck**:
- Admit it clearly
- Explain what you've tried
- Ask specific questions
- Suggest where to look for answers

**If requirements conflict**:
- Point out the conflict
- Propose how to resolve it
- Wait for user decision

### 12. Task Completion Checklist

Before saying a task is complete:

- [ ] Code written and follows style guide
- [ ] Docstrings added to all functions/classes
- [ ] Error handling implemented
- [ ] Logging added at key points
- [ ] Unit tests written and passing
- [ ] Integration tests (if applicable) passing
- [ ] `requirements.txt` updated
- [ ] No hard-coded values
- [ ] All "Success Criteria" from PROJECT.md met
- [ ] Code formatted with black
- [ ] User has reviewed and approved

### 13. Current Status

**Current Task**: [To be filled by user]
**Completed Tasks**: [To be updated as we go]
**Blockers**: [Any open questions or blockers]

---

## Remember

This is a **learning project**. The user wants to:
- Understand every decision
- Learn the tech stack
- Have control over the implementation
- Build something maintainable

Take your time. Explain thoroughly. Ask questions. Build it right.

**Good luck! Let's build Rumi together. 🚀**
```

---

## Summary: What Files Go Where
```
rumi/
├── OVERVIEW.md          ← File 2: High-level user-facing description
├── PROJECT.md           ← File 3: Detailed technical tasks (the big one)
├── .claude/
│   └── instructions.md  ← File 4: Rules for Claude Code
└── README.md            ← File 1: Skip for now (write at end)