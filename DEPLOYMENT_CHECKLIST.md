# Deployment Checklist

Quick reference for deploying to Vercel + Render.

## Pre-Deployment

- [ ] Commit all changes to GitHub
- [ ] Test locally (backend + frontend)
- [ ] Review `render.yaml` configuration
- [ ] Review `vercel.json` configuration

## Backend (Render)

- [ ] Create Render account
- [ ] Connect GitHub repository
- [ ] Create new Web Service
- [ ] Verify `render.yaml` is detected
- [ ] Verify FFmpeg installation in build command
- [ ] Add environment variables:
  - [ ] `FRONTEND_URL` (will be your Vercel URL)
  - [ ] `PORT` (optional, default 8000)
  - [ ] `MAX_CONCURRENT` (optional, default 2)
- [ ] Deploy and wait for build
- [ ] Check build logs for FFmpeg installation
- [ ] Copy backend URL: `https://your-app.onrender.com`
- [ ] Test API docs: `https://your-app.onrender.com/docs`

## Frontend (Vercel)

- [ ] Create Vercel account
- [ ] Import GitHub repository
- [ ] Configure project:
  - [ ] Framework: Vite
  - [ ] Root Directory: `frontend`
  - [ ] Build Command: `npm run build`
  - [ ] Output Directory: `dist`
- [ ] Add environment variable:
  - [ ] `VITE_API_URL` = `https://your-app.onrender.com`
- [ ] Deploy and wait for build
- [ ] Copy frontend URL: `https://your-app.vercel.app`

## Post-Deployment

- [ ] Update Render environment variable:
  - [ ] Set `FRONTEND_URL` to your Vercel URL
  - [ ] Wait for automatic redeploy
- [ ] Test the app:
  - [ ] Visit Vercel URL
  - [ ] Try extracting a video
  - [ ] Check browser console for errors
  - [ ] Verify WebSocket connection works
  - [ ] Test high-quality download (to verify FFmpeg)
- [ ] Check for CORS errors
- [ ] Verify downloads work
- [ ] Check Render logs for FFmpeg validation message

## Optional

- [ ] Set up custom domain on Vercel
- [ ] Set up custom domain on Render
- [ ] Configure monitoring/alerts
- [ ] Set up automatic deployments
- [ ] Review security settings
- [ ] Consider upgrading to paid tier for FFmpeg support

## Troubleshooting

If something doesn't work:
1. Check browser console for errors
2. Check Render logs for backend errors
3. Verify environment variables are set correctly
4. Ensure CORS is configured properly
5. Verify FFmpeg is installed (check build logs)
6. See FFmpeg guide: `FFMPEG_SETUP.md`
7. See full guide: `docs/DEPLOYMENT.md`

## Quick Links

- Vercel Dashboard: https://vercel.com/dashboard
- Render Dashboard: https://dashboard.render.com/
- Full Deployment Guide: `docs/DEPLOYMENT.md`
