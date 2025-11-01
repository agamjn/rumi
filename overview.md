# Rumi - Personal Content AI Assistant

An AI-powered content assistant that helps you create authentic, engaging content by leveraging your unique work, voice, and ideas.

## What It Does

Rumi acts as your content co-pilot, helping you:

### 1. **Discover Content Ideas from Your Work**
- Automatically scans your recent work (blog posts, social media, customer conversations)
- Identifies unique insights and achievements worth sharing
- Suggests content angles based on what resonates with your audience
- Connects patterns across your work to surface hidden stories

### 2. **Generate Content in Your Voice**
Ask Rumi to write content, and it will:
- Match your LinkedIn voice (professional, story-driven)
- Match your Twitter/X voice (technical, punchy)
- Match your blog voice (in-depth, explanatory)
- Pull context exclusively from YOUR work, not generic AI knowledge
- Reference your actual projects, customer insights, and technical achievements

### 3. **Query Your Personal Knowledge Base**
Chat with Rumi to:
- "Find everything I've written about Fastpull"
- "What patterns do you see in my recent customer conversations?"
- "Show me my highest-performing LinkedIn posts about GPU optimization"
- "What have I been consuming lately about wafer-scale processors?"

### 4. **Daily Content Digest**
Every morning, receive:
- Summary of new work you've created (posts, meetings, blogs)
- 3-5 content ideas based on recent activity
- Suggestions for what consumed content to remember
- Patterns and insights from your recent work

### 5. **Smart Content Curation**
Rumi helps you remember what matters:
- Reviews your browser history nightly
- Suggests 10 articles/videos worth keeping based on pattern analysis
- You review and approve - only what YOU choose gets remembered
- Keeps your "consumption memory" relevant and noise-free

## How You Use It

### Chat Interface
Open the chat and ask natural questions:
- "Write a LinkedIn post about the cold start optimization we achieved"
- "Find me content ideas from my recent customer calls"
- "What should I write about next based on my work?"
- "Generate a thread about token consumption in agentic systems"

### Morning Routine
Start your day with the digest:
- See what's new in your work
- Review content suggestions
- Curate last night's consumed content
- Get inspired for what to share

### Content Creation Workflow
1. Ask for ideas: "What can I write about from my Fastpull work?"
2. Choose an angle: "Tell me more about the lazy-loading innovation"
3. Generate draft: "Write this as a LinkedIn post in my voice"
4. Edit and publish: Make it yours and share

## What Makes It Different

### Your Content, Your Voice
- Trained on YOUR writing style from each platform
- Only uses YOUR work as context (not generic AI knowledge)
- Generates content that sounds like you, not a robot

### Work/Personal Separation
- Understands the difference between your technical work and personal reflections
- Won't mix philosophical content into technical posts
- Keeps contexts separate unless you want to blend them

### Smart Memory
- Remembers important work indefinitely
- Prioritizes recent and high-importance content
- Lets you control what gets remembered from your consumption
- Automatically stays up-to-date with new content

### No Busywork
- Set it up once, it runs automatically
- Nightly syncing of all your content sources
- No manual copying or pasting
- Just chat when you need it

## Content Sources

Rumi learns from:

### What You Create (Automatic)
- LinkedIn posts (with engagement data)
- Twitter/X posts (with engagement data)
- Blog posts from your website
- Customer meeting transcripts (via Fathom)

### What You Consume (Curated by You)
- Articles you read
- Videos you watch
- Technical content you browse
- You review and approve what gets remembered

## Tech Stack

### Backend
- **Python 3.11+**: Core application
- **Letta**: Agent orchestration and memory management
- **AWS Bedrock Knowledge Base**: Managed RAG for content storage
- **FastAPI**: REST API backend
- **browser-use**: LLM-powered browser automation for LinkedIn/Twitter

### Frontend
- **Next.js 14+**: Web interface
- **React**: UI components
- **TailwindCSS**: Styling

### Infrastructure
- **AWS EC2**: Server for scheduled jobs
- **AWS Bedrock**: Knowledge Base and embeddings
- **SQLite or DynamoDB**: State management

### External Services
- **Anthropic Claude API**: Classification, generation, browser automation
- **Fathom API**: Meeting transcripts

---

*Named after Rumi, the 13th-century poet who mastered the art of expressing profound ideas through beautiful, accessible language.*