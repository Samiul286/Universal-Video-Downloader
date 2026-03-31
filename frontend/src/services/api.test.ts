/**
 * FE-U2: API client — extract and download use correct URL and payload; errors mapped to user-facing.
 * We test the error helper (pure) and rely on store tests + E2E for full URL/payload coverage.
 */
import { describe, it, expect } from 'vitest'
import { isNoValidDownloadPathError } from './api'

describe('isNoValidDownloadPathError', () => {
  it('returns true for axios error 503 with detail no_valid_download_path', () => {
    const err = Object.assign(new Error('req'), {
      isAxiosError: true,
      response: { status: 503, data: { detail: 'no_valid_download_path' } },
    }) as Parameters<typeof isNoValidDownloadPathError>[0]
    expect(isNoValidDownloadPathError(err)).toBe(true)
  })

  it('returns false for 404', () => {
    const err = Object.assign(new Error('req'), {
      isAxiosError: true,
      response: { status: 404, data: {} },
    }) as Parameters<typeof isNoValidDownloadPathError>[0]
    expect(isNoValidDownloadPathError(err)).toBe(false)
  })

  it('returns false for non-axios error', () => {
    expect(isNoValidDownloadPathError(new Error('network'))).toBe(false)
  })
})
