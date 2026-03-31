# Maintenance Guide

Keep your deployed Universal Video Downloader running smoothly.

## Monthly Tasks

### 1. Update yt-dlp (Critical)

Video sites change frequently. Update yt-dlp monthly or when downloads fail.

**How to update:**
1. Go to [Render Dashboard](https://dashboard.render.com/)
2. Select your service
3. Click **Manual Deploy** → **Deploy latest commit**
4. Wait for deployment (5-10 minutes)
5. Test with a video download

**Why:** yt-dlp is updated weekly to fix broken site extractors.

**See:** [YTDLP_UPDATES.md](YTDLP_UPDATES.md) for details.

### 2. Check Service Health

**Render (Backend):**
- Go to Dashboard → Your service → **Metrics**
- Check for errors or crashes
- Review **Logs** for warnings

**Vercel (Frontend):**
- Go to Dashboard → Your project → **Analytics**
- Check for errors or slow performance
- Review deployment logs

### 3. Monitor Disk Usage

**Render free tier: 1GB disk**

Check disk usage:
1. Go to Render Dashboard → Your service → **Shell**
2. Run: `df -h /opt/render/project/src/backend/storage`

If disk is full:
- Delete old download records from database
- Clear temporary files
- Upgrade to larger disk (paid tier)

## Weekly Tasks

### 1. Test Core Functionality

Quick smoke test:
1. Visit your app URL
2. Paste a YouTube URL
3. Click **Extract**
4. Verify formats appear
5. Start a download
6. Verify progress updates work

### 2. Review Logs

Check for recurring errors:
- Render: Dashboard → Logs
- Vercel: Dashboard → Deployments → View Function Logs

Common issues to look for:
- FFmpeg errors
- yt-dlp extraction failures
- Database errors
- Memory issues

## As Needed

### When Downloads Start Failing

**Symptoms:**
- "Unable to extract video data"
- "HTTP Error 403"
- Specific sites stop working

**Solution:**
1. Check if it's a yt-dlp issue
2. Redeploy to get latest yt-dlp
3. Check site-specific issues: https://github.com/yt-dlp/yt-dlp/issues
4. Test with cookies if age-restricted

### When Backend is Slow

**Render free tier spins down after 15 minutes**

**Solutions:**
- Accept 30-60 second cold start
- Upgrade to paid tier ($7/month, always-on)
- Implement keep-alive ping (not recommended, wastes resources)

### When Memory Issues Occur

**Symptoms:**
- Downloads fail with "Out of memory"
- Backend crashes during downloads

**Solutions:**
1. Reduce `MAX_CONCURRENT` in Render environment variables:
   - Set to `1` for free tier (512MB RAM)
   - Set to `2-3` for paid tier
2. Upgrade to paid tier with more RAM
3. Avoid downloading very large files simultaneously

### When Disk is Full

**Symptoms:**
- "No space left on device"
- Database errors

**Solutions:**
1. Clean up old downloads:
   - Delete completed downloads from UI
   - Or manually clean database
2. Increase disk size (Render settings)
3. Implement automatic cleanup (code change needed)

## Database Maintenance

### Backup Database

**Free tier:** No automatic backups

**Manual backup:**
1. Go to Render Dashboard → Your service → **Shell**
2. Run: `cat /opt/render/project/src/backend/storage/downloader.db > backup.db`
3. Download the file

**Paid tier:** Enable automatic backups in Render settings

### Clean Old Records

If database grows too large:

1. Connect to Render Shell
2. Run Python script:
```python
import sqlite3
conn = sqlite3.connect('/opt/render/project/src/backend/storage/downloader.db')
cursor = conn.cursor()
# Delete downloads older than 30 days
cursor.execute("DELETE FROM downloads WHERE created_at < datetime('now', '-30 days')")
conn.commit()
print(f"Deleted {cursor.rowcount} old records")
conn.close()
```

## Security Maintenance

### 1. Review Access

This app has no authentication. Ensure:
- Only trusted users have the URL
- Consider adding authentication if public
- Use Render's IP allowlist if needed

### 2. Monitor for Abuse

Check logs for:
- Excessive download requests
- Unusual traffic patterns
- Failed authentication attempts (if you add auth)

### 3. Update Dependencies

**Backend:**
```bash
cd backend
pip list --outdated
```

Update carefully (test locally first):
```bash
pip install -U fastapi uvicorn pydantic
```

**Frontend:**
```bash
cd frontend
npm outdated
npm update
```

## Performance Optimization

### 1. Optimize Concurrent Downloads

Adjust `MAX_CONCURRENT` based on:
- Free tier: 1-2
- Paid tier (512MB): 2-3
- Paid tier (1GB+): 3-5

### 2. Monitor Response Times

Use Vercel Analytics to track:
- API response times
- Frontend load times
- User experience metrics

### 3. Optimize Database

If queries are slow:
1. Add indexes (code change)
2. Clean old records
3. Upgrade to PostgreSQL (paid tier)

## Monitoring Setup (Optional)

### Uptime Monitoring

Use free services:
- **UptimeRobot**: https://uptimerobot.com/
- **Pingdom**: https://www.pingdom.com/
- **StatusCake**: https://www.statuscake.com/

Monitor:
- Frontend URL (Vercel)
- Backend health endpoint: `/health`

### Error Tracking

Consider adding:
- **Sentry**: Error tracking for both frontend and backend
- **LogRocket**: Session replay for frontend issues

### Analytics

Track usage:
- Vercel Analytics (built-in)
- Google Analytics (add to frontend)
- Custom metrics in backend logs

## Upgrade Considerations

### When to Upgrade Render

Consider paid tier ($7/month) if:
- Backend spins down too often (>15 min inactivity)
- Need more RAM for concurrent downloads
- Want automatic backups
- Need better performance

### When to Upgrade Vercel

Vercel free tier is usually sufficient. Upgrade if:
- Exceed 100GB bandwidth/month
- Need team collaboration features
- Want advanced analytics

## Troubleshooting Common Issues

### Issue: "Service Unavailable"

**Cause:** Backend spinning down (free tier)

**Solution:** Wait 30-60 seconds for cold start

### Issue: Downloads fail randomly

**Cause:** yt-dlp outdated or site changes

**Solution:** Redeploy to update yt-dlp

### Issue: CORS errors

**Cause:** `FRONTEND_URL` mismatch

**Solution:** 
1. Check Render environment variables
2. Ensure `FRONTEND_URL` matches Vercel URL exactly
3. Redeploy backend

### Issue: WebSocket disconnects

**Cause:** Network issues or backend restart

**Solution:** Frontend should auto-reconnect (check logs)

## Maintenance Checklist

### Monthly
- [ ] Update yt-dlp (redeploy on Render)
- [ ] Review service health metrics
- [ ] Check disk usage
- [ ] Backup database (if needed)
- [ ] Review logs for errors

### Weekly
- [ ] Test core functionality
- [ ] Quick log review

### As Needed
- [ ] Update dependencies
- [ ] Clean old database records
- [ ] Adjust concurrent download limits
- [ ] Review and optimize performance

## Support Resources

- **yt-dlp issues**: https://github.com/yt-dlp/yt-dlp/issues
- **Render docs**: https://render.com/docs
- **Vercel docs**: https://vercel.com/docs
- **Project docs**: See repository README and docs/

## Automation Ideas

### Auto-update yt-dlp

Set up GitHub Action to redeploy weekly:
```yaml
# .github/workflows/weekly-update.yml
name: Weekly Update
on:
  schedule:
    - cron: '0 0 * * 0'  # Sunday midnight
jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - name: Trigger Render Deploy
        run: curl -X POST "${{ secrets.RENDER_DEPLOY_HOOK }}"
```

### Auto-cleanup Database

Add cron job in backend to clean old records automatically (code change needed).

### Health Check Alerts

Use monitoring service to alert when:
- Backend is down
- Response time > 5 seconds
- Error rate > 5%

## Summary

✅ Update yt-dlp monthly (redeploy)
✅ Monitor service health weekly
✅ Backup database periodically
✅ Watch for disk space issues
✅ Review logs for errors
✅ Test functionality regularly
✅ Consider upgrades if needed

Most maintenance is automated. Main task is keeping yt-dlp updated by redeploying monthly.
