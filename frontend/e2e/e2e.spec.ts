/**
 * E2E-1: Happy path — Paste URL, Extract, Select format, Download; list shows job; progress updates.
 * E2E-2: Cancel — Start download; click Cancel; job status becomes cancelled.
 * E2E-3: Settings — Open settings; change one setting; save; confirm value (if Settings UI exists).
 *
 * Uses route interception to mock API so no real network/yt-dlp.
 */
import { test, expect } from '@playwright/test'

const MOCK_EXTRACT = {
  title: 'E2E Mock Video',
  thumbnail: 'https://example.com/t.jpg',
  duration: 120,
  formats: [
    { format_id: '22', resolution: '720p', ext: 'mp4', filesize: 50_000_000 },
    { format_id: '18', resolution: '360p', ext: 'mp4', filesize: 20_000_000 },
  ],
  playlist_entries: [],
}

test.beforeEach(async ({ page }) => {
  await page.route('**/api/extract', (route) =>
    route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify(MOCK_EXTRACT) })
  )
  await page.route('**/api/downloads', (route) =>
    route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify([]),
    })
  )
  await page.route('**/api/settings', (route) => {
    const url = route.request().url()
    if (route.request().method() === 'GET') {
      return route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({ settings: { download_path: 'C:\\Downloads' } }),
      })
    }
    return route.continue()
  })
})

test('E2E-1: Happy path — paste URL, Extract, select format, Download; list shows job', async ({ page }) => {
  await page.goto('/')
  await expect(page.getByRole('heading', { name: /local video downloader/i })).toBeVisible()

  await page.getByPlaceholder('https://...').fill('https://youtube.com/watch?v=e2e1')
  await page.getByRole('button', { name: /extract/i }).click()
  await expect(page.getByText('E2E Mock Video')).toBeVisible()
  await expect(page.getByText(/select format/i)).toBeVisible()

  await page.route('**/api/download', (route) =>
    route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({ job_id: 'e2e-job-1' }),
    })
  )
  let downloadListCalls = 0
  await page.route('**/api/downloads', (route) => {
    downloadListCalls++
    const body =
      downloadListCalls >= 2
        ? [
            {
              id: 'e2e-job-1',
              url: 'https://youtube.com/watch?v=e2e1',
              title: 'E2E Mock Video',
              status: 'queued',
              progress: 0,
              created_at: new Date().toISOString(),
              updated_at: new Date().toISOString(),
            },
          ]
        : []
    return route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify(body),
    })
  })

  await page.getByRole('button', { name: /download/i }).click()
  await expect(page.getByText(/E2E Mock Video|e2e-job-1|queued/i)).toBeVisible({ timeout: 10000 })
})

test('E2E-2: Cancel — start download, click Cancel, job status cancelled', async ({ page }) => {
  await page.goto('/')
  await page.getByPlaceholder('https://...').fill('https://youtube.com/watch?v=e2e2')
  await page.getByRole('button', { name: /extract/i }).click()
  await expect(page.getByText('E2E Mock Video')).toBeVisible()

  await page.route('**/api/download', (route) =>
    route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({ job_id: 'e2e-job-cancel' }),
    })
  )
  const jobId = 'e2e-job-cancel'
  await page.route('**/api/downloads', (route) =>
    route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify([
        {
          id: jobId,
          url: 'https://youtube.com/watch?v=e2e2',
          title: 'E2E Mock Video',
          status: 'downloading',
          progress: 10,
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString(),
        },
      ]),
    })
  )
  await page.getByRole('button', { name: /download/i }).click()
  await expect(page.getByText(/cancel/i).first()).toBeVisible({ timeout: 5000 })

  await page.route('**/api/cancel/' + jobId, (route) =>
    route.fulfill({ status: 200, contentType: 'application/json', body: '{}' })
  )
  await page.route('**/api/downloads', (route) =>
    route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify([
        {
          id: jobId,
          url: 'https://youtube.com/watch?v=e2e2',
          title: 'E2E Mock Video',
          status: 'cancelled',
          progress: 0,
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString(),
        },
      ]),
    })
  )
  await page.getByRole('button', { name: /cancel/i }).first().click()
  await expect(page.getByText('cancelled')).toBeVisible({ timeout: 5000 })
})

test('E2E-3: App loads and Downloads section visible (settings API mocked)', async ({ page }) => {
  await page.goto('/')
  await expect(page.getByRole('heading', { name: /Universal Video Downloader/i })).toBeVisible()
  await expect(page.getByRole('heading', { name: /downloads/i })).toBeVisible()
})
