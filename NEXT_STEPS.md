# Next Steps - Deploy Your App 🚀

Your code is now on GitHub! Follow these steps to deploy to production.

## ✅ What's Done

- ✅ Code pushed to: https://github.com/Samiul286/Universal-Video-Downloader.git
- ✅ FFmpeg auto-install configured
- ✅ yt-dlp set to always use latest version
- ✅ CORS configured for production
- ✅ All deployment documentation created

## 🚀 Deploy Now (10 Minutes)

### Step 1: Deploy Backend to Render

1. **Go to Render**: https://dashboard.render.com/
2. **Sign up/Login** (use GitHub account for easy connection)
3. **Click "New +"** → **"Web Service"**
4. **Connect Repository**:
   - Click "Connect account" if needed
   - Select: `Samiul286/Universal-Video-Downloader`
5. **Render Auto-Detects** `render.yaml` ✅
6. **Add Environment Variable**:
   - Click "Environment" tab
   - Add: `FRONTEND_URL` = `https://your-app.vercel.app` (you'll get this in Step 2)
   - Leave it empty for now, we'll update it after deploying frontend
7. **Click "Create Web Service"**
8. **Wait 5-10 minutes** for build and deployment
9. **Copy your backend URL**: `https://universal-video-downloader-backend-xxxx.onrender.com`

**Check build logs** to verify FFmpeg installation:
- Look for: "Setting up ffmpeg..."

### Step 2: Deploy Frontend to Vercel

1. **Go to Vercel**: https://vercel.com/dashboard
2. **Sign up/Login** (use GitHub account)
3. **Click "Add New"** → **"Project"**
4. **Import Repository**:
   - Find: `Samiul286/Universal-Video-Downloader`
   - Click "Import"
5. **Configure Project**:
   - Framework Preset: **Vite** (auto-detected)
   - Root Directory: **frontend**
   - Build Command: `npm run build` (auto-detected)
   - Output Directory: `dist` (auto-detected)
6. **Add Environment Variable**:
   - Click "Environment Variables"
   - Name: `VITE_API_URL`
   - Value: Your Render backend URL from Step 1
   - Example: `https://universal-video-downloader-backend-xxxx.onrender.com`
7. **Click "Deploy"**
8. **Wait 2-5 minutes**
9. **Copy your frontend URL**: `https://universal-video-downloader-xxxx.vercel.app`

### Step 3: Update Backend CORS

1. **Go back to Render Dashboard**
2. **Select your web service**
3. **Click "Environment" tab**
4. **Update `FRONTEND_URL`**:
   - Set to your Vercel URL from Step 2
   - Example: `https://universal-video-downloader-xxxx.vercel.app`
5. **Click "Save Changes"**
6. **Render will automatically redeploy** (2-3 minutes)

### Step 4: Test Your App

1. **Visit your Vercel URL**
2. **Paste a YouTube URL**: `https://www.youtube.com/watch?v=dQw4w9WgXcQ`
3. **Click "Extract"** - Should show video info
4. **Select a format** - Choose "Best" or "1080p"
5. **Click "Download"** - Should start downloading
6. **Check progress** - Should see live updates

**If everything works**: 🎉 Congratulations! Your app is live!

## 🔍 Troubleshooting

### Backend Build Fails
- Check Render logs for errors
- Verify `render.yaml` is in repository root
- See: [FFMPEG_SETUP.md](FFMPEG_SETUP.md)

### Frontend Build Fails
- Check Vercel logs
- Verify `VITE_API_URL` is set correctly
- Ensure root directory is set to `frontend`

### CORS Errors in Browser
- Verify `FRONTEND_URL` in Render matches Vercel URL exactly
- No trailing slash in URL
- Wait for Render to finish redeploying

### Downloads Fail
- Check Render logs for specific errors
- Verify FFmpeg was installed (check build logs)
- Try a different video URL
- See: [YTDLP_UPDATES.md](YTDLP_UPDATES.md)

### Backend Not Responding
- Render free tier spins down after 15 minutes
- First request takes 30-60 seconds to wake up
- This is normal on free tier

## 📚 Documentation

- **Quick Guide**: [QUICK_DEPLOY.md](QUICK_DEPLOY.md)
- **Full Guide**: [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md)
- **Checklist**: [DEPLOYMENT_CHECKLIST.md](DEPLOYMENT_CHECKLIST.md)
- **All Docs**: [DEPLOYMENT_INDEX.md](DEPLOYMENT_INDEX.md)

## 🔧 After Deployment

### Set Up Custom Domain (Optional)

**Vercel:**
1. Go to Project Settings → Domains
2. Add your domain
3. Follow DNS configuration instructions

**Render:**
1. Go to Service Settings → Custom Domain
2. Add your domain
3. Follow DNS configuration instructions

### Enable Automatic Deployments

Both platforms auto-deploy when you push to GitHub:
- Push to `main` branch → Automatic deployment
- Already configured! ✅

### Monitor Your App

**Render:**
- Dashboard → Your service → Metrics
- View logs, CPU, memory usage

**Vercel:**
- Dashboard → Your project → Analytics
- View traffic, performance

### Monthly Maintenance

1. **Update yt-dlp** (when downloads fail):
   - Render Dashboard → Manual Deploy
   - See: [MAINTENANCE.md](MAINTENANCE.md)

2. **Check disk usage**:
   - Render Dashboard → Shell
   - Run: `df -h /opt/render/project/src/backend/storage`

3. **Review logs** for errors

## 💰 Cost

### Current Setup (Free Tier)
- **Render**: Free (512MB RAM, spins down after 15 min)
- **Vercel**: Free (100GB bandwidth/month)
- **Total**: $0/month

### Upgrade Options
- **Render Starter**: $7/month (always-on, 512MB RAM)
- **Render Standard**: $25/month (2GB RAM, better performance)
- **Vercel Pro**: $20/month (more bandwidth, team features)

## 🎯 Your URLs

After deployment, save these:

- **Frontend**: `https://universal-video-downloader-xxxx.vercel.app`
- **Backend**: `https://universal-video-downloader-backend-xxxx.onrender.com`
- **API Docs**: `https://universal-video-downloader-backend-xxxx.onrender.com/docs`
- **GitHub**: https://github.com/Samiul286/Universal-Video-Downloader

## 📱 Share Your App

Once deployed, you can share your Vercel URL with:
- Friends and family
- Team members
- Anyone on your trusted network

⚠️ **Security Note**: This app has no authentication. Only share with trusted users.

## 🆘 Need Help?

1. **Check documentation**: [DEPLOYMENT_INDEX.md](DEPLOYMENT_INDEX.md)
2. **Review troubleshooting**: [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md#troubleshooting)
3. **Check platform docs**:
   - Vercel: https://vercel.com/docs
   - Render: https://render.com/docs
4. **Open GitHub issue**: https://github.com/Samiul286/Universal-Video-Downloader/issues

## ✨ Features Included

- ✅ Download videos from 1000+ sites
- ✅ YouTube, TikTok, Vimeo, and more
- ✅ Choose quality/format
- ✅ Live progress updates
- ✅ Playlist support
- ✅ Queue management
- ✅ Pause/resume/cancel
- ✅ FFmpeg for high-quality merging
- ✅ Always up-to-date yt-dlp

## 🎉 You're Ready!

Everything is configured and ready to deploy. Follow the 4 steps above and you'll have a live app in 10-15 minutes!

**Start here**: Step 1 - Deploy Backend to Render

Good luck! 🚀
