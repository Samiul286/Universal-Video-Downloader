import axios from 'axios';
import { debugLog, debugLogError } from '../store/debugLog';

// Use environment variable for production, empty string for development (Vite proxy)
const API_BASE_URL = import.meta.env.VITE_API_URL || '';
const api = axios.create({ baseURL: API_BASE_URL, timeout: 30000 });

// Capture every API error so we see the EXACT issue (status, response body, url)
api.interceptors.response.use(
  (res) => res,
  (err) => {
    debugLogError('axios', err?.message ?? 'Request failed', err);
    return Promise.reject(err);
  }
);

export interface FormatItem {
  format_id: string;
  ext?: string;
  resolution?: string;
  filesize?: number;
  vcodec?: string;
  acodec?: string;
}

export interface ExtractResponse {
  title: string;
  thumbnail?: string;
  duration?: number;
  formats: FormatItem[];
  playlist_entries: { id?: string; title?: string; url: string }[];
}

export async function extract(url: string, cookies?: string | null): Promise<ExtractResponse> {
  debugLog('API', 'POST /api/extract', { url });
  try {
    const body = cookies?.trim() ? { url, cookies: cookies.trim() } : { url };
    const { data } = await api.post<ExtractResponse>('/api/extract', body);
    debugLog('API', 'POST /api/extract OK', { title: data.title, formatsCount: data.formats?.length, playlistCount: data.playlist_entries?.length });
    return data;
  } catch (err) {
    debugLogError('API', 'POST /api/extract FAIL', err);
    throw err;
  }
}

export interface DownloadRequest {
  url: string;
  /** Video title (from extract); shown in downloads list */
  title?: string | null;
  format_id?: string;
  download_path?: string;
  /** Netscape-format cookies (optional); used for this download only. */
  cookies?: string | null;
  /** Video thumbnail URL (e.g. from extract); shown in downloads list. */
  thumbnail?: string | null;
}

export interface DownloadResponse {
  job_id: string;
}

export async function startDownload(payload: DownloadRequest): Promise<DownloadResponse> {
  const body = { ...payload };
  if (!body.cookies?.trim()) delete body.cookies;
  debugLog('API', 'POST /api/download', { url: body.url, format_id: body.format_id, download_path: body.download_path });
  try {
    const { data } = await api.post<DownloadResponse>('/api/download', body);
    debugLog('API', 'POST /api/download OK', { job_id: data.job_id });
    return data;
  } catch (err) {
    debugLogError('API', 'POST /api/download FAIL', err);
    throw err;
  }
}

export interface DownloadItem {
  id: string;
  url: string;
  title?: string;
  status: string;
  progress: number;
  filepath?: string;
  format_id?: string;
  /** Reason when status is "failed" (from backend yt-dlp/worker) */
  error_message?: string;
  /** Video thumbnail URL for list UI */
  thumbnail?: string | null;
  created_at: string;
  updated_at: string;
}

export async function listDownloads(): Promise<DownloadItem[]> {
  try {
    const { data } = await api.get<DownloadItem[]>('/api/downloads');
    debugLog('API', 'GET /api/downloads OK', { count: data?.length });
    return data;
  } catch (err) {
    debugLogError('API', 'GET /api/downloads FAIL', err);
    throw err;
  }
}

export async function cancelDownload(jobId: string): Promise<void> {
  debugLog('API', `DELETE /api/cancel/${jobId}`);
  await api.delete(`/api/cancel/${jobId}`);
}

export async function pauseDownload(jobId: string): Promise<void> {
  debugLog('API', `POST /api/pause/${jobId}`);
  await api.post(`/api/pause/${jobId}`);
}

export async function resumeDownload(jobId: string): Promise<void> {
  debugLog('API', `POST /api/resume/${jobId}`);
  await api.post(`/api/resume/${jobId}`);
}

export async function retryDownload(jobId: string): Promise<void> {
  debugLog('API', `POST /api/retry/${jobId}`);
  await api.post(`/api/retry/${jobId}`);
}

export async function removeDownload(jobId: string): Promise<void> {
  debugLog('API', `DELETE /api/downloads/${jobId}`);
  await api.delete(`/api/downloads/${jobId}`);
}

export async function removeDownloads(jobIds: string[]): Promise<{ removed: number }> {
  debugLog('API', 'DELETE /api/downloads (batch)', { job_ids: jobIds });
  const { data } = await api.delete<{ removed: number }>('/api/downloads', {
    data: { job_ids: jobIds },
  });
  debugLog('API', 'DELETE /api/downloads (batch) OK', { removed: data.removed });
  return data;
}

export interface SettingsResponse {
  settings: Record<string, string>;
}

export async function getSettings(): Promise<SettingsResponse> {
  debugLog('API', 'GET /api/settings');
  const { data } = await api.get<SettingsResponse>('/api/settings');
  debugLog('API', 'GET /api/settings OK', { keys: Object.keys(data.settings || {}) });
  return data;
}

export async function putSettings(settings: Record<string, string>): Promise<SettingsResponse> {
  debugLog('API', 'PUT /api/settings', { keys: Object.keys(settings || {}) });
  const { data } = await api.put<SettingsResponse>('/api/settings', { settings });
  return data;
}

export function isNoValidDownloadPathError(err: unknown): boolean {
  return axios.isAxiosError(err) && err.response?.status === 503 && (err.response?.data as { detail?: string })?.detail === 'no_valid_download_path';
}
