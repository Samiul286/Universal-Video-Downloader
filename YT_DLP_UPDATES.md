# yt-dlp Updates and Maintenance

yt-dlp is the core engine that downloads videos from 1000+ sites. Video sites frequently change their APIs, so keeping yt-dlp updated is crucial.

## Current Configuration

### requirements.txt
```
yt-dlp>=2024.11.0
```

This installs yt-dlp version 2024.11.0 or newer.

## Why Updates Matter

Video sites (YouTube, TikTok, etc.) regularly change their APIs to prevent downloading. yt-dlp is updated frequently (often weekly) to fix these issues.

**Symptoms of outdated yt-dlp:**
- "Unable to extract video data"
- "HTTP Error 403: Forbidden"
- "Video unavailable"
- Downloads that worked before suddenly fail

## Update Strategies

### Strategy 1: Always Latest (Recommended for Production)

Update `requirements.txt` to always install the latest version:

```txt
yt-dlp
```

**Pros:**
- Always up-to-date with site changes
- Automatic fixes for broken extractors
- New site support

**Cons:**
- Potential breaking changes (rare)
- Slightly longer build times

### Strategy 2: Minimum Version (Current)

```txt
yt-dlp>=2024.11.0
```

**Pros:**
- Predictable behavior
- Controlled updates

**Cons:**
- May become outdated
- Requires manual version bumps

### Strategy 3: Pinned Version (Most Stable)

```txt
yt-dlp==2024.11.0
```

**Pros:**
- Completely predictable
- No surprises

**Cons:**
- Will become outdated quickly
- Requires frequent manual updates

## Recommended: Always Latest

For production deployment, I recommend using the latest version:

<function_calls>
<invoke name="strReplace">
<parameter name="newStr">fastapi>=0.115.0,<0.116
uvicorn[standard]>=0.32.0,<0.33
pydantic>=2.0,<3
pydantic-settings>=2.0
yt-dlp  # Always use latest version for best site compatibility
aiosqlite>=0.20.0
pytest>=8.0
pytest-asyncio
httpx
ruff