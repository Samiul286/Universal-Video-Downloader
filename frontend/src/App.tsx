import { useEffect, useState, useRef } from 'react';
import { useDownloadsStore } from './store/downloads';
import { ChooseFolderModal } from './components/ChooseFolderModal';
import { subscribeDebugLog, getDebugEntries, clearDebugLog, debugLog, subscribeLastError, type DebugEntry, type LastErrorInfo } from './store/debugLog';
import { getProgressWsUrl, parseProgressMessage } from './services/progressWs';
import './App.css';

const SAMPLE_VIDEO_URL = 'https://youtu.be/R3GfuzLMPkA?si=AYzP6Sj7xQG1lSmv';

function JobProgressBar({ status, progress }: { status: string; progress: number }) {
  const percent = status === 'completed' ? 100 : Math.min(100, Math.max(0, progress));
  const isCompleted = status === 'completed';
  const isFailed = status === 'failed';
  const isIndeterminate = status === 'queued' || status === 'paused';
  return (
    <div
      className={`progress-bar ${isCompleted ? 'progress-bar--completed' : ''} ${isFailed ? 'progress-bar--failed' : ''} ${isIndeterminate ? 'progress-bar--indeterminate' : ''}`}
      role="progressbar"
      aria-valuenow={isIndeterminate ? undefined : percent}
      aria-valuemin={0}
      aria-valuemax={100}
      aria-label={isCompleted ? 'Completed' : isFailed ? 'Failed' : `Download progress ${Math.round(percent)}%`}
    >
      <div className="progress-bar-fill" style={{ width: isIndeterminate ? undefined : `${percent}%` }} />
    </div>
  );
}

