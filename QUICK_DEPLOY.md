# Quick Deploy Guide

Deploy in 10 minutes. Follow these steps in order.

## 1. Deploy Backend (Render)

1. Go to https://dashboard.render.com/
2. Click **New +** → **Web Service**
3. Connect your GitHub repo
4. Render detects `render.yaml` automatically
5. Add environment variable:
   - `FRONTEND_URL` = `https://your-app.vercel.app` (you'll get this in step 2)
6. Click **Create Web Service**
7. Wait 5-10 minutes for deployment
8. Copy your backend URL: `https://your-app.onrender.com`

## 2. Deploy Frontend (Vercel)

1. Go to https://vercel.com/dashboard
2. Click **Add New** → **Project**
3. Import your GitHub repo
4. Configure:
   - Framework: **Vite**
   - Root Directory: **frontend**
   - Build Command: `npm run build`
   - Output Directory: `dist`
5. Add environment variable:
   - `VITE_API_URL` = `https://your-app.onrender.com` (from step 1)
6. Click **Deploy**
7. Wait 2-5 minutes
8. Copy your frontend URL: `https://your-app.vercel.app`

## 3. Update Backend CORS

1. Go back to Render dashboard
2. Open your web service
3. Go to **Environment** tab
4. Update `FRONTEND_URL` to your Vercel URL from step 2
5. Save (Render will auto-redeploy)

## 4. Test

1. Visit your Vercel URL
2. Paste a YouTube URL
3. Click **Extract**
4. Choose a format
5. Click **Download**

## Done! 🎉

Your app is now live at `https://your-app.vercel.app`

## Troubleshooting

**CORS errors?**
- Make sure `FRONTEND_URL` in Render matches your Vercel URL exactly

**Backend not responding?**
- Render free tier spins down after 15 minutes
- First request takes 30-60 seconds to wake up

**Downloads failing?**
- Check Render logs for specific error messages
- Verify the video URL is accessible
- Some sites may require cookies for authentication

## Need More Help?

- Full guide: `docs/DEPLOYMENT.md`
- Checklist: `DEPLOYMENT_CHECKLIST.md`
- Summary: `DEPLOYMENT_SUMMARY.md`
- FFmpeg issues: `FFMPEG_SETUP.md`
