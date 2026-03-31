/**
 * FE-C1: URL input and Extract button; FE-C2: Format selection and Download; FE-C3: Download list.
 */
import { describe, it, expect, beforeEach, vi } from 'vitest'
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import App from './App'
import { useDownloadsStore } from './store/downloads'

vi.mock('./services/api', () => ({
  extract: vi.fn(),
  startDownload: vi.fn(),
  listDownloads: vi.fn().mockResolvedValue([]),
  cancelDownload: vi.fn().mockResolvedValue(undefined),
  pauseDownload: vi.fn().mockResolvedValue(undefined),
  resumeDownload: vi.fn().mockResolvedValue(undefined),
  retryDownload: vi.fn().mockResolvedValue(undefined),
  getSettings: vi.fn().mockResolvedValue({ settings: {} }),
  putSettings: vi.fn().mockResolvedValue({ settings: {} }),
  isNoValidDownloadPathError: vi.fn().mockReturnValue(false),
}))

describe('App', () => {
  beforeEach(async () => {
    useDownloadsStore.setState({
      url: '',
      extractResult: null,
      selectedFormatId: null,
      jobs: [],
      loading: false,
      error: null,
    })
    const { listDownloads } = await import('./services/api')
    vi.mocked(listDownloads).mockResolvedValue([])
  })

  it('FE-C1: has URL input and Extract button; Extract shows loading then title and format list', async () => {
    const { extract } = await import('./services/api')
    vi.mocked(extract).mockResolvedValueOnce({
      title: 'Mocked Video Title',
      formats: [
        { format_id: '22', resolution: '720p', ext: 'mp4' },
        { format_id: '18', resolution: '360p', ext: 'mp4' },
      ],
      playlist_entries: [],
    })

    render(<App />)
    const input = screen.getByPlaceholderText('https://...')
    const extractBtn = screen.getByRole('button', { name: /extract/i })

    expect(extractBtn).toBeDisabled()
    await userEvent.type(input, 'https://youtube.com/watch?v=1')
    expect(extractBtn).toBeEnabled()

    await userEvent.click(extractBtn)
    await screen.findByText('Mocked Video Title')
    expect(screen.getByText(/select format/i)).toBeInTheDocument()
    const options = screen.getByRole('combobox').querySelectorAll('option')
    expect(options.length).toBeGreaterThanOrEqual(2)
  })

  it('FE-C2: format selection and Download button', async () => {
    useDownloadsStore.setState({
      url: 'https://youtube.com/watch?v=1',
      extractResult: {
        title: 'T',
        formats: [
          { format_id: '22', resolution: '720p', ext: 'mp4' },
          { format_id: '18', resolution: '360p', ext: 'mp4' },
        ],
        playlist_entries: [],
      },
    })
    const { startDownload } = await import('./services/api')
    vi.mocked(startDownload).mockResolvedValueOnce({ job_id: 'job-123' })

    render(<App />)
    const downloadBtn = screen.getByRole('button', { name: /download/i })
    expect(downloadBtn).toBeInTheDocument()
    await userEvent.click(downloadBtn)
    expect(startDownload).toHaveBeenCalled()
  })

  it('FE-C3: download list shows jobs with status and Cancel/Pause/Retry buttons', async () => {
    const api = await import('./services/api')
    const testJobs = [
      {
        id: 'j1',
        url: 'https://a.com',
        title: 'Video A',
        status: 'downloading',
        progress: 45,
        created_at: '',
        updated_at: '',
      },
      {
        id: 'j2',
        url: 'https://b.com',
        status: 'failed',
        progress: 0,
        created_at: '',
        updated_at: '',
      },
    ]
    vi.mocked(api.listDownloads).mockResolvedValue(testJobs)

    render(<App />)
    await screen.findByText(/Video A/)
    expect(screen.getByText(/downloading/)).toBeInTheDocument()
    expect(screen.getByText(/45%/)).toBeInTheDocument()
    expect(screen.getByText(/failed/)).toBeInTheDocument()
    const cancelBtn = screen.getByRole('button', { name: /cancel/i })
    const retryBtn = screen.getByRole('button', { name: /retry/i })
    expect(cancelBtn).toBeInTheDocument()
    expect(retryBtn).toBeInTheDocument()

    await userEvent.click(cancelBtn)
    expect(api.cancelDownload).toHaveBeenCalledWith('j1')
  })
})
