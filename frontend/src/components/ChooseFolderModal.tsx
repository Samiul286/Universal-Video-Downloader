import { useState } from 'react';
import { debugLog } from '../store/debugLog';

interface ChooseFolderModalProps {
  onChoose: (path: string) => void;
  onClose: () => void;
}

export function ChooseFolderModal({ onChoose, onClose }: ChooseFolderModalProps) {
  const [path, setPath] = useState('');

  return (
    <div style={{ position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.5)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 10 }}>
      <div style={{ background: '#242424', padding: 24, borderRadius: 8, minWidth: 360 }}>
        <h3 style={{ marginTop: 0 }}>Choose folder to save this video</h3>
        <p style={{ color: '#888', fontSize: 14 }}>No save folder is set. Enter the full path to a folder where you want to save downloads (e.g. C:\Users\You\Downloads).</p>
        <input
          type="text"
          value={path}
          onChange={(e) => setPath(e.target.value)}
          placeholder="C:\Users\...\Downloads"
          style={{ width: '100%', padding: 8, marginBottom: 16, boxSizing: 'border-box' }}
        />
        <div style={{ display: 'flex', gap: 8, justifyContent: 'flex-end' }}>
          <button onClick={onClose}>Cancel</button>
          <button
            onClick={() => {
              const p = path.trim();
              if (p) {
                debugLog('UI', 'ChooseFolderModal: user chose folder', { path: p });
                onChoose(p);
              }
            }}
            disabled={!path.trim()}
          >
            Use this folder
          </button>
        </div>
      </div>
    </div>
  );
}
