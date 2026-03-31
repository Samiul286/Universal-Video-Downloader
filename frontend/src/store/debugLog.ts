/**
 * In-memory debug log for the entire flow (extract → download → jobs).
 * Use "Debug" panel in UI to see what happened without opening DevTools.
 * ERROR capture: last error is stored and shown prominently to find exact issue.
 */

const MAX_ENTRIES = 80;

export interface DebugEntry {
  ts: string;
  tag: string;
  message: string;
  detail?: unknown;
}

/** Full serialized error for "Last error" box - so we see exact issue. */
export interface LastErrorInfo {
  ts: string;
  message: string;
  status?: number;
  statusText?: string;
  responseData?: unknown;
  url?: string;
  stack?: string;
  source: string; // e.g. 'API', 'STORE', 'axios'
}

let entries: DebugEntry[] = [];
let lastError: LastErrorInfo | null = null;
const errorListeners: Array<(err: LastErrorInfo | null) => void> = [];

function ts(): string {
  return new Date().toISOString().slice(11, 23);
}

export function debugLog(tag: string, message: string, detail?: unknown): void {
  const entry: DebugEntry = { ts: ts(), tag, message, detail };
  entries = [entry, ...entries].slice(0, MAX_ENTRIES);
  console.log(`[DEBUG ${entry.ts}] [${tag}] ${message}`, detail ?? '');
  listeners.forEach((cb) => cb(entries));
}

/** Call this when an error occurs - saves full error so we find exact issue. */
export function debugLogError(source: string, message: string, err: unknown): void {
  const info: LastErrorInfo = {
    ts: ts(),
    message: message,
    source,
  };
  if (err && typeof err === 'object') {
    const e = err as Record<string, unknown>;
    if (e.message !== undefined) info.message = String(e.message);
    if (e.stack !== undefined) info.stack = String(e.stack);
    // Axios error shape
    if (e.response && typeof e.response === 'object') {
      const res = e.response as Record<string, unknown>;
      if (res.status !== undefined) info.status = Number(res.status);
      if (res.statusText !== undefined) info.statusText = String(res.statusText);
      if (res.data !== undefined) info.responseData = res.data;
    }
    if (e.config && typeof e.config === 'object') {
      const cfg = e.config as Record<string, unknown>;
      if (cfg.url !== undefined) info.url = String(cfg.url);
    }
  } else {
    info.responseData = err;
  }
  lastError = info;
  errorListeners.forEach((cb) => cb(lastError));
  const entry: DebugEntry = { ts: info.ts, tag: 'ERROR', message: `[${source}] ${message}`, detail: info };
  entries = [entry, ...entries].slice(0, MAX_ENTRIES);
  console.error('[DEBUG ERROR]', info);
  listeners.forEach((cb) => cb(entries));
}

const listeners: Array<(entries: DebugEntry[]) => void> = [];

export function subscribeDebugLog(cb: (entries: DebugEntry[]) => void): () => void {
  listeners.push(cb);
  cb(entries);
  return () => {
    const i = listeners.indexOf(cb);
    if (i >= 0) listeners.splice(i, 1);
  };
}

export function subscribeLastError(cb: (err: LastErrorInfo | null) => void): () => void {
  errorListeners.push(cb);
  cb(lastError);
  return () => {
    const i = errorListeners.indexOf(cb);
    if (i >= 0) errorListeners.splice(i, 1);
  };
}

export function getDebugEntries(): DebugEntry[] {
  return entries;
}

export function getLastError(): LastErrorInfo | null {
  return lastError;
}

export function clearDebugLog(): void {
  entries = [];
  lastError = null;
  errorListeners.forEach((cb) => cb(null));
  listeners.forEach((cb) => cb(entries));
}
