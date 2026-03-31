# FFmpeg Setup for Render Deployment

FFmpeg is required for merging video and audio streams when downloading high-quality videos.

## Automatic Installation (Default)

The `render.yaml` configuration automatically installs FFmpeg during build:

```yaml
buildCommand: |
  apt-get update && apt-get install -y ffmpeg
  cd backend && pip install -r requirements.txt
```

This works on Render's free tier and requires no additional configuration.

## Verify Installation

After deploying to Render:

1. Go to **Render Dashboard** → Your service → **Logs**
2. Click **Deploy** tab to see build logs
3. Look for:
   ```
   Setting up ffmpeg (7:4.4.2-0ubuntu0.22.04.1) ...
   ```

4. Check runtime logs for:
   ```
   INFO: FFmpeg found at /usr/bin/ffmpeg
   ```

## Alternative Installation Methods

If the default method fails, try these alternatives:

### Method 1: No Recommends (Smaller Install)

```yaml
buildCommand: |
  apt-get update
  apt-get install -y --no-install-recommends ffmpeg
  cd backend && pip install -r requirements.txt
```

### Method 2: Static Binary (Most Reliable)

```yaml
buildCommand: |
  wget -q https://johnvansickle.com/ffmpeg/releases/ffmpeg-release-amd64-static.tar.xz
  tar xf ffmpeg-release-amd64-static.tar.xz
  cp ffmpeg-*-amd64-static/ffmpeg /usr/local/bin/
  chmod +x /usr/local/bin/ffmpeg
  cd backend && pip install -r requirements.txt
```

Then add environment variable in Render:
- Key: `FFMPEG_PATH`
- Value: `/usr/local/bin/ffmpeg`

### Method 3: From Source (Advanced)

Only use if other methods fail:

```yaml
buildCommand: |
  apt-get update
  apt-get install -y build-essential yasm pkg-config
  wget https://ffmpeg.org/releases/ffmpeg-6.0.tar.xz
  tar xf ffmpeg-6.0.tar.xz
  cd ffmpeg-6.0
  ./configure --disable-x86asm
  make -j$(nproc)
  make install
  cd ..
  cd backend && pip install -r requirements.txt
```

⚠️ Warning: This takes 10-15 minutes to build and may timeout on free tier.

## Troubleshooting

### Build Fails with "Unable to locate package ffmpeg"

**Cause**: apt repositories not updated or unavailable

**Solution**: Ensure `apt-get update` runs before install:
```yaml
buildCommand: |
  apt-get update -y
  apt-get install -y ffmpeg
  cd backend && pip install -r requirements.txt
```

### Build Succeeds but FFmpeg Not Found at Runtime

**Cause**: FFmpeg installed but not in PATH

**Solution**: Set `FFMPEG_PATH` environment variable in Render:
1. Go to service → **Environment** tab
2. Add variable:
   - Key: `FFMPEG_PATH`
   - Value: `/usr/bin/ffmpeg`
3. Save and redeploy

### Downloads Fail with "ffmpeg not found"

**Cause**: FFmpeg not installed or not accessible

**Solution**: Check logs and verify installation:
1. View Render logs
2. Look for FFmpeg validation message on startup
3. Try manual verification (see below)

### Manual Verification

Add a test command to verify FFmpeg after build:

```yaml
buildCommand: |
  apt-get update && apt-get install -y ffmpeg
  which ffmpeg || echo "FFmpeg not found in PATH"
  ffmpeg -version || echo "FFmpeg not executable"
  cd backend && pip install -r requirements.txt
```

Check build logs for output.

## Testing FFmpeg

After deployment, test with a video that requires merging:

1. Go to your deployed app
2. Paste a YouTube URL
3. Click **Extract**
4. Choose a high-quality format (e.g., "1080p")
5. Click **Download**
6. Check if download completes successfully

If it fails, check Render logs for FFmpeg-related errors.

## Performance Considerations

### Free Tier
- 512MB RAM may limit concurrent downloads
- Set `MAX_CONCURRENT=1` if you experience memory issues
- FFmpeg uses ~100-200MB RAM per active download

### Paid Tier ($7/month)
- More RAM available
- Can increase `MAX_CONCURRENT` to 3-5
- Always-on (no spin-down)

## Environment Variables

Add these to Render if needed:

| Variable | Value | Purpose |
|----------|-------|---------|
| `FFMPEG_PATH` | `/usr/bin/ffmpeg` | Explicit FFmpeg location |
| `MAX_CONCURRENT` | `1` or `2` | Limit concurrent downloads |

## Alternative: Use Render Paid Tier

Render's paid tier ($7/month) provides:
- More reliable builds
- More RAM for FFmpeg operations
- Always-on service (no cold starts)
- Better performance

## Alternative: Deploy Backend Elsewhere

If FFmpeg continues to be problematic on Render, consider:

1. **Railway** - Similar to Render, better FFmpeg support
2. **Fly.io** - Dockerfile-based, full control
3. **DigitalOcean App Platform** - Managed platform
4. **VPS** (DigitalOcean, Linode, etc.) - Full control

## Docker Alternative

For maximum control, use Docker deployment:

```dockerfile
FROM python:3.11-slim

# Install FFmpeg
RUN apt-get update && \
    apt-get install -y ffmpeg && \
    rm -rf /var/lib/apt/lists/*

# Copy and install app
WORKDIR /app
COPY backend/requirements.txt .
RUN pip install -r requirements.txt
COPY backend/ .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

Deploy this to any Docker-compatible platform.

## Support

If you continue to have issues:
1. Check Render's status page: https://status.render.com/
2. Review Render docs: https://render.com/docs
3. Open an issue in the project repository
4. Contact Render support (paid tier only)

## Summary

✅ Default configuration installs FFmpeg automatically
✅ Works on free tier
✅ No additional configuration needed
✅ Alternative methods available if needed
✅ Can verify installation via logs
