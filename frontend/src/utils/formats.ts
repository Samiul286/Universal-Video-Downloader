import type { FormatItem } from '../services/api'

/**
 * Pick best video+audio format (single format id) or null for "best".
 * Prefers formats with resolution, then by filesize.
 */
export function pickBestFormatId(formats: FormatItem[]): string | null {
  if (!formats.length) return null
  const withVideo = formats.filter((f) => f.resolution || f.vcodec)
  if (!withVideo.length) return formats[0]?.format_id ?? null
  const sorted = [...withVideo].sort((a, b) => {
    const resA = parseResolution(a.resolution)
    const resB = parseResolution(b.resolution)
    if (resA !== resB) return resB - resA
    return (b.filesize ?? 0) - (a.filesize ?? 0)
  })
  return sorted[0]?.format_id ?? null
}

function parseResolution(r?: string): number {
  if (!r) return 0
  const match = r.match(/(\d+)p/)
  return match ? parseInt(match[1], 10) : 0
}

/** Human-readable label for format (resolution, ext, size). */
export function getFormatLabel(f: FormatItem): string {
  const parts = [f.resolution ?? f.format_id, f.ext].filter(Boolean)
  if (f.filesize) parts.push(`(${Math.round(f.filesize / 1024 / 1024)} MB)`)
  return parts.join(' ')
}
