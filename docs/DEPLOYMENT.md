# Deployment Guide

This guide covers deploying the Universal Video Downloader to:
- **Vercel** (Frontend - React/Vite)
- **Render** (Backend - FastAPI/Python)

## Overview

The app consists of two parts:
1. **Frontend**: Static React app (Vite build) → Deploy to Vercel
2. **Backend**: FastAPI Python server → Deploy to Render

## Prerequisites

- GitHub account (for connecting to Vercel and Render)
- Vercel account (free tier available)
- Render account (free tier available)

## Part 1: Deploy Backend to Render

### Step 1: Prepare Your Repository

Ensure `render.yaml` is in your repository root (already created).

### Step 2: Create Render Web Service

1. Go to [Render Dashboard](https://dashboard.render.com/)
2. Click **New +** → **Web Service**
3. Connect your GitHub repository
4. Render will auto-detect `render.yaml` configuration

### Step 3: Configure Environment Variables

In Render dashboard, add these environment variables:


| Variable | Value | Required |
|----------|-------|----------|
| `FRONTEND_URL` | Your Vercel URL (e.g., `https://your-app.vercel.app`) | Yes |
| `PORT` | 8000 (or use Render's default) | No |
| `MAX_CONCURRENT` | 2 | No |
| `QUEUE_MAX_SIZE` | 100 | No |

**Important Notes:**
- Render's free tier has limitations (512MB RAM, spins down after inactivity)
- FFmpeg is automatically installed during build (configured in `render.yaml`)
- The app will work for all downloads including those requiring FFmpeg (merging video+audio)

### Step 4: Deploy

1. Click **Create Web Service**
2. Wait for build and deployment (5-10 minutes)
3. Note your backend URL: `https://your-app.onrender.com`

### Step 5: Test Backend

Visit `https://your-app.onrender.com/docs` to see the API documentation.

## Part 2: Deploy Frontend to Vercel

### Step 1: Update Frontend API Configuration

The frontend needs to know your backend URL. Update the API base URL:

1. In `frontend/src/services/api.ts`, the axios instance uses `baseURL: ''` (relative URLs)
2. For production, we'll use Vercel environment variables

### Step 2: Create Vercel Project

1. Go to [Vercel Dashboard](https://vercel.com/dashboard)
2. Click **Add New** → **Project**
3. Import your GitHub repository
4. Vercel will auto-detect it's a Vite project

### Step 3: Configure Build Settings

Vercel should auto-detect these settings (verify/update if needed):

- **Framework Preset**: Vite
- **Root Directory**: `frontend`
- **Build Command**: `npm run build`
- **Output Directory**: `dist`

### Step 4: Add Environment Variables

In Vercel project settings → Environment Variables, add:

| Variable | Value | Description |
|----------|-------|-------------|
| `VITE_API_URL` | `https://your-app.onrender.com` | Your Render backend URL |

### Step 5: Update Frontend Code for Production

Create a production-ready API configuration:

```typescript
// frontend/src/services/api.ts
const API_BASE_URL = import.meta.env.VITE_API_URL || '';
const api = axios.create({ baseURL: API_BASE_URL, timeout: 30000 });
```

And for WebSocket:

```typescript
// frontend/src/services/progressWs.ts
export function getProgressWsUrl(): string {
  const apiUrl = import.meta.env.VITE_API_URL;
  if (apiUrl) {
    // Production: use backend URL
    const url = new URL(apiUrl);
    const protocol = url.protocol === 'https:' ? 'wss:' : 'ws:';
    return `${protocol}//${url.host}/ws/progress`;
  }
  // Development: use same origin
  const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
  const host = window.location.host;
  return `${protocol}//${host}/ws/progress`;
}
```

### Step 6: Deploy

1. Click **Deploy**
2. Wait for build (2-5 minutes)
3. Your app will be live at `https://your-app.vercel.app`

### Step 7: Update Backend CORS

Go back to Render and update the `FRONTEND_URL` environment variable:
- Set it to your Vercel URL: `https://your-app.vercel.app`
- Render will automatically redeploy

## Part 3: Verification

1. Visit your Vercel URL: `https://your-app.vercel.app`
2. Try extracting a video URL
3. Check browser console for any CORS or connection errors
4. Verify WebSocket connection works (progress updates)

## Troubleshooting

### CORS Errors

If you see CORS errors in browser console:
1. Verify `FRONTEND_URL` is set correctly in Render
2. Make sure it matches your Vercel URL exactly (no trailing slash)
3. Redeploy backend after changing environment variables

### WebSocket Connection Failed

1. Check that your backend URL uses HTTPS (Render provides this)
2. Verify the WebSocket URL is using `wss://` protocol
3. Check Render logs for WebSocket connection attempts

### Backend Spins Down (Render Free Tier)

Render's free tier spins down after 15 minutes of inactivity:
- First request after spin-down takes 30-60 seconds
- Consider upgrading to paid tier for always-on service
- Or implement a keep-alive ping from frontend

### Downloads Fail for Specific Sites

If downloads suddenly stop working for certain sites:
1. **yt-dlp may need updating** - Video sites change frequently
2. Redeploy on Render to get latest yt-dlp version
3. See [YTDLP_UPDATES.md](../YTDLP_UPDATES.md) for details
4. Check yt-dlp releases: https://github.com/yt-dlp/yt-dlp/releases

### FFmpeg Installation

FFmpeg is automatically installed during the build process via the `render.yaml` configuration:

```yaml
buildCommand: |
  apt-get update && apt-get install -y ffmpeg
  cd backend && pip install -r requirements.txt
```

This works on both free and paid Render tiers. Downloads requiring video+audio merge will work correctly.

#### Verify FFmpeg Installation

After deployment, check Render logs to verify FFmpeg was installed:

1. Go to Render dashboard → Your service → Logs
2. Look for build logs showing:
   ```
   Setting up ffmpeg...
   Done.
   ```

#### If FFmpeg Installation Fails

If you see errors during FFmpeg installation:

1. **Check build logs** for specific error messages
2. **Try alternative build command** (add to `render.yaml`):
   ```yaml
   buildCommand: |
     apt-get update
     apt-get install -y --no-install-recommends ffmpeg
     cd backend && pip install -r requirements.txt
   ```

3. **Use static FFmpeg binary** (if apt-get fails):
   ```yaml
   buildCommand: |
     wget https://johnvansickle.com/ffmpeg/releases/ffmpeg-release-amd64-static.tar.xz
     tar xf ffmpeg-release-amd64-static.tar.xz
     cp ffmpeg-*-amd64-static/ffmpeg /usr/local/bin/
     cd backend && pip install -r requirements.txt
   ```

4. **Set FFMPEG_PATH** environment variable in Render:
   - Key: `FFMPEG_PATH`
   - Value: `/usr/bin/ffmpeg` (or path to static binary)

#### Test FFmpeg

To verify FFmpeg works after deployment, check the backend logs on startup. The app validates FFmpeg on startup and logs a warning if not found.

For detailed FFmpeg troubleshooting, see **[FFMPEG_SETUP.md](../FFMPEG_SETUP.md)**.

### Database Persistence

Render free tier filesystem is ephemeral:
- Use the disk mount configured in `render.yaml`
- Or upgrade to use Render's PostgreSQL (requires code changes)

## Alternative: Deploy Both to Render

If you prefer to deploy both frontend and backend to Render:

1. Add a static site service to `render.yaml`:
```yaml
- type: web
  name: universal-video-downloader-frontend
  runtime: static
  buildCommand: cd frontend && npm install && npm run build
  staticPublishPath: frontend/dist
  envVars:
    - key: VITE_API_URL
      value: https://your-backend.onrender.com
```

2. Deploy as a single repository with both services

## Cost Estimates

### Free Tier (Both Platforms)
- **Vercel**: 100GB bandwidth/month, unlimited deployments
- **Render**: 750 hours/month, 512MB RAM, spins down after inactivity
- **Total**: $0/month (with limitations)

### Paid Tier Recommendations
- **Render**: $7/month for always-on, 512MB RAM
- **Vercel**: Free tier usually sufficient for frontend
- **Total**: ~$7/month for production-ready setup

## Security Considerations

1. **No Authentication**: This app has no built-in auth
   - Only deploy on trusted networks
   - Consider adding authentication layer
   - Use Render's IP allowlist feature

2. **Rate Limiting**: Consider adding rate limiting to prevent abuse

3. **HTTPS**: Both Vercel and Render provide free SSL certificates

## Next Steps

- Set up custom domain (both platforms support this)
- Configure monitoring and alerts
- Set up automatic deployments on git push
- Consider adding authentication
- Monitor usage and costs

## Maintenance

### Keep yt-dlp Updated

Video sites change frequently. Redeploy monthly or when downloads fail:

1. Go to Render Dashboard → Your service
2. Click **Manual Deploy** → **Deploy latest commit**
3. Latest yt-dlp version will be installed

See [YTDLP_UPDATES.md](../YTDLP_UPDATES.md) for details.

### Monitor Service Health

- Check Render logs regularly for errors
- Monitor Vercel analytics for frontend issues
- Set up uptime monitoring (e.g., UptimeRobot)
- Watch yt-dlp releases: https://github.com/yt-dlp/yt-dlp/releases

### Database Backups

Render's disk is persistent but not backed up on free tier:
- Download database periodically: `/opt/render/project/src/backend/storage/downloader.db`
- Or upgrade to paid tier with automatic backups
- Or migrate to PostgreSQL for better reliability

## Support

For deployment issues:
- Vercel: https://vercel.com/docs
- Render: https://render.com/docs
- FFmpeg setup: See [FFMPEG_SETUP.md](../FFMPEG_SETUP.md)
- yt-dlp updates: See [YTDLP_UPDATES.md](../YTDLP_UPDATES.md)
- Project issues: GitHub repository issues page
