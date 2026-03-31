# Deployment Guide

Complete guide to deploy Universal Video Downloader to Vercel (frontend) and Render (backend).

## Table of Contents

- [Quick Start (10 Minutes)](#quick-start-10-minutes)
- [Prerequisites](#prerequisites)
- [Step 1: Deploy Backend (Render)](#step-1-deploy-backend-render)
- [Step 2: Deploy Frontend (Vercel)](#step-2-deploy-frontend-vercel)
- [Step 3: Configure CORS](#step-3-configure-cors)
- [Step 4: Test Deployment](#step-4-test-deployment)
- [Environment Variables](#environment-variables)
- [FFmpeg & yt-dlp](#ffmpeg--yt-dlp)
- [Troubleshooting](#troubleshooting)
- [Maintenance](#maintenance)
- [Cost & Upgrades](#cost--upgrades)

---

## Quick Start (10 Minutes)

1. Deploy backend to Render → Get backend URL
2. Deploy frontend to Vercel → Get frontend URL
3. Update CORS in Render with frontend URL
4. Test your app

---

## Prerequisites

- GitHub account
- Vercel account (free): https://vercel.com
- Render account (free): https://render.com
- Your code pushed to GitHub

---

## Step 1: Deploy Backend (Render)

### 1.1 Create Web Service

1. Go to https://dashboard.render.com/
2. Click **New +** → **Web Service**
3. Connect your GitHub repository
4. Select: `Universal-Video-Downloader`

### 1.2 Configure Service

Render auto-detects `render.yaml` with these settings:

- **Name**: `universal-video-downloader-backend`
- **Runtime**: Docker
- **Root Directory**: `backend`
- **Dockerfile**: `backend/Dockerfile`
- **FFmpeg**: Installed in Docker image

### 1.3 Add Environment Variables

Click **Environment** tab and add:

| Variable | Value | Required |
|----------|-------|----------|
| `FRONTEND_URL` | Leave empty for now | Yes (add after Step 2) |
| `PORT` | 8000 | No (default) |
| `MAX_CONCURRENT` | 2 | No (default) |

### 1.4 Deploy

1. Click **Create Web Service**
2. Wait 5-10 minutes for build
3. Check logs for: `Setting up ffmpeg...` ✅
4. Copy your backend URL: `https://your-app.onrender.com`

---

## Step 2: Deploy Frontend (Vercel)

### 2.1 Import Project

1. Go to https://vercel.com/dashboard
2. Click **Add New** → **Project**
3. Import your GitHub repository

### 2.2 Configure Build

Vercel auto-detects these settings:

- **Framework**: Vite
- **Root Directory**: `frontend`
- **Build Command**: `npm run build`
- **Output Directory**: `dist`

### 2.3 Add Environment Variable

Click **Environment Variables** and add:

| Variable | Value |
|----------|-------|
| `VITE_API_URL` | Your Render backend URL from Step 1 |

Example: `https://universal-video-downloader-backend-xxxx.onrender.com`

### 2.4 Deploy

1. Click **Deploy**
2. Wait 2-5 minutes
3. Copy your frontend URL: `https://your-app.vercel.app`

---

## Step 3: Configure CORS

### 3.1 Update Backend

1. Go back to Render Dashboard
2. Select your web service
3. Click **Environment** tab
4. Update `FRONTEND_URL` to your Vercel URL
5. Click **Save Changes**
6. Wait for automatic redeploy (2-3 minutes)

---

## Step 4: Test Deployment

### 4.1 Access Your App

Visit your Vercel URL: `https://your-app.vercel.app`

### 4.2 Test Download

1. Paste a YouTube URL: `https://www.youtube.com/watch?v=dQw4w9WgXcQ`
2. Click **Extract** → Should show video info
3. Select format → Choose "Best" or "1080p"
4. Click **Download** → Should start downloading
5. Check progress → Should see live updates

### 4.3 Verify

- ✅ No CORS errors in browser console
- ✅ WebSocket connects successfully
- ✅ Progress updates in real-time
- ✅ Download completes

---

## Environment Variables

### Backend (Render)

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `FRONTEND_URL` | Your Vercel URL for CORS | - | Yes |
| `PORT` | Server port | 8000 | No |
| `BIND` | Bind address | 0.0.0.0 | No |
| `MAX_CONCURRENT` | Max concurrent downloads | 2 | No |
| `QUEUE_MAX_SIZE` | Max queue size | 100 | No |
| `DB_PATH` | Database path | ./storage/downloader.db | No |
| `FFMPEG_PATH` | FFmpeg binary path | auto-detected | No |
| `PROXY` | Proxy URL for downloads | - | No |
| `COOKIES_PATH` | Cookies file path | - | No |

### Frontend (Vercel)

| Variable | Description | Required |
|----------|-------------|----------|
| `VITE_API_URL` | Backend API URL | Yes |

---

## FFmpeg & yt-dlp

### FFmpeg

**Status**: ✅ Automatically installed via Docker

The `backend/Dockerfile` installs FFmpeg during the Docker image build:

```dockerfile
FROM python:3.11-slim

# Install FFmpeg
RUN apt-get update && \
    apt-get install -y ffmpeg && \
    rm -rf /var/lib/apt/lists/*
```

**Verify installation**: Check Render build logs for `Setting up ffmpeg...`

**What it does**: Merges video+audio streams for high-quality downloads

### yt-dlp

**Status**: ✅ Always uses latest version

The `requirements.txt` is configured to install the latest yt-dlp:

```txt
yt-dlp  # Always use latest version
```

**Why**: Video sites change frequently. Latest version ensures maximum compatibility.

**Update**: Redeploy on Render to get the latest yt-dlp version

---

## Troubleshooting

### CORS Errors

**Symptom**: Browser console shows CORS errors

**Solution**:
1. Verify `FRONTEND_URL` in Render matches Vercel URL exactly
2. No trailing slash in URL
3. Wait for Render to finish redeploying
4. Clear browser cache

### Backend Not Responding

**Symptom**: API requests timeout or fail

**Solution**:
- Render free tier spins down after 15 minutes
- First request takes 30-60 seconds to wake up
- This is normal behavior on free tier
- Upgrade to paid tier for always-on service

### Downloads Fail

**Symptom**: "Unable to extract video data" or "HTTP Error 403"

**Solution**:
1. Check if yt-dlp needs updating (redeploy on Render)
2. Try a different video URL
3. Check if site requires cookies (use "Use my cookies" feature)
4. Check Render logs for specific error messages

### FFmpeg Not Working

**Symptom**: High-quality downloads fail with FFmpeg errors

**Solution**:
1. Check Render build logs for FFmpeg installation
2. Look for: `Setting up ffmpeg...`
3. If missing, verify `render.yaml` is correct
4. Redeploy to retry installation

### WebSocket Disconnects

**Symptom**: Progress updates stop working

**Solution**:
- Frontend auto-reconnects automatically
- Check browser console for connection errors
- Verify backend is running (not spun down)
- Check network connection

### Build Failures

**Backend build fails**:
- Check Render logs for specific errors
- Verify `render.yaml` is in repository root
- Ensure Python dependencies are correct

**Frontend build fails**:
- Check Vercel logs for errors
- Verify `VITE_API_URL` is set
- Ensure root directory is set to `frontend`

---

## Maintenance

### Monthly Tasks

#### 1. Update yt-dlp

Video sites change frequently. Update yt-dlp when downloads fail:

1. Go to Render Dashboard
2. Select your service
3. Click **Manual Deploy** → **Deploy latest commit**
4. Wait 5-10 minutes
5. Test downloads

#### 2. Check Service Health

**Render**:
- Dashboard → Metrics
- Review logs for errors
- Check CPU/memory usage

**Vercel**:
- Dashboard → Analytics
- Check traffic and performance
- Review deployment logs

#### 3. Monitor Disk Usage

Render free tier: 1GB disk

Check usage:
1. Render Dashboard → Shell
2. Run: `df -h /opt/render/project/src/storage`

If disk is full:
- Delete old download records
- Clear temporary files
- Upgrade to larger disk

### Weekly Tasks

1. **Test functionality**: Quick smoke test
2. **Review logs**: Check for recurring errors

### As Needed

- Update when downloads fail (yt-dlp)
- Adjust `MAX_CONCURRENT` if memory issues
- Clean old database records
- Backup database (no auto-backup on free tier)

---

## Cost & Upgrades

### Free Tier (Current Setup)

**Render**:
- 512MB RAM
- Spins down after 15 minutes
- 750 hours/month
- 1GB disk
- **Cost**: $0/month

**Vercel**:
- 100GB bandwidth/month
- Unlimited deployments
- **Cost**: $0/month

**Total**: $0/month

### Paid Tier (Recommended for Production)

**Render Starter** ($7/month):
- Always-on (no spin-down)
- 512MB RAM
- Better performance
- Automatic backups available

**Vercel** (Free tier sufficient):
- Pro plan: $20/month (if needed)
- More bandwidth and features

**Total**: ~$7/month for production-ready setup

### When to Upgrade

Upgrade Render if:
- Backend spins down too often
- Need more RAM for concurrent downloads
- Want automatic backups
- Need better performance

Upgrade Vercel if:
- Exceed 100GB bandwidth/month
- Need team collaboration
- Want advanced analytics

---

## Configuration Files

### render.yaml

Backend deployment configuration using Docker:

```yaml
services:
  - type: web
    name: universal-video-downloader-backend
    runtime: docker
    plan: free
    rootDir: backend
    dockerfilePath: ./Dockerfile
    envVars:
      - key: PORT
        value: 8000
      - key: BIND
        value: 0.0.0.0
      - key: MAX_CONCURRENT
        value: 2
      - key: QUEUE_MAX_SIZE
        value: 100
      - key: DB_PATH
        value: /opt/render/project/src/storage/downloader.db
    disk:
      name: video-storage
      mountPath: /opt/render/project/src/storage
      sizeGB: 1
```

### Dockerfile

Docker image with FFmpeg pre-installed:

```dockerfile
FROM python:3.11-slim

# Install FFmpeg
RUN apt-get update && \
    apt-get install -y ffmpeg && \
    rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Run server
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### vercel.json

Frontend deployment configuration:

```json
{
  "version": 2,
  "buildCommand": "cd frontend && npm install && npm run build",
  "outputDirectory": "frontend/dist",
  "framework": "vite",
  "rewrites": [
    {
      "source": "/(.*)",
      "destination": "/index.html"
    }
  ],
  "env": {
    "VITE_API_URL": "@api_url"
  }
}
```

---

## Security Notes

⚠️ **Important**: This app has no built-in authentication

**Recommendations**:
- Only share with trusted users
- Consider adding authentication for public deployment
- Use Render's IP allowlist feature
- Monitor usage and logs regularly
- Keep dependencies updated

---

## Automatic Deployments

Both platforms auto-deploy when you push to GitHub:

1. Push to `main` branch
2. Render rebuilds backend automatically
3. Vercel rebuilds frontend automatically
4. Changes go live in 5-10 minutes

Already configured! ✅

---

## Custom Domains (Optional)

### Vercel

1. Project Settings → Domains
2. Add your domain
3. Follow DNS configuration

### Render

1. Service Settings → Custom Domain
2. Add your domain
3. Follow DNS configuration

---

## Support Resources

- **Render Docs**: https://render.com/docs
- **Vercel Docs**: https://vercel.com/docs
- **yt-dlp Issues**: https://github.com/yt-dlp/yt-dlp/issues
- **Project Issues**: GitHub repository issues

---

## Summary

✅ FFmpeg automatically installed
✅ yt-dlp always uses latest version
✅ CORS properly configured
✅ WebSocket support enabled
✅ Persistent storage configured
✅ Free tier compatible
✅ Auto-deploy on git push

**Deployment time**: 10-15 minutes
**Cost**: Free tier available
**Maintenance**: Redeploy monthly for yt-dlp updates

---

**Ready to deploy?** Start with [Step 1: Deploy Backend](#step-1-deploy-backend-render)
