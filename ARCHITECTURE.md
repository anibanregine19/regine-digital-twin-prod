# 🏗️ Architecture Documentation

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        USER / VISITOR                            │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             │ HTTPS Request
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                      VERCEL (Hosting)                            │
│  ┌────────────────────────────────────────────────────────┐    │
│  │  Serverless Function: api/index.py                      │    │
│  │  ├─ Routes all requests                                 │    │
│  │  └─ Imports Flask app from vercel_mcp_server.py        │    │
│  └────────────────────────────────────────────────────────┘    │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             │ Python Import
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│              FLASK APPLICATION (vercel_mcp_server.py)            │
│  ┌────────────────────────────────────────────────────────┐    │
│  │  EnhancedDigitalTwin Class                              │    │
│  │  ├─ Vector Search                                       │    │
│  │  ├─ AI Response Generation                              │    │
│  │  ├─ Database Logging                                    │    │
│  │  └─ Analytics                                           │    │
│  └────────────────────────────────────────────────────────┘    │
│                                                                   │
│  Routes:                                                         │
│  ├─ /                      → Home/API info                      │
│  ├─ /health                → Service status                     │
│  ├─ /api/test              → Quick test                         │
│  ├─ /api/query    [POST]   → AI chat                           │
│  └─ /api/analytics         → Usage stats                        │
└───────────────┬──────────────────┬──────────────┬───────────────┘
                │                  │              │
    ┌───────────▼───────┐  ┌──────▼──────┐  ┌───▼────────┐
    │  NEON PostgreSQL  │  │   UPSTASH   │  │    GROQ    │
    │    (Database)     │  │  (Vector DB)│  │  (AI API)  │
    │                   │  │             │  │            │
    │  ┌─────────────┐  │  │  ┌────────┐ │  │  ┌───────┐ │
    │  │ chat_logs   │  │  │  │ Vector │ │  │  │ Llama │ │
    │  │ popular_qs  │  │  │  │ Index  │ │  │  │  3.1  │ │
    │  └─────────────┘  │  │  └────────┘ │  │  └───────┘ │
    └───────────────────┘  └─────────────┘  └────────────┘
         Analytics            Knowledge        AI Brain
         & Logging              Base           Responses
```

---

## Request Flow

### 1. User Makes a Query

```
User → https://your-app.vercel.app/api/query
     POST: {"query": "Tell me about yourself"}
```

### 2. Vercel Routes Request

```
Vercel → api/index.py (Serverless Function)
      → Imports Flask app from vercel_mcp_server.py
      → Routes to /api/query endpoint
```

### 3. Flask Processes Request

```
Flask → EnhancedDigitalTwin.answer_query()
      │
      ├─ 1. Search Upstash Vector DB
      │    ├─ Convert query to embedding
      │    ├─ Find similar content
      │    └─ Return top 3 results
      │
      ├─ 2. Generate AI Response with Groq
      │    ├─ Build prompt with context
      │    ├─ Call Groq API
      │    └─ Get natural language response
      │
      ├─ 3. Log to Neon PostgreSQL
      │    ├─ Save query & response
      │    ├─ Record response time
      │    └─ Track category
      │
      └─ 4. Return Response
           └─ JSON with content & metadata
```

### 4. Response to User

```
{
  "content": "I am a Business Analyst with 13+ years...",
  "metadata": {
    "response_time": 1.23,
    "vector_hits": 5,
    "category": "general",
    "context_used": 3
  }
}
```

---

## Component Details

### Vercel Serverless Function (`api/index.py`)

**Purpose:** Entry point for all requests

**Key Features:**
- Routes all HTTP requests
- Imports and runs Flask application
- Handles serverless cold starts
- Manages Python environment

**Code:**
```python
from vercel_mcp_server import app

def handler(request, response):
    return app
