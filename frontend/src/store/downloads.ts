import { create } from 'zustand';
import type { DownloadItem, ExtractResponse } from '../services/api';
import * as api from '../services/api';
import { debugLog, debugLogError } from './debugLog';

interface DownloadsState {
  url: string;
  setUrl: (u: string) => void;
  /** Optional Netscape-format cookies (e.g. for YouTube); used for extract and download when set. */
  userCookies: string;
  setUserCookies: (c: string) => void;
  extractResult: ExtractResponse | null;
  selectedFormatId: string | null;
  jobs: DownloadItem[];
  loading: boolean;
  error: string | null;
  extract: () => Promise<void>;
  setSelectedFormat: (id: string | null) => void;
  startDownload: (downloadPath?: string) => Promise<{ jobId: string } | { needFolder: true }>;
  refreshJobs: () => Promise<void>;
  cancel: (jobId: string) => Promise<void>;
  pause: (jobId: string) => Promise<void>;
  resume: (jobId: string) => Promise<void>;
  retry: (jobId: string) => Promise<void>;
  remove: (jobIds: string[]) => Promise<void>;
  clearError: () => void;
  setJobProgress: (jobId: string, progress: number) => void;
}

export const useDownloadsStore = create<DownloadsState>((set, get) => ({
  url: '',
  userCookies: '',
  extractResult: null,
  selectedFormatId: null,
  jobs: [],
  loading: false,
  error: null,

  setUrl: (u) => set({ url: u }),

  setUserCookies: (c) => set({ userCookies: c }),

  setSelectedFormat: (id) => set({ selectedFormatId: id }),

  extract: async () => {
    const { url, userCookies } = get();
    if (!url.trim()) {
      debugLog('STORE', 'extract skipped: empty url');
      return;
    }
    debugLog('STORE', 'extract start', { url: url.trim() });
    set({ loading: true, error: null });
    try {
      const result = await api.extract(url.trim(), userCookies || undefined);
      set({ extractResult: result, loading: false });
      debugLog('STORE', 'extract success', { title: result.title, formatsCount: result.formats?.length });
    } catch (e: unknown) {
      const msg = e instanceof Error ? e.message : 'Extract failed';
      set({ loading: false, error: msg });
      debugLogError('STORE', 'extract failed', e);
    }
  },

  startDownload: async (downloadPath?: string) => {
    const { url, selectedFormatId, userCookies, extractResult } = get();
    if (!url.trim()) {
      debugLog('STORE', 'startDownload skipped: empty url');
      return { needFolder: false as const, jobId: '' };
    }
    debugLog('STORE', 'startDownload start', { url: url.trim(), selectedFormatId, downloadPath });
    set({ error: null });
    try {
      const res = await api.startDownload({
        url: url.trim(),
        title: extractResult?.title ?? undefined,
        format_id: selectedFormatId ?? undefined,
        download_path: downloadPath,
        cookies: userCookies?.trim() || undefined,
        thumbnail: extractResult?.thumbnail ?? undefined,
      });
      await get().refreshJobs();
      debugLog('STORE', 'startDownload success', { jobId: res.job_id });
      return { jobId: res.job_id };
    } catch (e: unknown) {
      if (api.isNoValidDownloadPathError(e)) {
        debugLog('STORE', 'startDownload needFolder (503 no_valid_download_path)');
        return { needFolder: true };
      }
      const msg = e instanceof Error ? e.message : 'Download failed';
      set({ error: msg });
      debugLogError('STORE', 'startDownload failed', e);
      return { needFolder: false as const, jobId: '' };
    }
  },

  refreshJobs: async () => {
    try {
      const jobs = await api.listDownloads();
      set({ jobs });
      if (jobs.length > 0) debugLog('STORE', 'refreshJobs', { count: jobs.length, statuses: jobs.map((j) => j.status) });
    } catch (e) {
      debugLogError('STORE', 'refreshJobs failed', e);
    }
  },

  cancel: async (jobId) => {
    debugLog('STORE', 'cancel', { jobId });
    await api.cancelDownload(jobId);
    await get().refreshJobs();
  },
  pause: async (jobId) => {
    debugLog('STORE', 'pause', { jobId });
    await api.pauseDownload(jobId);
    await get().refreshJobs();
  },
  resume: async (jobId) => {
    debugLog('STORE', 'resume', { jobId });
    await api.resumeDownload(jobId);
    await get().refreshJobs();
  },
  retry: async (jobId) => {
    debugLog('STORE', 'retry', { jobId });
    await api.retryDownload(jobId);
    await get().refreshJobs();
  },

  remove: async (jobIds) => {
    debugLog('STORE', 'remove', { jobIds, removeAll: jobIds.length === 0 });
    await api.removeDownloads(jobIds);
    await get().refreshJobs();
  },

  clearError: () => set({ error: null }),

  setJobProgress: (jobId, progress) => {
    set((state) => ({
      jobs: state.jobs.map((j) =>
        j.id === jobId ? { ...j, progress } : j
      ),
    }));
  },
}));
