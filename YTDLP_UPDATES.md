# yt-dlp Updates and Maintenance

yt-dlp is the core engine that downloads videos from 1000+ sites. Video sites frequently change their APIs, so keeping yt-dlp updated is crucial.

## Current Configuration

### requirements.txt
```
yt-dlp  # Always use latest version
```

This installs the latest yt-dlp version on every deployment.

## Why Updates Matter

Video sites (YouTube, TikTok, etc.) regularly change their APIs to prevent downloading. yt-dlp is updated frequently (often weekly) to fix these issues.

**Symptoms of outdated yt-dlp:**
- "Unable to extract video data"
- "HTTP Error 403: Forbidden"
- "Video unavailable"
- Downloads that worked before suddenly fail

## Automatic Updates on Render

Every time you deploy to Render:
1. Render runs `pip install -r requirements.txt`
2. Latest yt-dlp version is installed
3. Your app gets the newest site extractors

**To force an update:**
1. Go to Render Dashboard → Your service
2. Click **Manual Deploy** → **Deploy latest commit**
3. Render rebuilds with latest yt-dlp

## Manual Updates (Local Development)

Update yt-dlp locally:

```bash
cd backend
source venv/bin/activate  # or .\venv\Scripts\activate on Windows
pip install -U yt-dlp
```

Test the update:
```bash
python -m yt_dlp --version
```

## Version Strategies

### Current: Always Latest (Recommended)
```txt
yt-dlp
```

✅ Best for production
✅ Always compatible with sites
✅ Automatic security fixes

### Alternative: Minimum Version
```txt
yt-dlp>=2024.11.0
```

⚠️ May become outdated
⚠️ Requires manual bumps

### Alternative: Pinned Version
```txt
yt-dlp==2024.11.0
```

❌ Not recommended
❌ Will break as sites change
❌ Requires frequent manual updates

## Checking yt-dlp Version

### On Render (Production)

1. Go to Render Dashboard → Your service → **Shell**
2. Run:
   ```bash
   python -c "import yt_dlp; print(yt_dlp.version.__version__)"
   ```

### Locally

```bash
cd backend
source venv/bin/activate
python -c "import yt_dlp; print(yt_dlp.version.__version__)"
```

Or:
```bash
python -m yt_dlp --version
```

## Update Schedule

yt-dlp releases:
- **Frequency**: Multiple times per week
- **Why**: Sites break frequently
- **Where**: https://github.com/yt-dlp/yt-dlp/releases

**Recommended**: Redeploy monthly or when downloads start failing.

## Troubleshooting

### Downloads Suddenly Stop Working

**Likely cause**: Site changed API, yt-dlp needs update

**Solution**:
1. Check yt-dlp releases: https://github.com/yt-dlp/yt-dlp/releases
2. Redeploy on Render (gets latest version)
3. Test the problematic URL again

### Specific Site Not Working

**Check if site is supported**:
```bash
python -m yt_dlp --list-extractors | grep -i youtube
```

**Test extraction locally**:
```bash
python -m yt_dlp --skip-download "https://youtube.com/watch?v=..."
```

### "No module named 'yt_dlp'"

**Cause**: yt-dlp not installed

**Solution**:
```bash
pip install yt-dlp
```

## Monitoring yt-dlp Updates

### GitHub Watch
1. Go to https://github.com/yt-dlp/yt-dlp
2. Click **Watch** → **Custom** → **Releases**
3. Get notified of new versions

### RSS Feed
Subscribe to: https://github.com/yt-dlp/yt-dlp/releases.atom

## Breaking Changes

yt-dlp rarely has breaking changes, but when they occur:

1. Check release notes: https://github.com/yt-dlp/yt-dlp/releases
2. Test locally before deploying
3. Pin version temporarily if needed:
   ```txt
   yt-dlp==2024.11.0  # Pin to last working version
   ```
4. Wait for fix or adjust code

## Performance Considerations

### Build Time
- Latest version: +10-30 seconds build time
- Pinned version: Faster (cached)

**Recommendation**: Accept longer build for better compatibility

### Runtime Performance
- yt-dlp version doesn't significantly affect runtime
- Newer versions may be faster due to optimizations

## Security

yt-dlp security updates are critical:
- Fixes for malicious video URLs
- Fixes for code execution vulnerabilities
- Always use latest for security

## Alternative: Nightly Builds

For bleeding-edge fixes:

```txt
yt-dlp @ git+https://github.com/yt-dlp/yt-dlp.git@master
```

⚠️ **Not recommended for production** - may be unstable

## Rollback Strategy

If new yt-dlp version causes issues:

1. **Quick fix**: Pin to previous version
   ```txt
   yt-dlp==2024.10.0  # Replace with last working version
   ```

2. **Redeploy** on Render

3. **Report issue**: https://github.com/yt-dlp/yt-dlp/issues

4. **Wait for fix** or investigate

## Best Practices

✅ Use `yt-dlp` (no version) in requirements.txt
✅ Redeploy monthly or when issues occur
✅ Monitor yt-dlp releases
✅ Test locally before deploying
✅ Keep FFmpeg updated too (for format merging)

❌ Don't pin to old versions
❌ Don't ignore download failures
❌ Don't skip testing after updates

## Testing After Update

After updating yt-dlp, test these scenarios:

1. **YouTube video**: Standard video
2. **YouTube playlist**: Multiple videos
3. **Age-restricted**: Requires cookies
4. **High quality**: Tests FFmpeg merge
5. **Other sites**: TikTok, Vimeo, etc.

## Automation (Advanced)

### Auto-redeploy on yt-dlp Release

Create GitHub Action (`.github/workflows/auto-update-ytdlp.yml`):

```yaml
name: Auto-update yt-dlp

on:
  schedule:
    - cron: '0 0 * * 0'  # Weekly on Sunday
  workflow_dispatch:

jobs:
  check-update:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Check yt-dlp version
        run: |
          pip install yt-dlp
          python -m yt_dlp --version
      
      - name: Trigger Render Deploy
        run: |
          curl -X POST "${{ secrets.RENDER_DEPLOY_HOOK }}"
```

Set `RENDER_DEPLOY_HOOK` in GitHub secrets.

## Summary

- ✅ yt-dlp is already configured in requirements.txt
- ✅ Updated to always use latest version
- ✅ Automatic updates on every Render deployment
- ✅ No additional configuration needed
- ✅ Redeploy monthly or when downloads fail

For issues, check:
1. yt-dlp releases: https://github.com/yt-dlp/yt-dlp/releases
2. Supported sites: https://github.com/yt-dlp/yt-dlp/blob/master/supportedsites.md
3. Report bugs: https://github.com/yt-dlp/yt-dlp/issues
