# Universal Video Downloader

**Open source video downloader and yt-dlp web interface.** Paste a video URL → pick quality → download. YouTube, Vimeo, TikTok, and 1000+ sites. FastAPI + React, self-hosted, no cloud.

---

## Table of contents

- [Tagline](#tagline)
- [Description](#description)
- [Key features](#key-features)
- [Supported sites: YouTube, Vimeo, TikTok and 1000+ (yt-dlp)](#supported-sites-youtube-vimeo-tiktok-and-1000-yt-dlp)
- [Quick start: run the video downloader locally](#quick-start-run-the-video-downloader-locally)
- [Copy-paste: run in 3 steps](#copy-paste-run-in-3-steps)
- [Demo usage](#demo-usage)
- [Installation: self-hosted video downloader (Python, Node, FFmpeg)](#installation-self-hosted-video-downloader-python-node-ffmpeg)
- [Deployment](#deployment)
- [Project structure](#project-structure)
- [Key concepts](#key-concepts)
- [Running tests](#running-tests)
- [API docs](#api-docs)
- [Windows](#windows)
- [yt-dlp updates](#yt-dlp-updates)
- [Contributing](#contributing)
- [License](#license)

---

## Tagline

*Paste a video URL → pick quality → download. Universal support for YouTube, Vimeo, TikTok and 1000+ sites. Self-hosted, no cloud.*

---

## Description

Universal Video Downloader is an **open source video downloader** and **yt-dlp web interface**: a local-first web app you run on your PC or LAN. Paste any supported video URL, **Extract** to get title and format list, choose quality, then **Download**. Files are saved to a folder you choose (or system Downloads). No account, no cloud — download video by link from 1000+ sites. Built with **FastAPI** (Python) and **React** (TypeScript, Vite). Ideal for self-hosted video downloads, batch and playlist jobs, and developers who want a yt-dlp-based REST API with a ready-made UI.

---

## Key features

- **Paste URL → Extract → Choose format → Download** — Get video info (title, thumbnail, formats) without downloading; then pick quality and start the download.
- **Save location:** Default is system Downloads if it exists. If not set, the app asks **"Where do you want to save this video?"** once; that folder is used for all future downloads.
- **Queue and worker pool** — Configurable max concurrent downloads; jobs are queued and processed in order.
- **WebSocket live progress** — Percentage, speed, and ETA per job in the UI.
- **Pause, resume, cancel, retry** — Full control over queued and active downloads.
- **Playlist support** — Extract playlist metadata; add multiple jobs from a playlist.
- **SQLite persistence** — Job history and settings (download path, max concurrent, etc.) stored locally.
- **Settings** — Download folder, max concurrent, optional cookies file and proxy (for age-restricted or geo-blocked content).
- **API docs** — Swagger UI at `/docs` when the backend is running. No authentication (for trusted local/LAN use only).

---

## Supported sites: YouTube, Vimeo, TikTok and 1000+ (yt-dlp)

**Single video and playlist URLs** from:

- **YouTube** (videos, playlists, Shorts)
- **Vimeo, TikTok, Twitter/X, Instagram, Facebook, Dailymotion**
- **1000+ other sites** supported by [yt-dlp](https://github.com/yt-dlp/yt-dlp/blob/master/supportedsites.md)

Age-restricted or private content may require **cookies**. You can either set `COOKIES_PATH` in `.env` (server-wide) or use **per-user cookies** in the app: open "Use my cookies (optional)", paste Netscape-format cookies (e.g. exported from a browser extension), then Extract/Download—your cookies are sent with the request only and are not stored on the server. **FFmpeg** (on PATH or set `FFMPEG_PATH`) is needed for merging video+audio when you choose formats that download separately.

---

## Quick start: run the video downloader locally

Run the yt-dlp web interface (FastAPI + React) on your machine:

1. **Backend**
   ```bash
   cd backend
   python -m venv venv
   pip install -r requirements.txt
   cp .env.example .env   # optional: edit .env
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```
   **Windows (PowerShell)** — If script execution is disabled, run without activating venv:
   ```powershell
   .\venv\Scripts\python.exe -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```

2. **Frontend**
   ```bash
   cd frontend
   npm install
   npm run dev
   ```

3. Open **http://localhost:5173**. API: **http://localhost:8000**. Swagger: **http://localhost:8000/docs**.

For a full step-by-step install guide (Windows, Linux, macOS), see **[docs/INSTALL.md](docs/INSTALL.md)**.

---

## Copy-paste: run in 3 steps

**Linux / macOS (from repo root):**

```bash
cd backend && python -m venv venv && . venv/bin/activate && pip install -r requirements.txt && uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

In a second terminal:

```bash
cd frontend && npm install && npm run dev
```

Then open **http://localhost:5173**.

**Windows (PowerShell, from repo root):**

```powershell
cd backend; .\venv\Scripts\python.exe -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

In a second terminal:

```powershell
cd frontend; npm install; npm run dev
```

Then open **http://localhost:5173**.

---

## Demo usage

How the app works end-to-end:

1. **Paste URL** — Enter a video link (e.g. `https://www.youtube.com/watch?v=...` or `https://vimeo.com/...`) in the **Video URL** field.
2. **Extract** — Click **Extract**. The app fetches title, thumbnail, and available formats (no download yet).
3. **Select format** — Choose quality from the dropdown (e.g. "Best" or a specific resolution). Optionally pick a different save folder when prompted.
4. **Download** — Click **Download**. The job is queued; progress (%, speed, ETA) appears in the download list.
5. **Completed** — When status is **completed**, use **Copy path** to open the file location. Failed jobs show a **Reason** (error message) for debugging.

**API flow (for scripts or integration):** see [API docs](#api-docs) and **[docs/API.md](docs/API.md)** for the REST and WebSocket overview.

- `POST /api/extract` with `{ "url": "https://..." }` → returns title, thumbnail, `formats[]`, `playlist_entries[]`.
- `POST /api/download` with `{ "url": "...", "format_id": "optional", "download_path": "optional" }` → returns `job_id`.
- `GET /api/downloads` → list jobs with status and progress.
- WebSocket `ws://localhost:8000/ws/progress` → live progress events per job.

---

## Installation: self-hosted video downloader (Python, Node, FFmpeg)

Full step-by-step instructions for Windows, Linux, and macOS: **[docs/INSTALL.md](docs/INSTALL.md)**.

### Prerequisites

- **Python 3.11+**
- **Node 18+**
- **FFmpeg** (on PATH or set `FFMPEG_PATH` in `.env`)

### Environment variables

Copy `backend/.env.example` to `backend/.env` and adjust if needed.

| Variable         | Description |
|------------------|-------------|
| `PORT`           | Backend port (default 8000). |
| `BIND`           | Bind address (default 0.0.0.0). |
| `DOWNLOAD_PATH`  | Optional. If set and the folder exists, used as default save folder. Otherwise app uses system Downloads or asks at first download. |
| `DB_PATH`        | SQLite database path (default `./storage/downloader.db`). |
| `MAX_CONCURRENT` | Max concurrent downloads (default 2). |
| `QUEUE_MAX_SIZE` | Max queue size (default 100). |
| `FFMPEG_PATH`    | Optional path to FFmpeg binary. |
| `PROXY`          | Optional proxy URL. |
| `COOKIES_PATH`   | Optional path to cookies file for age-restricted/private content. |

---

## Deployment

Deploy to production with Vercel (frontend) and Render (backend):

- **Start Here**: [DEPLOYMENT_INDEX.md](DEPLOYMENT_INDEX.md) - Complete documentation index
- **Quick Start**: [QUICK_DEPLOY.md](QUICK_DEPLOY.md) - Deploy in 10 minutes
- **Checklist**: [DEPLOYMENT_CHECKLIST.md](DEPLOYMENT_CHECKLIST.md) - Step-by-step guide
- **Full Guide**: [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md) - Detailed instructions with troubleshooting

Configuration files included:
- `render.yaml` - Render deployment config (FFmpeg + yt-dlp auto-installed)
- `vercel.json` - Vercel deployment config

**Features:**
- ✅ FFmpeg automatically installed (works on free tier)
- ✅ yt-dlp always uses latest version
- ✅ Persistent storage for database
- ✅ WebSocket support for progress updates
- ✅ CORS properly configured

---

## Project structure

See [Quick start: run the video downloader locally](#quick-start-run-the-video-downloader-locally) for run commands.

```
universal-video-downloader/
├── backend/
│   ├── main.py                 # FastAPI app; routes, WebSocket, CORS
│   ├── requirements.txt
│   ├── .env.example
│   └── app/
│       ├── core/               # config, logging
│       ├── database/           # SQLite session, repositories (downloads, settings)
│       ├── schemas/            # Pydantic request/response (extract, download, settings)
│       ├── downloader/          # ytdlp_wrapper, queue, manager (workers)
│       └── api/
│           ├── routes/         # extract, download, downloads list, pause/resume/cancel/retry, settings
│           └── websocket/      # /ws/progress
├── frontend/
│   ├── src/
│   │   ├── App.tsx             # Main UI: URL input, Extract, format picker, download list
│   │   ├── store/              # Zustand: downloads, progress, debug log
│   │   ├── services/           # API client (axios)
│   │   └── components/         # ChooseFolderModal, etc.
│   ├── package.json
│   └── vite.config.ts
├── docs/                       # INSTALL.md, API.md
├── README.md
├── CONTRIBUTING.md
└── GITHUB_SETUP.md             # Repo description, topics, tagline, keywords (copy-paste)
```

| Path | Purpose |
|------|---------|
| `backend/main.py` | FastAPI app entry; mounts routes, WebSocket, CORS. |
| `backend/app/core/config.py` | Env (PORT, DOWNLOAD_PATH, DB_PATH, etc.); effective download path. |
| `backend/app/database/` | SQLite connection; `downloads` and `settings` tables. |
| `backend/app/downloader/ytdlp_wrapper.py` | yt-dlp: extract metadata, run download with progress hook. |
| `backend/app/downloader/manager.py` | Queue + workers; pause/resume/cancel/retry. |
| `backend/app/api/routes/` | REST: extract, download, downloads list, settings. |
| `backend/app/api/websocket/` | WebSocket `/ws/progress` for live progress. |
| `frontend/src/store/` | Zustand: download list, progress; API actions. |
| `frontend/src/services/` | Axios API client. |
| `frontend/src/components/` | Choose folder modal, etc. |

See also [frontend/README.md](frontend/README.md) for the React app and [GITHUB_SETUP.md](GITHUB_SETUP.md) for repo description and topics.

---

## Key concepts

- **Extract** — Get video info (title, formats) without downloading.
- **Format** — Quality option (e.g. 1080p, best).
- **Job** — One download task (queued → downloading → completed/failed).
- **Queue** — List of jobs waiting or running.
- **WebSocket** — Live updates (progress %, speed, ETA).
- **yt-dlp** — Engine that fetches video from 1000+ sites.
- **Effective download path** — Where files are saved (system Downloads or user-chosen folder).

---

## Running tests

- **Backend:** From repo root with backend venv activated: `pytest backend/tests -v`
- **Frontend:** In `frontend`: `npm run test`
- **E2E:** In `frontend`: `npm run e2e` (Playwright)

---

## API docs

When the backend is running: **http://localhost:8000/docs** (Swagger/OpenAPI).

For a short REST and WebSocket overview, see **[docs/API.md](docs/API.md)**.

---

## Windows

- Use **PowerShell** for commands.
- Activate venv: `.\venv\Scripts\Activate.ps1` from `backend`. Or run without activating: `.\venv\Scripts\python.exe -m uvicorn main:app --reload --host 0.0.0.0 --port 8000`
- FFmpeg: `winget install FFmpeg` or set `FFMPEG_PATH` in `.env`.

---

## yt-dlp updates

yt-dlp is updated frequently for site support. The deployment is configured to always use the latest version.

**For production:** Redeploy monthly or when downloads fail to get the latest yt-dlp version. See [YTDLP_UPDATES.md](YTDLP_UPDATES.md) for details.

**For local development:** Upgrade with `pip install -U yt-dlp`

---

## Contributing

See **[CONTRIBUTING.md](CONTRIBUTING.md)** for setup, lint, tests, and PR workflow. New contributors: start with the README and [project structure](#project-structure), then run the app and explore **http://localhost:8000/docs**.

---

## License

MIT
