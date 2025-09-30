# 🤖 **Regine's Professional AI Digital Twin**

[![Vercel](https://img.shields.io/badge/Deployed%20on-Vercel-black)](https://vercel.com)
[![Neon](https://img.shields.io/badge/Database-Neon%20PostgreSQL-green)](https://neon.tech)
[![Upstash](https://img.shields.io/badge/Vector%20DB-Upstash-orange)](https://upstash.com)
[![Python](https://img.shields.io/badge/python-3.9+-blue?logo=python)
[![Flask](https://img.shields.io/badge/Framework-Flask-lightgrey?logo=flask)

> **Professional AI-powered Digital Twin showcasing 13+ years of Business Analysis expertise with advanced RAG capabilities and PostgreSQL analytics.**

## 🎯 **What This Is**

An intelligent digital twin that represents my professional experience, skills, and achievements. Built with enterprise-grade technology stack for recruiters, hiring managers, and professional networking.

### **Live Demo**
- 🌐 **Website**: [Your deployed URL here]
- 💬 **AI Chat**: Interactive conversation about my professional background
- 📊 **Analytics**: Real-time chat metrics and popular questions

## 🏗️ **Architecture**

```
v0.app Frontend ✅ Vercel API ✅ Neon PostgreSQL + Upstash Vector
       ⬇️              ⬇️                    ⬇️
   Chat Interface ➤ AI Brain ➤ Knowledge Base + Analytics
```

### **Technology Stack**

| Component | Technology | Purpose |
|-----------|------------|---------|
| **Frontend** | v0.app | Professional portfolio website |
| **Backend** | Flask + Vercel | Serverless AI API |
| **AI Search** | Upstash Vector | Semantic search with embeddings |
| **Database** | Neon PostgreSQL | Chat logs and analytics |
| **LLM** | Groq Llama 3.1 | Natural language processing |
| **Embeddings** | Mixedbread AI | Professional vector embeddings |

## 🚀 **Features**

### **AI Capabilities**
- ✅ **Semantic Search**: 40+ embedded knowledge chunks
- ✅ **Context-Aware Responses**: Intelligent query categorization
- ✅ **Professional Tone**: Interview-ready communication
- ✅ **Fallback Handling**: Graceful error recovery

### **Analytics Dashboard**
- 📊 **Chat Metrics**: Response times, query counts
- 📈 **Popular Questions**: Most asked interview topics
- 🎯 **User Patterns**: Engagement analytics
- 🔍 **Search Performance**: Vector similarity scores

### **Professional Content**
- 💼 **13+ Years Experience**: Asurion, Etisalat, TeleTech
- 🎯 **8 Core Competencies**: Requirements Analysis, Stakeholder Management
- 🏆 **Proven Results**: 35% support ticket reduction achievement
- 📋 **Interview Q&A**: 25+ professional question responses

## 📋 **API Endpoints**

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | System health and service status |
| `/api/query` | POST | Main AI chat interface |
| `/api/test` | GET | Quick response test |
| `/api/analytics` | GET | Chat analytics dashboard |

### **API Usage Example**

```javascript
// Query the AI Digital Twin
const response = await fetch('https://your-deployment.vercel.app/api/query', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ 
    query: "What are your core competencies?" 
  })
});

const data = await response.json();
console.log(data.content); // Professional response about competencies
```

## 🛠️ **Local Development**

### **Prerequisites**
- Python 3.9+
- pip package manager
- Environment variables (see `.env.example`)

### **Installation**

```bash
# Clone repository
git clone https://github.com/yourusername/regine-digital-twin-production.git
cd regine-digital-twin-production

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your API keys

# Run locally
python vercel_mcp_server.py
```

### **Environment Variables**

```bash
# Required for local development
UPSTASH_VECTOR_REST_URL=your_upstash_url
UPSTASH_VECTOR_REST_TOKEN=your_upstash_token
GROQ_API_KEY=your_groq_key
DATABASE_URL=your_neon_postgresql_url
PORT=8000
```

## 📊 **Performance Metrics**

### **Response Quality**
- ✅ **100% Success Rate** on core interview questions
- ✅ **90% Success Rate** on question variations
- ✅ **Average Response Time**: 0.8-1.5 seconds
- ✅ **Content Quality**: 200-2500+ characters per response

### **Knowledge Base**
- 📚 **40+ Embedded Chunks** with professional content
- 🎯 **5 Question Categories**: competencies, experience, stakeholder, methodologies, achievements
- 📈 **MTEB Score**: 64.68 (mixedbread-ai embeddings)
- 🔍 **Similarity Threshold**: 0.3 for optimal recall

## 🎯 **Interview Questions Supported**

### **Core Competencies**
- "What are your core competencies?"
- "What are your main skills?"
- "Tell me about your core skills"

### **Professional Experience**
- "Tell me about your experience at Asurion"
- "What did you do at Asurion?"
- "Describe your role at Asurion Australia"

### **Stakeholder Management**
- "How do you handle stakeholder management?"
- "What's your approach to stakeholder management?"
- "How do you manage stakeholders?"

### **Methodologies**
- "What methodologies do you use?"
- "What frameworks do you work with?"
- "Tell me about your methodology approach"

### **Achievements**
- "What awards have you received?"
- "Tell me about your achievements"
- "What are your main accomplishments?"

## 🚀 **Deployment**

### **Vercel Deployment**

1. **Connect Repository**: Link GitHub repo to Vercel
2. **Configure Environment**: Add all required variables
3. **Deploy**: Automatic deployment on push to main
4. **Monitor**: Check deployment logs and health endpoints

### **Database Setup**

- **Neon PostgreSQL**: Automatic table creation on first run
- **Upstash Vector**: Pre-embedded with 40 knowledge chunks
- **Analytics Tables**: `chat_logs`, `popular_questions`, `system_metrics`

## 🔧 **Configuration**

### **Similarity Thresholds**
```python
SIMILARITY_THRESHOLD = 0.3  # Vector search threshold
MAX_RESULTS = 5             # Maximum search results
CACHE_SIZE = 128           # LRU cache size
```

### **Response Categories**
- `competencies`: Skills and abilities
- `experience`: Work history and roles
- `stakeholder_management`: Team leadership
- `methodologies`: Frameworks and processes
- `achievements`: Awards and accomplishments

## 📈 **Analytics Schema**

### **Chat Logs Table**
```sql
CREATE TABLE chat_logs (
    id SERIAL PRIMARY KEY,
    query TEXT NOT NULL,
    response TEXT NOT NULL,
    response_time FLOAT,
    vector_hits INTEGER,
    query_category VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    user_ip VARCHAR(45),
    user_agent TEXT
);
```

### **Popular Questions Table**
```sql
CREATE TABLE popular_questions (
    id SERIAL PRIMARY KEY,
    question_type VARCHAR(100),
    question_text TEXT,
    ask_count INTEGER DEFAULT 1,
    avg_response_time FLOAT,
    last_asked TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## 📞 **Support & Contact**

### **Professional Inquiries**
- 📧 **Email**: aniban.regine@gmail.com
- 📱 **Phone**: 0493 693 259
- 🌐 **LinkedIn**: [linkedin.com/in/regine-aniban](https://www.linkedin.com/in/regine-aniban/)
- 📍 **Location**: Melbourne, Australia

### **Technical Support**
- 🐛 **Issues**: Use GitHub Issues for bug reports
- 📖 **Documentation**: See `NEON_DEPLOYMENT_GUIDE.md`
- 🔧 **Configuration**: Check environment variables

## 🏆 **About Regine Aniban**

**Business Analyst | 13+ Years Experience | Digital Transformation Expert**

Accomplished Business Analyst with progressive experience driving digital transformation and process optimization across telecommunications, technology, and customer experience domains. Proven expertise in requirements elicitation, stakeholder management, and agile delivery methodologies.

### **Core Competencies**
1. **Requirements Analysis** - Stakeholder interviews, business process mapping
2. **Stakeholder Management** - Cross-functional team leadership, workshop facilitation
3. **Process Improvement** - Workflow optimization, efficiency metrics
4. **Agile Delivery** - Scrum/Kanban methodologies, sprint planning
5. **Solution Testing** - UAT coordination, test case development
6. **Change Management** - Training facilitation, knowledge transfer
7. **Business Intelligence** - Data analysis, reporting solutions
8. **Technical Systems** - System integration, API documentation

### **Key Achievement**
🎯 **35% Reduction in Support Tickets** - Instrumental in launching Help & Support feature in My Etisalat app

---

## 📄 **License**

This project is private and proprietary. All rights reserved. © 2025 Regine Aniban

---

**Built with ❤️ for professional excellence**
