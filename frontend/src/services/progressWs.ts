/**
 * WebSocket client for live download progress from backend /ws/progress.
 */

export interface ProgressMessage {
  job_id: string;
  percent: number;
  speed: number | null;
  eta: number | null;
  status: string;
}

export function parseProgressMessage(data: string): ProgressMessage | null {
  try {
    const o = JSON.parse(data) as Record<string, unknown>;
    if (typeof o.job_id !== 'string' || typeof o.percent !== 'number') return null;
    return {
      job_id: o.job_id,
      percent: o.percent,
      speed: (o.speed as number) ?? null,
      eta: (o.eta as number) ?? null,
      status: (o.status as string) ?? 'downloading',
    };
  } catch {
    return null;
  }
}

/** WebSocket URL for progress stream (same origin; Vite proxies /ws to backend in dev). */
export function getProgressWsUrl(): string {
  // Production: use backend URL from environment variable
  const apiUrl = import.meta.env.VITE_API_URL;
  if (apiUrl) {
    try {
      const url = new URL(apiUrl);
      const protocol = url.protocol === 'https:' ? 'wss:' : 'ws:';
      return `${protocol}//${url.host}/ws/progress`;
    } catch {
      // Fallback if URL parsing fails
    }
  }
  
  // Development: use same origin (Vite proxy)
  const protocol = typeof window !== 'undefined' && window.location.protocol === 'https:' ? 'wss:' : 'ws:';
  const host = typeof window !== 'undefined' ? window.location.host : 'localhost:5173';
  return `${protocol}//${host}/ws/progress`;
}