```

---

### Flask Application (`vercel_mcp_server.py`)

**Purpose:** Main application logic

**Key Features:**
- 5 REST API endpoints
- Database connection pooling
- Vector search integration
- AI response generation
- Analytics tracking

**Key Functions:**
- `health()` - Check service status
- `test()` - Quick functionality test
- `query()` - Main AI chat interface
- `analytics()` - Usage statistics
- `home()` - API information

---

### Neon PostgreSQL

**Purpose:** Structured data storage and analytics

**Tables:**
```sql
chat_logs:
  - id, query, response, response_time
  - vector_hits, query_category
  - created_at, user_ip, user_agent

popular_questions:
  - id, question_type, question_text
  - ask_count, avg_response_time
  - last_asked
```

**Usage:**
- Store all chat interactions
- Track popular questions
- Generate analytics
- Monitor performance

---

### Upstash Vector Database

**Purpose:** Semantic search and knowledge retrieval

**Data Structure:**
```
Vector Index:
  - Dimension: 1536
  - Similarity: COSINE
  - Metadata: {text, category, source}
```

**Content Types:**
- Professional experiences
- Skills and competencies
- Interview Q&A responses
- Personal information
- Achievements

**Usage:**
- Convert query to embedding
- Find semantically similar content
- Return top K results
- Filter by category (optional)

---

### Groq API

**Purpose:** Natural language AI responses

**Model:** Llama 3.1 8B Instant

**Features:**
- Fast response times (~1-2 seconds)
- Context-aware generation
- Professional tone
- 1000 token max output

**Process:**
```
1. Receive query + vector search context
2. Build structured prompt
3. Generate response via Groq API
4. Return professional answer
```

---

## Data Flow Diagrams

### Health Check Flow

```
GET /health
    │
    ├─ Test Neon Connection
    │   └─ psycopg2.connect() → "connected" | "error"
    │
    ├─ Test Upstash Connection
    │   └─ GET /info → "connected" | "error"
    │
    ├─ Check Groq API Key
    │   └─ "configured" | "not_configured"
    │
    └─ Return Status
        └─ {"status": "healthy", "services": {...}}
```

### Query Processing Flow

```
POST /api/query {"query": "..."}
    │
    ├─ 1. VECTOR SEARCH (Upstash)
    │   ├─ POST /query with text
    │   ├─ Get top 5 similar chunks
    │   └─ Extract metadata.text
    │
    ├─ 2. GENERATE RESPONSE (Groq)
    │   ├─ Build prompt with context
    │   ├─ POST /chat/completions
    │   └─ Extract AI response
    │
    ├─ 3. LOG INTERACTION (Neon)
    │   ├─ INSERT INTO chat_logs
    │   ├─ Record timing & metadata
    │   └─ Categorize query
    │
    └─ 4. RETURN RESPONSE
        └─ {"content": "...", "metadata": {...}}
```

---

## Environment Configuration

### Required Environment Variables

```bash
# Neon PostgreSQL
DATABASE_URL=postgresql://user:pass@host/db?sslmode=require

# Upstash Vector
UPSTASH_VECTOR_REST_URL=https://xxx.upstash.io
UPSTASH_VECTOR_REST_TOKEN=Axxxxxxxxxxxxx

# Groq AI
GROQ_API_KEY=gsk_xxxxxxxxxxxxx

# Optional
PORT=8000  # For local development only
```

### How Variables Are Used

```
vercel_mcp_server.py
    │
    ├─ EnhancedDigitalTwin.__init__()
    │   ├─ self.db_url = os.getenv('DATABASE_URL')
    │   ├─ self.upstash_url = os.getenv('UPSTASH_VECTOR_REST_URL')
    │   ├─ self.upstash_token = os.getenv('UPSTASH_VECTOR_REST_TOKEN')
    │   └─ self.groq_api_key = os.getenv('GROQ_API_KEY')
    │
    └─ Used throughout application for API calls
