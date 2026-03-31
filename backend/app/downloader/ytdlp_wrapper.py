from __future__ import annotations

import asyncio
import logging
import tempfile
from pathlib import Path
from typing import Any, Callable, Optional

import yt_dlp

from app.core.config import settings
from app.downloader.sources import ExtractResult, FormatInfo, ProgressInfo, VideoSource

logger = logging.getLogger(__name__)


def _format_from_info(f: dict) -> FormatInfo:
    return FormatInfo(
        format_id=f.get("format_id") or "",
        ext=f.get("ext"),
        resolution=f.get("resolution") or (f"{f.get('height')}p" if f.get("height") else None),
        filesize=f.get("filesize"),
        vcodec=f.get("vcodec"),
        acodec=f.get("acodec"),
    )


class YtDlpSource(VideoSource):
    def __init__(self, proxy: Optional[str] = None, cookies_path: Optional[str] = None):
        self._proxy = proxy or settings.PROXY
        self._cookies_path = cookies_path or settings.COOKIES_PATH

    def _base_opts(self) -> dict:
        opts: dict[str, Any] = {"quiet": True, "no_warnings": True}
        if self._proxy:
            opts["proxy"] = self._proxy
        if self._cookies_path:
            opts["cookiefile"] = self._cookies_path
        if settings.FFMPEG_PATH:
            opts["ffmpeg_location"] = settings.FFMPEG_PATH
        return opts

    async def extract(self, url: str, cookies: Optional[str] = None) -> ExtractResult:
        logger.info("[DEBUG] ytdlp extract url=%s", url)
        opts = {**self._base_opts(), "extract_flat": False, "skip_download": True}
        if cookies:
            # Per-request cookies override server COOKIES_PATH for this request
            with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False, encoding="utf-8") as f:
                f.write(cookies)
                opts["cookiefile"] = f.name
            try:
                return await self._extract_with_opts(url, opts)
            finally:
                Path(opts["cookiefile"]).unlink(missing_ok=True)
        return await self._extract_with_opts(url, opts)

    async def _extract_with_opts(self, url: str, opts: dict) -> ExtractResult:
        def _run():
            with yt_dlp.YoutubeDL(opts) as ydl:
                info = ydl.extract_info(url, download=False)
                if info is None:
                    raise ValueError("Could not extract info for URL")
                return info

        loop = asyncio.get_running_loop()
        try:
            info = await loop.run_in_executor(None, _run)
        except Exception as e:
            logger.exception("[DEBUG] ytdlp extract_info failed url=%s: %s", url, e)
            raise
        info_keys = list(info.keys()) if isinstance(info, dict) else []
        raw_formats = info.get("formats") or []
        formats = [_format_from_info(f) for f in raw_formats]
        logger.info("[DEBUG] ytdlp extract info keys=%s title=%r formats_count=%s", info_keys[:15], info.get("title"), len(formats))
        playlist = info.get("entries") if info.get("_type") == "playlist" else None
        playlist_entries = []
        if playlist:
            for e in playlist:
                playlist_entries.append({
                    "id": e.get("id") if isinstance(e, dict) else None,
                    "title": e.get("title") if isinstance(e, dict) else None,
                    "url": (e.get("url") or url) if isinstance(e, dict) else url,
                })
        logger.debug("[DEBUG] ytdlp extract playlist_entries=%s", len(playlist_entries))
        return ExtractResult(
            title=info.get("title") or "Unknown",
            thumbnail=info.get("thumbnail"),
            duration=info.get("duration"),
            formats=formats,
            playlist_entries=playlist_entries,
        )

    async def download(
        self,
        url: str,
        output_path: str,
        format_id: Optional[str] = None,
        progress_callback: Optional[Callable[[ProgressInfo], None]] = None,
        cookies: Optional[str] = None,
    ) -> str:
        out_tmpl = str(Path(output_path) / "%(title).200s.%(ext)s")
        opts: dict[str, Any] = {**self._base_opts(), "outtmpl": out_tmpl}
        if format_id:
            opts["format"] = format_id
        if cookies:
            with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False, encoding="utf-8") as f:
                f.write(cookies)
                opts["cookiefile"] = f.name
            try:
                return await self._download_with_opts(url, opts, progress_callback)
            finally:
                Path(opts["cookiefile"]).unlink(missing_ok=True)
        return await self._download_with_opts(url, opts, progress_callback)

    async def _download_with_opts(
        self,
        url: str,
        opts: dict,
        progress_callback: Optional[Callable[[ProgressInfo], None]] = None,
    ) -> str:
        # Capture actual path written by yt-dlp when status is "finished" (key "filename")
        final_path: list[Optional[str]] = [None]
        if progress_callback:
            last_percent: list[float] = [0.0]

            def _progress(d: dict):
                if d.get("status") == "downloading":
                    percent = None
                    raw = d.get("percent")
                    if raw is not None and isinstance(raw, (int, float)) and 0 <= raw <= 100:
                        percent = float(raw)
                    if percent is None:
                        total = d.get("total_bytes")
                        downloaded = d.get("downloaded_bytes")
                        if total is not None and downloaded is not None and total > 0:
                            percent = min(100.0, (float(downloaded) / float(total)) * 100.0)
                    if percent is None:
                        percent = last_percent[0]
                    else:
                        last_percent[0] = percent
                    progress_callback(ProgressInfo(percent, d.get("speed"), d.get("eta"), "downloading"))
                elif d.get("status") == "finished":
                    if d.get("filename"):
                        final_path[0] = d["filename"]
                    progress_callback(ProgressInfo(100.0, None, None, "finished"))
            opts["progress_hooks"] = [_progress]
        else:
            def _progress(d: dict):
                if d.get("status") == "finished" and d.get("filename"):
                    final_path[0] = d["filename"]
            opts["progress_hooks"] = [_progress]

        def _run():
            with yt_dlp.YoutubeDL(opts) as ydl:
                info = ydl.extract_info(url, download=True)
                if info is None:
                    raise ValueError("Download failed")
                # When merging video+audio, progress hook gets "finished" for each temp file (then deleted).
                # The real file is in requested_downloads[0]["filepath"]. Always prefer that over hook.
                req = (info.get("requested_downloads") or [{}])[0]
                path_from_info = req.get("filepath") or (ydl.prepare_filename(info) if info else None)
                if path_from_info:
                    path_from_info = str(Path(path_from_info).resolve())
                    if Path(path_from_info).exists():
                        return path_from_info
                if final_path[0]:
                    hook_path = str(Path(final_path[0]).resolve())
                    if Path(hook_path).exists():
                        return hook_path
                if path_from_info:
                    return path_from_info
                raise ValueError("Download completed but output file path could not be determined")

        logger.info("[DEBUG] ytdlp download url=%s outtmpl=%s format=%s", url, opts.get("outtmpl"), opts.get("format"))
        loop = asyncio.get_running_loop()
        try:
            result = await loop.run_in_executor(None, _run)
            logger.info("[DEBUG] ytdlp download done filepath=%s", result)
            return result
        except Exception as e:
            logger.exception("[DEBUG] ytdlp download failed url=%s: %s", url, e)
            raise
