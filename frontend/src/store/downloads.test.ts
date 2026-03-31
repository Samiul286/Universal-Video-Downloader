/**
 * FE-U1: Store (Zustand) — download list: add job, update progress, update status; selectors return correct slice.
 */
import { describe, it, expect, beforeEach, vi } from 'vitest'
import { useDownloadsStore } from './downloads'

// Mock api so we don't hit network
vi.mock('../services/api', () => ({
  extract: vi.fn(),
  startDownload: vi.fn(),
  listDownloads: vi.fn().mockResolvedValue([]),
  cancelDownload: vi.fn().mockResolvedValue(undefined),
  pauseDownload: vi.fn().mockResolvedValue(undefined),
  resumeDownload: vi.fn().mockResolvedValue(undefined),
  retryDownload: vi.fn().mockResolvedValue(undefined),
  isNoValidDownloadPathError: vi.fn().mockReturnValue(false),
}))

describe('useDownloadsStore', () => {
  beforeEach(() => {
    useDownloadsStore.setState({
      url: '',
      extractResult: null,
      selectedFormatId: null,
      jobs: [],
      loading: false,
      error: null,
    })
  })

  it('setUrl updates url', () => {
    useDownloadsStore.getState().setUrl('https://example.com/v')
    expect(useDownloadsStore.getState().url).toBe('https://example.com/v')
  })

  it('setSelectedFormat updates selectedFormatId', () => {
    useDownloadsStore.getState().setSelectedFormat('22')
    expect(useDownloadsStore.getState().selectedFormatId).toBe('22')
    useDownloadsStore.getState().setSelectedFormat(null)
    expect(useDownloadsStore.getState().selectedFormatId).toBeNull()
  })

  it('jobs slice is updated by refreshJobs', async () => {
    const { listDownloads } = await import('../services/api')
    vi.mocked(listDownloads).mockResolvedValueOnce([
      {
        id: 'j1',
        url: 'https://a.com',
        status: 'completed',
        progress: 100,
        created_at: '',
        updated_at: '',
      },
    ])
    await useDownloadsStore.getState().refreshJobs()
    expect(useDownloadsStore.getState().jobs).toHaveLength(1)
    expect(useDownloadsStore.getState().jobs[0].id).toBe('j1')
    expect(useDownloadsStore.getState().jobs[0].status).toBe('completed')
    expect(useDownloadsStore.getState().jobs[0].progress).toBe(100)
  })

  it('clearError sets error to null', () => {
    useDownloadsStore.setState({ error: 'Something failed' })
    useDownloadsStore.getState().clearError()
    expect(useDownloadsStore.getState().error).toBeNull()
  })
})
