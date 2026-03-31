import logging

from fastapi import APIRouter, HTTPException

from app.downloader.sources import FormatInfo
from app.downloader.ytdlp_wrapper import YtDlpSource
from app.schemas.extract import ExtractRequest, ExtractResponse, FormatItem, PlaylistEntry

logger = logging.getLogger(__name__)
router = APIRouter()
_source = YtDlpSource()


def _format_item(f: FormatInfo) -> FormatItem:
    return FormatItem(
        format_id=f.format_id,
        ext=f.ext,
        resolution=f.resolution,
        filesize=f.filesize,
        vcodec=f.vcodec,
        acodec=f.acodec,
    )


@router.post("/extract", response_model=ExtractResponse)
async def extract(req: ExtractRequest):
    url = str(req.url)
    logger.info("[DEBUG] POST /api/extract request url=%s", url)
    try:
        result = await _source.extract(url, cookies=req.cookies)
        n_formats = len(result.formats)
        n_playlist = len(result.playlist_entries)
        logger.info(
            "[DEBUG] POST /api/extract success title=%r formats=%s playlist_entries=%s",
            result.title, n_formats, n_playlist,
        )
        response = ExtractResponse(
            title=result.title,
            thumbnail=result.thumbnail,
            duration=result.duration,
            formats=[_format_item(f) for f in result.formats],
            playlist_entries=[PlaylistEntry(id=e.get("id"), title=e.get("title"), url=e.get("url", url)) for e in result.playlist_entries],
        )
        logger.debug("[DEBUG] POST /api/extract response title=%s format_ids=%s", response.title, [f.format_id for f in response.formats[:5]])
        return response
    except Exception as e:
        logger.exception("[DEBUG] POST /api/extract failed url=%s error=%s", url, e)
        raise HTTPException(status_code=422, detail=str(e))
