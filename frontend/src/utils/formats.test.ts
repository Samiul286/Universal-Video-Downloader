/**
 * FE-U4: Format helpers — parse formats list; pick best video+audio or selected format_id.
 */
import { describe, it, expect } from 'vitest'
import { pickBestFormatId, getFormatLabel } from './formats'
import type { FormatItem } from '../services/api'

describe('pickBestFormatId', () => {
  it('returns null for empty formats', () => {
    expect(pickBestFormatId([])).toBeNull()
  })

  it('returns first format_id when no resolution', () => {
    const formats: FormatItem[] = [
      { format_id: 'a', ext: 'mp4' },
      { format_id: 'b', ext: 'webm' },
    ]
    expect(pickBestFormatId(formats)).toBe('a')
  })

  it('prefers higher resolution', () => {
    const formats: FormatItem[] = [
      { format_id: 'lo', resolution: '360p', vcodec: 'avc' },
      { format_id: 'hi', resolution: '720p', vcodec: 'avc' },
    ]
    expect(pickBestFormatId(formats)).toBe('hi')
  })

  it('returns single format when one element', () => {
    const formats: FormatItem[] = [{ format_id: '22', resolution: '720p', ext: 'mp4' }]
    expect(pickBestFormatId(formats)).toBe('22')
  })
})

describe('getFormatLabel', () => {
  it('joins resolution and ext', () => {
    expect(getFormatLabel({ format_id: '22', resolution: '720p', ext: 'mp4' })).toBe('720p mp4')
  })

  it('includes filesize in MB when present', () => {
    expect(
      getFormatLabel({ format_id: '22', resolution: '720p', ext: 'mp4', filesize: 5 * 1024 * 1024 })
    ).toBe('720p mp4 (5 MB)')
  })
})
