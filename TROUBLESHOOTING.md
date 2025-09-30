# 🔧 Troubleshooting Guide

Quick reference for common issues and their solutions.

## Quick Diagnostics

### Step 1: Check Health Endpoint
Visit: `https://your-app.vercel.app/health`

Expected response:
```json
{
  "status": "healthy",
  "services": {
    "database": "connected",
    "vector_db": "connected", 
    "groq_api": "configured"
  }
}
```

### Step 2: Identify the Problem

| Service Status | Issue | Go To |
|----------------|-------|-------|
| `database: "error"` | Database connection failed | [Fix Database](#database-issues) |
| `database: "not_configured"` | DATABASE_URL missing | [Fix Database](#database-issues) |
| `vector_db: "error"` | Upstash connection failed | [Fix Vector DB](#vector-database-issues) |
| `vector_db: "not_configured"` | Upstash credentials missing | [Fix Vector DB](#vector-database-issues) |
| `groq_api: "not_configured"` | Groq API key missing | [Fix Groq](#groq-api-issues) |
| All show "error" | Multiple configuration issues | [Check All Env Vars](#environment-variable-issues) |

---

## Database Issues

### Symptom: `database: "error"`

**Possible Causes:**
1. Invalid connection string
2. Database is suspended (Neon free tier)
3. Connection timeout
4. SSL certificate issues

**Solutions:**

#### Fix 1: Verify Connection String Format
Your DATABASE_URL should look like:
```
postgresql://username:password@ep-xxx.region.aws.neon.tech/database?sslmode=require
```

Check:
- ✅ Starts with `postgresql://`
- ✅ Contains `@` symbol
- ✅ Ends with `?sslmode=require`
- ✅ No spaces or line breaks
- ✅ Username and password are correct

#### Fix 2: Wake Up Suspended Database
1. Go to [Neon Console](https://console.neon.tech)
2. Find your project
3. If it says "Suspended", click "Activate"
4. Wait 30 seconds, then test again

#### Fix 3: Update Environment Variable
1. Go to [Vercel Dashboard](https://vercel.com/dashboard)
2. Select your project
3. Go to Settings → Environment Variables
4. Find `DATABASE_URL`
5. Click "Edit" and paste the correct value
6. Click "Save"
7. Go to Deployments → Latest → Click "..." → "Redeploy"

#### Fix 4: Test Connection in Neon
1. Go to Neon Console
2. Select your database
3. Click "SQL Editor"
4. Run: `SELECT 1;`
5. If this fails, your database has a problem

---

## Vector Database Issues

### Symptom: `vector_db: "error"` or `vector_db: "not_configured"`

**Possible Causes:**
1. Invalid Upstash URL
2. Invalid or expired token
3. Database is deleted
4. Network timeout

**Solutions:**

#### Fix 1: Get Fresh Credentials
1. Go to [Upstash Console](https://console.upstash.com)
2. Select your Vector database
3. Go to "REST API" tab
4. Copy both:
   - `UPSTASH_VECTOR_REST_URL`
   - `UPSTASH_VECTOR_REST_TOKEN`

#### Fix 2: Check URL Format
- ✅ Should be: `https://xxx-xxx-xxx.upstash.io`
- ❌ NOT: `https://xxx-xxx-xxx.upstash.io/`  (no trailing slash)
- ❌ NOT: Missing `https://`

#### Fix 3: Verify Token
- Should be a long string starting with capital letter
- No spaces or line breaks
- Copy the entire token

#### Fix 4: Update Vercel Environment Variables
1. Vercel Dashboard → Your Project → Settings → Environment Variables
2. Update both variables:
   - `UPSTASH_VECTOR_REST_URL`
   - `UPSTASH_VECTOR_REST_TOKEN`
3. Save and redeploy

#### Fix 5: Test Upstash Connection
Test with curl:
```bash
curl -X GET "YOUR_UPSTASH_URL/info" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

Expected: Status 200 with database info

---

## Groq API Issues

### Symptom: `groq_api: "not_configured"` or AI responses fail

**Possible Causes:**
1. API key missing
2. API key invalid
3. Rate limit exceeded
4. Groq service down

**Solutions:**

#### Fix 1: Get New API Key
1. Go to [Groq Console](https://console.groq.com)
2. Click "API Keys" in sidebar
3. Click "Create API Key"
4. Name it: `digital-twin`
5. Copy the key (starts with `gsk_`)

#### Fix 2: Update Environment Variable
1. Vercel Dashboard → Your Project → Settings → Environment Variables
2. Find or create `GROQ_API_KEY`
3. Paste your API key
4. Save and redeploy

#### Fix 3: Check Rate Limits
1. Go to Groq Console → Usage
2. Check if you've exceeded limits
3. If yes, wait for reset or upgrade plan

#### Fix 4: Check Groq Status
Visit: https://status.groq.com/

If Groq is down, wait for recovery.

---

## Environment Variable Issues

### Symptom: Multiple services showing errors

**Quick Fix: Review All Environment Variables**

1. Go to Vercel Dashboard → Your Project → Settings → Environment Variables

2. You should have exactly 4 variables:

| Variable Name | Example Value | Notes |
|---------------|---------------|-------|
| `DATABASE_URL` | `postgresql://user:pass@host/db?sslmode=require` | From Neon |
| `UPSTASH_VECTOR_REST_URL` | `https://xxx.upstash.io` | No trailing slash |
| `UPSTASH_VECTOR_REST_TOKEN` | `Axxxxxxxxxxxx` | Long string |
| `GROQ_API_KEY` | `gsk_xxxxxxxxx` | Starts with gsk_ |

3. Common mistakes:
   - ❌ Extra spaces at start/end
   - ❌ Line breaks in values
   - ❌ Missing variables
   - ❌ Wrong variable names (typos)
   - ❌ Values wrapped in quotes (not needed in Vercel)

4. After fixing, always click "Redeploy"

---

## Deployment Issues

### Symptom: Deployment fails or shows "Application Error"

#### Check Deployment Logs
1. Vercel Dashboard → Your Project → Deployments
2. Click on the latest deployment
3. Look at "Build Logs" and "Function Logs"

#### Common Deployment Errors

**Error: "No such file or directory"**
- Solution: Make sure `api/index.py` exists
- Solution: Check `vercel.json` points to correct file

**Error: "Module not found"**
- Solution: Check `requirements.txt` includes all dependencies
- Solution: Make sure Python version is compatible

**Error: "Function invocation timeout"**
- Solution: Database might be slow to connect
- Solution: Check if external services are responding

**Error: "Build failed"**
- Solution: Check Python syntax errors
- Solution: Verify all imports are available

#### Force Rebuild
1. Go to Deployments
2. Click "..." on latest deployment
3. Click "Redeploy"
4. Check "Use existing Build Cache" is OFF

---

## API Endpoint Issues

### `/api/test` Returns Error

**Solutions:**
1. Check if deployment is complete
2. Wait 30 seconds and try again
3. Check Function Logs in Vercel

### `/api/query` Returns "Internal server error"

**Possible causes:**
1. Missing request body
2. Invalid JSON
3. Backend error

**Test with proper request:**
```bash
curl -X POST https://your-app.vercel.app/api/query \
  -H "Content-Type: application/json" \
  -d '{"query": "test"}'
```

**Check Function Logs:**
1. Vercel Dashboard → Your Project
2. Click "Logs" tab
3. Look for error messages

### Empty or Generic AI Responses

**Causes:**
1. Vector database has no data
2. Upstash connection failing
3. Query not matching any data

**Solutions:**
1. Make sure you've populated Upstash with data
2. Check vector_db status in `/health`
3. Try more general queries first

---

## Performance Issues

### Slow Response Times

**Normal response time:** 1-5 seconds

**If slower than 10 seconds:**

1. **Check service locations:**
   - All services should be in same region if possible
   - Vercel deployment region
   - Neon database region
   - Upstash database region

2. **Check database sleep:**
   - Neon free tier databases sleep after inactivity
   - First query after sleep takes longer
   - Consider upgrading for always-on database

3. **Check Groq API:**
   - Visit Groq status page
   - Try different time of day

### Cold Starts

**What is it?** Serverless functions "wake up" on first request

**Normal:** First request takes 2-5 seconds, subsequent requests are fast

**Solutions:**
- Use a service like Uptime Robot to ping your app every 5 minutes
- Upgrade to Vercel Pro for faster cold starts
- Accept it as normal serverless behavior

---

## Local Development Issues

### "Module not found" Error

```bash
pip install -r requirements.txt
```

### Port Already in Use

```bash
# Find and kill process using port 8000
lsof -ti:8000 | xargs kill -9

# Or use different port
PORT=8001 python vercel_mcp_server.py
```

### Environment Variables Not Loading

1. Make sure `.env` file exists in project root
2. Check file is named exactly `.env` (not `.env.txt`)
3. Verify file format:
   ```
   DATABASE_URL=value
   UPSTASH_VECTOR_REST_URL=value
   ```
4. No spaces around `=`
5. No quotes needed around values

---

## Data Issues

### No Context in Responses

**Symptom:** AI gives generic responses, doesn't use your information

**Cause:** Vector database is empty or not returning results

**Solutions:**

1. **Check if Upstash has data:**
   - Go to Upstash Console
   - Select your database
   - Check "Data Browser"
   - Should see entries

2. **Populate database:**
   - You need to upload your data to Upstash
   - See main documentation for embedding instructions
   - Use the `mytwin_refined.json` as template

3. **Test vector search:**
   - Check `/health` shows vector_db: "connected"
   - Try broader queries
   - Check response metadata for `vector_hits`

---

## Emergency Fixes

### Everything is Broken - Start Fresh

1. **Delete and recreate environment variables:**
   - Vercel → Settings → Environment Variables
   - Delete all existing variables
   - Re-add one by one, carefully
   - Redeploy

2. **Redeploy from GitHub:**
   - Vercel → Deployments
   - Click "..." → Redeploy
   - Uncheck "Use existing Build Cache"

3. **Check all services are active:**
   - Neon: Database not suspended
   - Upstash: Database exists and is active
   - Groq: API key is valid
   - Vercel: No ongoing incidents

4. **Still not working?**
   - Check service status pages:
     - https://www.vercel-status.com/
     - https://neonstatus.com/
     - https://status.upstash.com/
     - https://status.groq.com/

---

## Getting Additional Help

### Before Asking for Help

Gather this information:
1. Screenshot of `/health` response
2. Screenshot of error message
3. Relevant logs from Vercel
4. What you've already tried

### Where to Get Help

1. **GitHub Issues** - Create an issue with details above
2. **Vercel Support** - support@vercel.com for Vercel-specific issues
3. **Service Documentation:**
   - Neon: https://neon.tech/docs
   - Upstash: https://upstash.com/docs
   - Groq: https://console.groq.com/docs

---

## Checklist for Working Deployment

Use this to verify everything is set up correctly:

- [ ] GitHub repository is accessible
- [ ] Vercel project is created and linked to GitHub
- [ ] All 4 environment variables are set in Vercel
- [ ] Neon database is created and not suspended
- [ ] Upstash Vector database is created
- [ ] Groq API key is valid and not rate-limited
- [ ] Latest deployment shows "Ready" status
- [ ] `/health` endpoint returns "healthy" status
- [ ] `/api/test` endpoint returns success message
- [ ] All three services show "connected" or "configured"
- [ ] Vector database has data populated
- [ ] API query returns actual responses

If all checkboxes are checked, your deployment should be working! ✅

---

**Need more help? Check the main [SETUP_GUIDE.md](./SETUP_GUIDE.md) for detailed instructions.**
