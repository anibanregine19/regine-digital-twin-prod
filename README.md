# mydigitaltwin
# 🧑‍💻 My Digital Twin – AI-Powered Interview Knowledge Base

![Python](https://img.shields.io/badge/python-3.8+-blue?logo=python)  
![Groq](https://img.shields.io/badge/Groq-API-orange?logo=lightning)  
![Upstash](https://img.shields.io/badge/Upstash-VectorDB-green?logo=upstash)  
![Neon](https://img.shields.io/badge/Neon-Postgres-blueviolet?logo=postgresql)  
![Vercel](https://img.shields.io/badge/Vercel-AI%20SDK-black?logo=vercel)  
![Clerk](https://img.shields.io/badge/Clerk-Auth-lightgrey?logo=clerk)  

This project builds a **personal AI Digital Twin** — an interactive assistant that can answer interview-style questions about my professional background using **Retrieval-Augmented Generation (RAG)**.

Instead of relying only on the LLM’s built-in memory, this project embeds my **career knowledge base (`digitaltwin.json`)** into a **vector database (Upstash Vector)** and retrieves the most relevant details to ground the AI’s answers.

---

## 🎯 What This Does

This Digital Twin can answer:

- “What were your key achievements at Asurion?”  
- “Tell me about your experience with journey mapping and CX design.”  
- “Which AI tools are you most confident with?”  
- “Walk me through a project where you reduced resolution time.”  

---

## 📦 Requirements

### ✅ Software
- Python 3.8+  
- [VS Code Insider](https://code.visualstudio.com/insiders/) with GitHub Copilot Agent  
- [Claude Desktop](https://claude.ai/) (for brainstorming/expansion)  

### ✅ Python Libraries
Install dependencies:

```bash
pip install python-dotenv upstash-vector groq
```

---

## 🔑 Environment Setup

Create a `.env` file in your project root:

```bash
# Upstash Vector credentials
UPSTASH_VECTOR_REST_URL="your-upstash-url"
UPSTASH_VECTOR_REST_TOKEN="your-upstash-token"

# Groq API
GROQ_API_KEY="your-groq-api-key"

# Vercel AI Gateway
AI_GATEWAY_API_KEY="your-vercel-ai-gateway-key"

# Neon Postgres (optional structured storage)
DATABASE_URL="your-neon-postgres-url"

# Clerk (optional authentication)
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY="your-clerk-publishable"
CLERK_SECRET_KEY="your-clerk-secret"
```

⚠️ **Do not commit `.env` to GitHub.** Add it to `.gitignore`.

---

## 🛠️ Project Structure

```
digital-twin-workshop/
├── data/
│   └── digitaltwin.json        # Knowledge base of your career
├── embed_digitaltwin.py        # Script to embed JSON into Upstash
├── digital_twin_mcp_server.py  # MCP server for retrieval + Q&A
├── .env                        # API keys (not committed)
└── README.md                   # This file
```

---

## 🚀 Usage

### 1. Embed your Digital Twin into Upstash
```bash
python embed_digitaltwin.py
```

### 2. Run the MCP Server
```bash
python digital_twin_mcp_server.py
```

---

## 📁 digitaltwin.json

This JSON is your **knowledge base**. It includes:

- Personal info  
- Experience (roles, achievements, technologies)  
- Projects & portfolio  
- Skills (technical + soft skills)  
- Education & certifications  
- Common interview prep Q&A  

The richer your `digitaltwin.json`, the better the AI will perform in interviews.

---

## 🧠 Example Queries

Once running, you can ask your Twin:

- “Summarize my top 3 career achievements.”  
- “What metrics show my impact at Etisalat?”  
- “How do I explain my leadership style in interviews?”  

---

## 🚀 Next Steps

- Expand `digitaltwin.json` with **STAR-format achievements**  
- Add more **interview prep Q&A**  
- Deploy your Twin via **Vercel** for a web-based demo  
- Integrate with **voice/telephony** via Twilio  

---

## 🙌 Credits

Built by **Regine Aniban** using:

- [Groq API](https://console.groq.com) ⚡ Fast embeddings & inference  
- [Upstash Vector](https://upstash.com/vector) 📦 Vector DB storage  
- [Neon](https://neon.tech) 🐘 Serverless Postgres  
- [Vercel AI SDK](https://vercel.com/ai) 🔗 AI Gateway integration  
- [Clerk](https://clerk.com) 🔐 Authentication  

---
