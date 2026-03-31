# yt-dlp Configuration Summary

## Status: ✅ Optimized for Production

yt-dlp is properly configured and will stay up-to-date automatically.

## What Changed

### requirements.txt
**Before:**
```txt
yt-dlp>=2024.11.0
```

**After:**
```txt
yt-dlp  # Always use latest version for best site compatibility
```

**Why:** Video sites change frequently. Using the latest version ensures maximum compatibility.

## How It Works

### On Render Deployment
1. Render runs `pip install -r requirements.txt`
2. Latest yt-dlp version is installed automatically
3. Your app gets newest site extractors and fixes

### Benefits
✅ Always compatible with latest site changes
✅ Automatic security updates
✅ New site support automatically
✅ Bug fixes without manual intervention
✅ No version management needed

## Maintenance

### When to Redeploy

Redeploy to get latest yt-dlp when:
- Downloads start failing for specific sites
- Monthly maintenance (recommended)
- After major yt-dlp releases

### How to Redeploy

1. Go to [Render Dashboard](https://dashboard.render.com/)
2. Select your service
3. Click **Manual Deploy** → **Deploy latest commit**
4. Wait 5-10 minutes
5. Test downloads

## Monitoring yt-dlp Updates

### GitHub Releases
Watch: https://github.com/yt-dlp/yt-dlp/releases

Typical release frequency:
- **Major updates**: Weekly
- **Hotfixes**: As needed (sometimes daily)
- **Breaking changes**: Rare (well documented)

### Signs You Need to Update

- ❌ "Unable to extract video data"
- ❌ "HTTP Error 403: Forbidden"
- ❌ "Video unavailable"
- ❌ Downloads that worked before suddenly fail
- ❌ Specific sites stop working

**Solution:** Redeploy on Render to get latest yt-dlp

## Version Information

### Check Current Version

**On Render (Production):**
1. Go to Dashboard → Your service → **Shell**
2. Run:
```bash
python -c "import yt_dlp; print(yt_dlp.version.__version__)"
```

**Locally:**
```bash
cd backend
source venv/bin/activate
python -m yt_dlp --version
```

### Latest Version
Check: https://github.com/yt-dlp/yt-dlp/releases/latest

## Troubleshooting

### Specific Site Not Working

1. **Check if site is supported:**
   - List: https://github.com/yt-dlp/yt-dlp/blob/master/supportedsites.md
   - Or run: `python -m yt_dlp --list-extractors`

2. **Test locally:**
   ```bash
   python -m yt_dlp --skip-download "https://example.com/video"
   ```

3. **Check yt-dlp issues:**
   - Search: https://github.com/yt-dlp/yt-dlp/issues
   - Report if new: https://github.com/yt-dlp/yt-dlp/issues/new

4. **Try with latest version:**
   - Redeploy on Render
   - Or update locally: `pip install -U yt-dlp`

### Age-Restricted Content

Some videos require cookies:
1. Export cookies from browser (Netscape format)
2. Use "Use my cookies" feature in app
3. Or set `COOKIES_PATH` in Render environment variables

### Geo-Blocked Content

Some videos are region-locked:
1. Set `PROXY` environment variable in Render
2. Use a proxy in the allowed region
3. Format: `http://proxy.example.com:8080`

## Documentation

### Comprehensive Guides
- **[YTDLP_UPDATES.md](YTDLP_UPDATES.md)** - Detailed update guide
- **[MAINTENANCE.md](MAINTENANCE.md)** - Monthly maintenance tasks
- **[docs/DEPLOYMENT.md](docs/DEPLOYMENT.md)** - Full deployment guide

### Quick References
- **[QUICK_DEPLOY.md](QUICK_DEPLOY.md)** - 10-minute deployment
- **[DEPLOYMENT_CHECKLIST.md](DEPLOYMENT_CHECKLIST.md)** - Step-by-step checklist

## Best Practices

✅ **Do:**
- Use latest version (no version pinning)
- Redeploy monthly for updates
- Monitor yt-dlp releases
- Test after major updates
- Report issues to yt-dlp project

❌ **Don't:**
- Pin to old versions
- Ignore download failures
- Skip testing after updates
- Use outdated extractors

## Performance Impact

### Build Time
- **Latest version**: +10-30 seconds
- **Worth it**: Yes, for compatibility

### Runtime Performance
- No significant impact
- Newer versions may be faster
- Better error handling

### Disk Space
- yt-dlp: ~10-15MB
- Negligible impact on 1GB disk

## Security

yt-dlp security updates are critical:
- ✅ Fixes for malicious URLs
- ✅ Code execution vulnerability patches
- ✅ Dependency security updates

**Always use latest for security.**

## Alternative Strategies

### If You Need Stability

Pin to specific version (not recommended):
```txt
yt-dlp==2024.11.0
```

**Cons:**
- Will break as sites change
- Requires manual updates
- Security vulnerabilities

### If You Need Bleeding Edge

Use nightly builds (not recommended for production):
```txt
yt-dlp @ git+https://github.com/yt-dlp/yt-dlp.git@master
```

**Cons:**
- May be unstable
- Longer build times
- Potential breaking changes

## Summary

✅ yt-dlp configured to always use latest version
✅ Automatic updates on every Render deployment
✅ No manual version management needed
✅ Maximum site compatibility
✅ Automatic security updates
✅ Redeploy monthly or when downloads fail

**No action required** - configuration is already optimal!

## Support

- yt-dlp issues: https://github.com/yt-dlp/yt-dlp/issues
- Supported sites: https://github.com/yt-dlp/yt-dlp/blob/master/supportedsites.md
- yt-dlp docs: https://github.com/yt-dlp/yt-dlp#readme
- Project docs: See repository README
