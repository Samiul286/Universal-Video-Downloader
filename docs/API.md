# REST API and WebSocket overview

Short reference for the **yt-dlp REST API** and live progress provided by the Universal Video Downloader backend. Use this to integrate the **video downloader from URL** into scripts or other apps.

For interactive API docs (Swagger), run the backend and open **http://localhost:8000/docs**. See the main [README](../README.md) for how to run the app.

---

## Table of contents

- [Extract video info (POST /api/extract)](#extract-video-info-post-apiextract)
- [Download (POST /api/download)](#download-post-apidownload)
- [List jobs (GET /api/downloads)](#list-jobs-get-apidownloads)
- [Live progress (WebSocket)](#live-progress-websocket)
- [Other endpoints](#other-endpoints)

---

## Extract video info (POST /api/extract)

Get title, thumbnail, duration, and available formats for a video or playlist **without downloading**. Use this to let users pick quality before starting a download.

**Request:**

```http
POST /api/extract
Content-Type: application/json

{"url": "https://www.youtube.com/watch?v=..."}
```

**Response:** JSON with `title`, `thumbnail`, `duration`, `formats` (array of `format_id`, `ext`, `resolution`, etc.), and optionally `playlist_entries` for playlists.

**Example (curl):**

```bash
curl -X POST http://localhost:8000/api/extract -H "Content-Type: application/json" -d '{"url":"https://www.youtube.com/watch?v=VIDEO_ID"}'
```

---

## Download (POST /api/download)

Start a download job. The backend queues the job and returns a `job_id`. Progress is reported via [GET /api/downloads](#list-jobs-get-apidownloads) or the [WebSocket](#live-progress-websocket).

**Request:**

```http
POST /api/download
Content-Type: application/json

{
  "url": "https://www.youtube.com/watch?v=...",
  "format_id": "optional; omit for best",
  "download_path": "optional; overrides default save folder",
  "output_template": "optional; yt-dlp output template"
}
```

**Response:** `{"job_id": "uuid"}`.

**Example (curl):**

```bash
curl -X POST http://localhost:8000/api/download -H "Content-Type: application/json" -d '{"url":"https://www.youtube.com/watch?v=VIDEO_ID"}'
```

---

## List jobs (GET /api/downloads)

Get all download jobs with status and progress.

**Request:**

```http
GET /api/downloads
```

**Response:** JSON array of jobs. Each has `id`, `url`, `status` (e.g. `queued`, `downloading`, `completed`, `failed`), `progress` (percentage, speed, ETA when downloading), `reason` (error message when failed), and related fields.

---

## Live progress (WebSocket)

Connect to receive real-time progress for all jobs.

**URL:** `ws://localhost:8000/ws/progress`

**Messages:** The server pushes progress events (e.g. job id, percentage, speed, ETA). Connect from the frontend or a script to show live updates without polling [GET /api/downloads](#list-jobs-get-apidownloads).

---

## Other endpoints

- **Pause / resume / cancel / retry** — Use the routes under `/api/downloads` (e.g. POST to pause or resume a job by ID). See **http://localhost:8000/docs** for the full list.
- **Settings** — GET/PUT for download path, max concurrent, etc., under `/api/settings`.
- **Health** — `GET /health` for liveness.

For the complete **FastAPI video downloader** API, run the backend and open **http://localhost:8000/docs** (Swagger UI). See the main [README](../README.md) and [INSTALL.md](INSTALL.md) for setup.
