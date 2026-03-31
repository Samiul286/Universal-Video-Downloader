# How to install Universal Video Downloader (Windows, Linux, macOS)

Step-by-step guide to install and run the **self-hosted video downloader** (yt-dlp web interface) on your machine. You will download video by link from YouTube, Vimeo, TikTok, and 1000+ sites using a local FastAPI + React app.

See the main [README](../README.md) for an overview and [CONTRIBUTING.md](../CONTRIBUTING.md) for development workflow.

---

## Table of contents

- [Prerequisites for self-hosted video downloader](#prerequisites-for-self-hosted-video-downloader)
- [Step 1: Clone or download the repo](#step-1-clone-or-download-the-repo)
- [Step 2: Backend (FastAPI, Python)](#step-2-backend-fastapi-python)
- [Step 3: Frontend (React, Node)](#step-3-frontend-react-node)
- [Step 4: Run and open the app](#step-4-run-and-open-the-app)
- [Optional: environment variables](#optional-environment-variables)
- [Troubleshooting](#troubleshooting)

---

## Prerequisites for self-hosted video downloader

Before installing, ensure you have:

| Requirement | Version | Notes |
|-------------|---------|--------|
| **Python** | 3.11+ | Used for the FastAPI backend and yt-dlp. |
| **Node.js** | 18+ | Used for the React frontend. |
| **FFmpeg** | Any recent | Required for merging video+audio when you pick formats that download separately. Must be on PATH or set `FFMPEG_PATH` in `.env`. |
| **Git** | Any | Optional; only needed if you clone the repo. |

- **Windows:** Install Python from [python.org](https://www.python.org/downloads/), Node from [nodejs.org](https://nodejs.org/). FFmpeg: `winget install FFmpeg` or set `FFMPEG_PATH` in `.env`.
- **macOS:** `brew install python node ffmpeg` (or use official Python/Node installers).
- **Linux:** Use your package manager (e.g. `apt install python3 python3-venv nodejs ffmpeg`).

---

## Step 1: Clone or download the repo

Get the **open source video downloader** source code:

```bash
git clone https://github.com/YOUR_USERNAME/universal-video-downloader.git
cd universal-video-downloader
```

Or download and extract the ZIP from GitHub, then open a terminal in the project folder.

---

## Step 2: Backend (FastAPI, Python)

The backend is the **FastAPI video downloader** server that runs yt-dlp and serves the REST API and WebSocket.

### Linux / macOS

```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Windows (PowerShell)

```powershell
cd backend
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

If script execution is disabled, run without activating the venv:

```powershell
.\venv\Scripts\python.exe -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Leave this terminal open. The API will be at **http://localhost:8000** and Swagger at **http://localhost:8000/docs**.

---

## Step 3: Frontend (React, Node)

The **React video downloader app** is the web UI. Run it in a **second terminal**.

### Linux / macOS

```bash
cd frontend
npm install
npm run dev
```

### Windows (PowerShell)

```powershell
cd frontend
npm install
npm run dev
```

Leave this terminal open. The app will be at **http://localhost:5173**.

---

## Step 4: Run and open the app

1. With both backend and frontend running, open a browser to **http://localhost:5173**.
2. Paste a video URL (e.g. YouTube, Vimeo, TikTok), click **Extract**, choose quality, then **Download**.
3. Files are saved to your chosen folder (or system Downloads). See the main [README – Demo usage](../README.md#demo-usage) for details.

You now have a **self-hosted video downloader** and **yt-dlp web interface** running locally. No cloud, no account.

---

## Optional: environment variables

Copy `backend/.env.example` to `backend/.env` and edit if needed. Common options:

| Variable | Description |
|----------|-------------|
| `DOWNLOAD_PATH` | Default save folder for downloads. If unset, the app uses system Downloads or asks once. |
| `FFMPEG_PATH` | Path to FFmpeg binary if not on PATH. |
| `COOKIES_PATH` | Path to a cookies file for age-restricted or private content. |
| `MAX_CONCURRENT` | Max concurrent downloads (default 2). |

See the main [README – Environment variables](../README.md#environment-variables) for the full list.

---

## Troubleshooting

- **Backend won’t start:** Ensure Python 3.11+ and that `pip install -r requirements.txt` finished without errors. On Windows, try `.\venv\Scripts\python.exe -m uvicorn main:app --reload --host 0.0.0.0 --port 8000`.
- **Frontend won’t start:** Ensure Node 18+ and run `npm install` in the `frontend` folder.
- **Downloads fail or no video+audio:** Install FFmpeg and ensure it’s on PATH (or set `FFMPEG_PATH` in `.env`).
- **Age-restricted or private content:** Set `COOKIES_PATH` in `.env` to a cookies file exported from your browser (e.g. with a browser extension).

For more help, see the main [README](../README.md) and [CONTRIBUTING.md](../CONTRIBUTING.md).