```

---

## Deployment Architecture

### Before Fix (Broken)

```
vercel.json → vercel_mcp_server.py (direct)
                     ↓
                  ❌ ERROR
     (Vercel couldn't find entry point)
```

### After Fix (Working)

```
vercel.json → api/index.py → vercel_mcp_server.py (Flask app)
                 ↓               ↓
           Serverless      Flask Routes
             Function        Processing
                 ↓               ↓
              ✅ Works     ✅ All endpoints
```

---

## Scalability Considerations

### Current Architecture
- **Type:** Serverless (auto-scaling)
- **Cold Start:** 1-3 seconds
- **Warm Response:** <500ms
- **Concurrent Requests:** Unlimited (Vercel handles)

### Performance Optimizations
1. **Lazy Initialization:** Database setup on first use
2. **Connection Pooling:** psycopg2 manages connections
3. **Caching:** LRU cache for repeated queries
4. **Serverless:** No server management needed

### Limitations & Upgrades
| Free Tier | Limit | Upgrade Path |
|-----------|-------|--------------|
| Vercel | 100GB/month | Pro: $20/month |
| Neon | 0.5GB storage | Scale: $19/month |
| Upstash | 10k req/day | Pay-as-you-go |
| Groq | Rate limited | Higher limits available |

---

## Security Architecture

### Data Protection
```
User Data Flow:
  ├─ HTTPS everywhere (TLS 1.3)
  ├─ Environment variables (not in code)
  ├─ PostgreSQL SSL required
  ├─ API token authentication
  └─ No sensitive data in logs
```

### Best Practices Implemented
1. ✅ Environment variables for secrets
2. ✅ .gitignore for .env files
3. ✅ HTTPS only (Vercel enforces)
4. ✅ PostgreSQL SSL mode required
5. ✅ Bearer token auth for APIs
6. ✅ CORS enabled for frontend

---

## Monitoring & Debugging

### Built-in Monitoring
```
1. Health Endpoint (/health)
   └─ Real-time service status

2. Analytics Endpoint (/api/analytics)
   └─ Usage statistics

3. Vercel Logs
   └─ Function execution logs

4. Database Logs (Neon)
   └─ Query performance

5. verify_deployment.py
   └─ Automated testing
```

### Debugging Flow
```
Issue Detected
    │
    ├─ 1. Check /health endpoint
    │   └─ Identify which service has error
    │
    ├─ 2. Check Vercel Logs
    │   └─ Look for Python exceptions
    │
    ├─ 3. Check Environment Variables
    │   └─ Verify all 4 variables set
    │
    ├─ 4. Test Individual Services
    │   ├─ Neon: Test connection
    │   ├─ Upstash: Check data exists
    │   └─ Groq: Verify API key
    │
    └─ 5. Run verify_deployment.py
        └─ Get comprehensive diagnostics
```

---

## Technology Stack Summary

| Layer | Technology | Purpose |
|-------|-----------|---------|
| **Hosting** | Vercel | Serverless deployment |
| **Backend** | Flask + Python | API framework |
| **Database** | Neon PostgreSQL | Structured data |
| **Vector DB** | Upstash Vector | Semantic search |
| **AI** | Groq (Llama 3.1) | Response generation |
| **HTTP** | HTTPS/REST | API protocol |
| **Auth** | Bearer Tokens | Service authentication |

---

## Future Enhancements

### Planned Features
1. **Voice Interface**
   - OpenAI Realtime API integration
   - Voice-to-voice conversations

2. **Phone Integration**
   - Twilio phone number
   - Call handling and voicemail
   - Interview scheduling

3. **Admin Dashboard**
   - Content management UI
   - Analytics visualization
   - Data editing interface

4. **Frontend Website**
   - Built with v0.dev
   - Chat interface
   - Portfolio display

### Architecture Changes Needed
```
Current:
  Backend API Only

Future:
  Frontend (v0.dev)
      ↓
  Backend API (current)
      ↓
  Enhanced Services
      ├─ Voice (OpenAI)
      ├─ Phone (Twilio)
      └─ Admin (Auth)
```

---

## Documentation Map

This architecture documentation connects to:

- **[README.md](./README.md)** - Technical overview
- **[SETUP_GUIDE.md](./SETUP_GUIDE.md)** - Deployment instructions
- **[TROUBLESHOOTING.md](./TROUBLESHOOTING.md)** - Fix issues
- **[CHANGES_SUMMARY.md](./CHANGES_SUMMARY.md)** - What changed

---

**Last Updated:** January 2025

**Version:** 2.1 (Serverless Optimized)