function App() {
  const {
    url,
    setUrl,
    userCookies,
    setUserCookies,
    extractResult,
    selectedFormatId,
    setSelectedFormat,
    jobs,
    loading,
    error,
    extract,
    startDownload,
    refreshJobs,
    cancel,
    pause,
    resume,
    retry,
    remove,
    clearError,
  } = useDownloadsStore();

  const [showChooseFolder, setShowChooseFolder] = useState(false);
  const [showCookies, setShowCookies] = useState(false);
  const [openCopiedId, setOpenCopiedId] = useState<string | null>(null);
  const [linkCopiedId, setLinkCopiedId] = useState<string | null>(null);
  const [pollingKey, setPollingKey] = useState(0);

  const copyFolderPath = (filepath: string) => {
    const sep = filepath.includes('\\') ? '\\' : '/';
    const folder = filepath.slice(0, filepath.lastIndexOf(sep));
    navigator.clipboard.writeText(folder);
    setOpenCopiedId(filepath);
    setTimeout(() => setOpenCopiedId(null), 2000);
  };
  const copyVideoLink = (jobId: string, url: string) => {
    navigator.clipboard.writeText(url);
    setLinkCopiedId(jobId);
    setTimeout(() => setLinkCopiedId(null), 2000);
  };
  const [selectedIds, setSelectedIds] = useState<Set<string>>(new Set());
  const [debugEntries, setDebugEntries] = useState<DebugEntry[]>(() => getDebugEntries());
  const [lastError, setLastError] = useState<LastErrorInfo | null>(null);
  const [showDebug, setShowDebug] = useState(true);

  const loadCookiesFile = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    const reader = new FileReader();
    reader.onload = () => {
      const text = typeof reader.result === 'string' ? reader.result : '';
      setUserCookies(text);
      setShowCookies(true);
    };
    reader.readAsText(file);
    e.target.value = '';
  };

  useEffect(() => {
    return subscribeDebugLog(setDebugEntries);
  }, []);
  useEffect(() => {
    return subscribeLastError(setLastError);
  }, []);

  const wsReconnectRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  useEffect(() => {
    const wsUrl = getProgressWsUrl();
    let ws: WebSocket | null = null;
    let closed = false;

    const connect = () => {
      if (closed) return;
      ws = new WebSocket(wsUrl);
      ws.onmessage = (event) => {
        const msg = parseProgressMessage(event.data);
        if (msg) useDownloadsStore.getState().setJobProgress(msg.job_id, msg.percent);
      };
      ws.onclose = () => {
        ws = null;
        if (!closed) wsReconnectRef.current = setTimeout(connect, 2000);
      };
      ws.onerror = () => { /* reconnect on close */ };
    };

    connect();
    return () => {
      closed = true;
      if (wsReconnectRef.current) clearTimeout(wsReconnectRef.current);
      wsReconnectRef.current = null;
      if (ws) ws.close();
    };
  }, []);

  useEffect(() => {
    refreshJobs();
    const ACTIVE_STATUSES = ['queued', 'downloading', 'paused'];
    const intervalId = setInterval(async () => {
      await refreshJobs();
      const currentJobs = useDownloadsStore.getState().jobs;
      const hasActive = currentJobs.some((j) => ACTIVE_STATUSES.includes(j.status));
      if (!hasActive) clearInterval(intervalId);
    }, 500);
    return () => clearInterval(intervalId);
  }, [refreshJobs, pollingKey]);

  const handleDownload = async () => {
    debugLog('UI', 'App: user clicked Download');
    const result = await startDownload();
    if (result && 'needFolder' in result && result.needFolder) {
      debugLog('UI', 'App: showing ChooseFolder modal (needFolder)');
      setShowChooseFolder(true);
    } else if (result && 'jobId' in result && result.jobId) {
      debugLog('UI', 'App: download started', { jobId: result.jobId });
      setPollingKey((k) => k + 1);
    }
  };

  const handleChooseFolder = async (path: string) => {
    debugLog('UI', 'App: user chose folder, starting download', { path });
    setShowChooseFolder(false);
    const result = await startDownload(path);
    if (result && 'jobId' in result && result.jobId) {
      debugLog('UI', 'App: download started after folder choice', { jobId: result.jobId });
      setPollingKey((k) => k + 1);
    }
  };

  const toggleSelect = (id: string) => {
    setSelectedIds((prev) => {
      const next = new Set(prev);
      if (next.has(id)) next.delete(id);
      else next.add(id);
      return next;
    });
  };
  const selectAll = (checked: boolean) => {
    setSelectedIds(checked ? new Set(jobs.map((j) => j.id)) : new Set());
  };
  const allSelected = jobs.length > 0 && selectedIds.size === jobs.length;
  const someSelected = selectedIds.size > 0;

  const completedCount = jobs.filter((j) => j.status === 'completed').length;
  const failedCount = jobs.filter((j) => j.status === 'failed').length;
  const inProgressCount = jobs.filter((j) => ['queued', 'downloading', 'paused'].includes(j.status)).length;
  const handleRemoveSelected = async () => {
    if (selectedIds.size === 0) return;
    debugLog('UI', 'App: remove selected', { count: selectedIds.size, ids: Array.from(selectedIds) });
    await remove(Array.from(selectedIds));
    setSelectedIds(new Set());
  };
  const handleRemoveAll = async () => {
    debugLog('UI', 'App: remove all');
    await remove([]);
    setSelectedIds(new Set());
  };

  return (
    <div className="app">
      <h1>Universal Video Downloader</h1>

      <div className="card">
        <label>
          Video URL
          <input
            type="url"
            value={url}
            onChange={(e) => setUrl(e.target.value)}
            placeholder="https://..."
            disabled={loading}
          />
        </label>
        <div className="url-actions">
          <button onClick={extract} disabled={loading || !url.trim()}>
            {loading ? 'Extracting…' : 'Extract'}
          </button>
          <button
            type="button"
            className="sample-url-btn"
            onClick={() => setUrl(SAMPLE_VIDEO_URL)}
            disabled={loading}
            title="Fill with a sample YouTube URL to try the app"
          >
            Try sample URL
          </button>
        </div>
        <p className="sample-url-hint">New here? Click “Try sample URL” then “Extract” to test.</p>
        <div className="card" style={{ marginTop: '0.5rem', padding: '0.75rem' }}>
          <button
            type="button"
            onClick={() => setShowCookies((v) => !v)}
            aria-expanded={showCookies}
            style={{ background: 'none', border: 'none', color: 'inherit', cursor: 'pointer', fontSize: '0.95rem', padding: 0, textAlign: 'left', width: '100%' }}
          >
            {showCookies ? '▼' : '▶'} Use my cookies (optional)
          </button>
          {showCookies && (
            <div style={{ marginTop: '0.5rem' }}>
              <p style={{ margin: '0 0 0.5rem 0', fontSize: '0.85rem', color: '#94a3b8' }}>
                If YouTube asks you to sign in, paste Netscape-format cookies here (e.g. from a browser extension). Used for Extract and Download only; not stored on the server.
              </p>
              <textarea
                value={userCookies}
                onChange={(e) => setUserCookies(e.target.value)}
                placeholder="# Netscape HTTP Cookie File..."
                rows={4}
                style={{ width: '100%', maxWidth: 560, fontFamily: 'monospace', fontSize: 12, padding: '0.5rem', resize: 'vertical' }}
                aria-label="Cookies (Netscape format)"
              />
              <div style={{ marginTop: '0.25rem', display: 'flex', gap: '0.5rem', alignItems: 'center' }}>
                <label style={{ fontSize: '0.85rem', cursor: 'pointer' }}>
                  <input type="file" accept=".txt" onChange={loadCookiesFile} style={{ marginRight: '0.25rem' }} />
                  Load from file
                </label>
                {userCookies && (
                  <button type="button" onClick={() => setUserCookies('')} style={{ fontSize: '0.85rem' }}>
                    Clear
                  </button>
                )}
              </div>
            </div>
          )}
        </div>
      </div>

      {error && (
        <div className="error" role="alert">
          {error}
          <button type="button" onClick={clearError} aria-label="Dismiss">×</button>
        </div>
      )}

      {lastError && (
        <div
          className="card"
          style={{
            marginTop: '0.5rem',
            border: '2px solid #c53030',
            background: '#2d1f1f',
          }}
        >
          <h3 style={{ margin: '0 0 0.5rem 0', color: '#fc8181' }}>Last error (exact issue)</h3>
          <pre
            style={{
              margin: 0,
              padding: '0.75rem',
              fontSize: '12px',
              overflow: 'auto',
              background: '#1a1a1a',
              color: '#e2e8f0',
              borderRadius: 4,
              whiteSpace: 'pre-wrap',
              wordBreak: 'break-all',
            }}
          >
            {[
              `Time: ${lastError.ts}`,
              `Source: ${lastError.source}`,
              `Message: ${lastError.message}`,
              lastError.status != null && `HTTP Status: ${lastError.status} ${lastError.statusText ?? ''}`.trim(),
              lastError.url != null && `URL: ${lastError.url}`,
              lastError.responseData != null && `Response: ${JSON.stringify(lastError.responseData, null, 2)}`,
              lastError.stack != null && `Stack: ${lastError.stack}`,
            ]
              .filter(Boolean)
              .join('\n')}
          </pre>
        </div>
      )}

      {extractResult && (
        <div className="card">
          <h2>{extractResult.title}</h2>
          {extractResult.thumbnail && (
            <img src={extractResult.thumbnail} alt="" style={{ maxWidth: 320, maxHeight: 180 }} />
          )}
          <p>Select format:</p>
          <select
            value={selectedFormatId ?? ''}
            onChange={(e) => setSelectedFormat(e.target.value || null)}
          >
            <option value="">Best</option>
            {extractResult.formats.map((f) => (
              <option key={f.format_id} value={f.format_id}>
                {f.resolution ?? f.format_id} {f.ext ?? ''} {f.filesize ? `(${Math.round(f.filesize / 1024 / 1024)} MB)` : ''}
              </option>
            ))}
          </select>
          <button onClick={handleDownload} disabled={!url.trim()}>
            Download
          </button>
        </div>
      )}

      <div className="card">
        <h2>Downloads</h2>
        {jobs.length > 0 && (
          <p className="downloads-summary" aria-live="polite">
            <span className="downloads-summary-completed">{completedCount} completed</span>
            {inProgressCount > 0 && <span className="downloads-summary-active">{inProgressCount} in progress</span>}
            {failedCount > 0 && <span className="downloads-summary-failed">{failedCount} failed</span>}
          </p>
        )}
        {jobs.length > 0 && (
          <div className="downloads-toolbar" style={{ marginBottom: '0.75rem', display: 'flex', alignItems: 'center', gap: '0.5rem', flexWrap: 'wrap' }}>
            <label style={{ display: 'flex', alignItems: 'center', gap: '0.25rem' }}>
              <input
                type="checkbox"
                checked={allSelected}
                ref={(el) => el && (el.indeterminate = someSelected && !allSelected)}
                onChange={(e) => selectAll(e.target.checked)}
                aria-label="Select all"
              />
              <span>Select all</span>
            </label>
            <button
              type="button"
              onClick={handleRemoveSelected}
              disabled={!someSelected}
              aria-label="Remove selected"
            >
              Remove selected
            </button>
            <button type="button" onClick={handleRemoveAll} aria-label="Remove all">
              Remove all
            </button>
          </div>
        )}
        <ul className="job-list">
          {jobs.length === 0 && <li>No downloads yet.</li>}
          {jobs.map((j) => (
            <li key={j.id} className="job-list-item job-list-item--card">
              <div className="job-list-item-top">
                <label className="job-list-item-check">
                  <input
                    type="checkbox"
                    checked={selectedIds.has(j.id)}
                    onChange={() => toggleSelect(j.id)}
                    aria-label={`Select ${j.title || j.url}`}
                  />
                </label>
                <div className="job-list-item-thumb">
                  {j.thumbnail ? (
                    <img src={j.thumbnail} alt="" width={120} height={68} loading="lazy" />
                  ) : (
                    <div className="job-list-item-thumb-placeholder" aria-hidden />
                  )}
                </div>
                <div className="job-list-item-title-wrap">
                  <span className="job-title" title={j.url}>{j.title || j.url}</span>
                  <button
                    type="button"
                    className="job-copy-link-icon"
                    onClick={() => copyVideoLink(j.id, j.url)}
                    title="Copy video URL"
                    aria-label="Copy link"
                  >
                    {linkCopiedId === j.id ? (
                      <span className="job-copy-link-check" aria-hidden>✓</span>
                    ) : (
                      <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden><path d="M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.71" /><path d="M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l1.71-1.71" /></svg>
                    )}
                  </button>
                </div>
              </div>
              <div className="job-list-item-bottom">
                <div className="job-list-item-bar-wrap">
                  <JobProgressBar status={j.status} progress={j.progress} />
                  <span className="job-percent">{Math.round(j.progress)}%</span>
                </div>
                <div className="job-list-item-actions">
                  {['queued', 'downloading', 'paused'].includes(j.status) && (
                    <>
                      <button type="button" onClick={() => cancel(j.id)}>Cancel</button>
                      {j.status === 'paused' ? (
                        <button type="button" onClick={() => resume(j.id)}>Resume</button>
                      ) : (
                        <button type="button" onClick={() => pause(j.id)}>Pause</button>
                      )}
                    </>
                  )}
                  {j.status === 'failed' && (
                    <>
                      <button type="button" onClick={() => retry(j.id)}>Retry</button>
                      {j.error_message && (
                        <span className="job-error-reason" title={j.error_message}>Reason: {j.error_message}</span>
                      )}
                    </>
                  )}
                  {j.status === 'completed' && j.filepath && (
                    <>
                      <button
                        type="button"
                        onClick={() => copyFolderPath(j.filepath!)}
                        title="Copy folder path (paste in Explorer to open)"
                      >
                        {openCopiedId === j.filepath ? 'Copied!' : 'Open'}
                      </button>
                      <button
                        type="button"
                        onClick={() => navigator.clipboard.writeText(j.filepath!)}
                        title="Copy file path"
                      >
                        Copy path
                      </button>
                    </>
                  )}
                  <button
                    type="button"
                    className="job-list-item-remove"
                    onClick={() => remove([j.id])}
                    aria-label={`Remove ${j.title || j.url}`}
                  >
                    Remove
                  </button>
                </div>
              </div>
            </li>
          ))}
        </ul>
      </div>

      {showChooseFolder && (
        <ChooseFolderModal
          onChoose={handleChooseFolder}
          onClose={() => setShowChooseFolder(false)}
        />
      )}

      <div className="card" style={{ marginTop: '1rem' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.5rem' }}>
          <button type="button" onClick={() => setShowDebug((v) => !v)} aria-expanded={showDebug}>
            {showDebug ? '▼' : '▶'} Debug log (entire flow)
          </button>
          <button type="button" onClick={clearDebugLog}>Clear</button>
        </div>
        {showDebug && (
          <pre
            style={{
              margin: 0,
              padding: '0.5rem',
              fontSize: '11px',
              maxHeight: 280,
              overflow: 'auto',
              background: '#1e1e1e',
              color: '#d4d4d4',
              borderRadius: 4,
            }}
          >
            {debugEntries.length === 0 && 'No debug entries yet. Use Extract / Download to see the flow.'}
            {debugEntries.map((e, i) => (
              <div key={i}>
                <span style={{ color: '#858585' }}>{e.ts}</span> <span style={{ color: '#4ec9b0' }}>[{e.tag}]</span> {e.message}
                {e.detail != null && (
                  <span style={{ color: '#ce9178' }}> {typeof e.detail === 'object' ? JSON.stringify(e.detail) : String(e.detail)}</span>
                )}
              </div>
            ))}
          </pre>
        )}
      </div>
    </div>
  );
}

export default App;
