/**
 * FE-U3: WebSocket client — connect to /ws/progress with job_id; parse progress messages and update callback.
 */
import { describe, it, expect } from 'vitest';
import { parseProgressMessage } from './progressWs';

describe('parseProgressMessage (WS contract)', () => {
  it('parses valid progress message', () => {
    const msg = parseProgressMessage(
      JSON.stringify({
        job_id: 'uuid-1',
        percent: 50.5,
        speed: 1000000,
        eta: 30,
        status: 'downloading',
      })
    )
    expect(msg).not.toBeNull()
    expect(msg!.job_id).toBe('uuid-1')
    expect(msg!.percent).toBe(50.5)
    expect(msg!.status).toBe('downloading')
  })

  it('returns null for invalid JSON', () => {
    expect(parseProgressMessage('not json')).toBeNull()
  })

  it('returns null when job_id or percent missing', () => {
    expect(parseProgressMessage(JSON.stringify({ percent: 50 }))).toBeNull()
    expect(parseProgressMessage(JSON.stringify({ job_id: 'x' }))).toBeNull()
  })
})
