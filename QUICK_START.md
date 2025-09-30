# ⚡ Quick Start Guide

**Get your Digital Twin running in 15 minutes!**

This is the express version of the setup. For detailed explanations, see [SETUP_GUIDE.md](./SETUP_GUIDE.md).

---

## Prerequisites

- GitHub account ✅ (you have this)
- 15 minutes of time ⏱️

---

## Step 1: Create Accounts (5 minutes)

### Vercel (Hosting)
1. Go to [vercel.com](https://vercel.com)
2. Click "Sign Up" → "Continue with GitHub"
3. Authorize Vercel

### Neon (Database)
1. Go to [neon.tech](https://neon.tech)
2. Click "Sign Up" → "Continue with GitHub"
3. Create project → Copy connection string
4. **Save this:** `postgresql://...` (you'll need it in Step 3)

### Upstash (Vector Database)
1. Go to [console.upstash.com](https://console.upstash.com)
2. Click "Sign Up" → "Continue with GitHub"
3. Create Vector Database → Dimensions: 1536, Similarity: COSINE
4. **Save these:**
   - REST URL: `https://xxx.upstash.io`
   - REST Token: `Axxxxxxxxxxxx`

### Groq (AI)
1. Go to [console.groq.com](https://console.groq.com)
2. Sign up with email
3. Create API Key
4. **Save this:** `gsk_xxxxxxxxxxxx`

---

## Step 2: Deploy to Vercel (5 minutes)

1. Go to [vercel.com/dashboard](https://vercel.com/dashboard)
2. Click "Add New..." → "Project"
3. Import your repository: `regine-digital-twin-prod`
4. **STOP!** Don't click Deploy yet!

---

## Step 3: Add Environment Variables (3 minutes)

In the Vercel import page, expand "Environment Variables" and add these 4 variables:

```
DATABASE_URL = [paste your Neon connection string]
UPSTASH_VECTOR_REST_URL = [paste your Upstash URL]
UPSTASH_VECTOR_REST_TOKEN = [paste your Upstash token]
GROQ_API_KEY = [paste your Groq API key]
```

Now click "Deploy" and wait 1-2 minutes.

---

## Step 4: Test Your Deployment (2 minutes)

After deployment, you'll get a URL like: `https://your-app.vercel.app`

### Test 1: Health Check
Visit: `https://your-app.vercel.app/health`

✅ Should show all services "connected" or "configured"

### Test 2: API Test
Visit: `https://your-app.vercel.app/api/test`

✅ Should show: "Regine's Digital Twin API is working!"

### Test 3: Automated Verification
Run this command (replace with your URL):
```bash
python verify_deployment.py https://your-app.vercel.app
```

---

## ✅ Success!

Your Digital Twin backend is now live! 

### Next Steps:

1. **Populate your vector database** with your professional data
   - See [SETUP_GUIDE.md](./SETUP_GUIDE.md) Step 3.3

2. **Build a frontend** to interact with your Digital Twin
   - Use v0.dev, React, or plain HTML

3. **Test the AI chat:**
   ```bash
   curl -X POST https://your-app.vercel.app/api/query \
     -H "Content-Type: application/json" \
     -d '{"query": "Tell me about yourself"}'
   ```

---

## ❌ Something Wrong?

### Quick Fixes:

**Services showing "not_configured"?**
- Check you added all 4 environment variables in Vercel
- Go to: Settings → Environment Variables
- Redeploy after adding

**Services showing "error"?**
- Check your credentials are correct
- Make sure databases are not suspended
- See [TROUBLESHOOTING.md](./TROUBLESHOOTING.md)

**Still stuck?**
- Check the detailed [SETUP_GUIDE.md](./SETUP_GUIDE.md)
- Review [TROUBLESHOOTING.md](./TROUBLESHOOTING.md)
- Check Vercel deployment logs

---

## Useful Commands

```bash
# Test locally
python vercel_mcp_server.py

# Verify deployment
python verify_deployment.py https://your-app.vercel.app

# Test health
curl https://your-app.vercel.app/health

# Test chat (requires configured services)
curl -X POST https://your-app.vercel.app/api/query \
  -H "Content-Type: application/json" \
  -d '{"query": "What are your skills?"}'
```

---

## Documentation

- 📖 [Complete Setup Guide](./SETUP_GUIDE.md) - Detailed explanations
- 🔧 [Troubleshooting](./TROUBLESHOOTING.md) - Fix common issues
- 📚 [README](./README.md) - Technical overview

---

**Ready to customize?** Check out the main [SETUP_GUIDE.md](./SETUP_GUIDE.md) for information on:
- Populating your vector database with your data
- Building a frontend interface
- Adding voice capabilities
- Phone integration

---

**Time taken:** ~15 minutes ⚡

**Total cost:** $0 (using free tiers) 🎉
