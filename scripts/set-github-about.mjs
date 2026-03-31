#!/usr/bin/env node
/**
 * Set GitHub repo description and topics via API.
 * Requires: GITHUB_TOKEN (env), and GITHUB_REPO (env, e.g. "owner/repo") or git remote origin.
 * Run from repo root: node scripts/set-github-about.mjs
 */

const DESCRIPTION =
  'Universal video downloader from URL. YouTube, Vimeo, TikTok, 1000+ sites. Paste link → pick quality → save. FastAPI + React, self-hosted, no cloud.';

const TOPICS = [
  'universal-video-downloader',
  'video-downloader',
  'youtube-downloader',
  'yt-dlp',
  'yt-dlp-web',
  'fastapi',
  'react',
  'python',
  'typescript',
  'vite',
  'self-hosted',
  'open-source',
  'download-videos',
  'paste-url',
  'quality-selector',
  'download-queue',
  'websocket',
  'sqlite',
  'rest-api',
  'swagger',
  'playlist-download',
  'batch-download',
  'vimeo-downloader',
  'tiktok-downloader',
  'instagram-downloader',
  'ffmpeg',
  'no-cloud',
  'local-first',
  'mit-license',
  'developer-tools',
];

function getRepo() {
  if (process.env.GITHUB_REPO) {
    const [owner, repo] = process.env.GITHUB_REPO.split('/');
    if (owner && repo) return { owner, repo };
  }
  const { execSync } = await import('child_process');
  try {
    const url = execSync('git config --get remote.origin.url', { encoding: 'utf-8' }).trim();
    const match = url.match(/github\.com[:/]([^/]+)\/([^/.]+)/);
    if (match) return { owner: match[1], repo: match[2].replace(/\.git$/, '') };
  } catch (_) {}
  return null;
}

async function main() {
  const token = process.env.GITHUB_TOKEN;
  if (!token) {
    console.error('Set GITHUB_TOKEN (e.g. a classic Personal Access Token with repo scope).');
    process.exit(1);
  }

  const repo = getRepo();
  if (!repo) {
    console.error('Set GITHUB_REPO (e.g. "owner/repo") or run from a git repo with remote.origin pointing to GitHub.');
    process.exit(1);
  }

  const base = `https://api.github.com/repos/${repo.owner}/${repo.repo}`;
  const headers = {
    Authorization: `Bearer ${token}`,
    Accept: 'application/vnd.github+json',
    'X-GitHub-Api-Version': '2022-11-28',
  };

  console.log(`Updating ${repo.owner}/${repo.repo}...`);

  const res1 = await fetch(base, {
    method: 'PATCH',
    headers: { ...headers, 'Content-Type': 'application/json' },
    body: JSON.stringify({ description: DESCRIPTION }),
  });
  if (!res1.ok) {
    const t = await res1.text();
    console.error('Description update failed:', res1.status, t);
    process.exit(1);
  }
  console.log('Description set.');

  const res2 = await fetch(`${base}/topics`, {
    method: 'PUT',
    headers: { ...headers, 'Content-Type': 'application/json' },
    body: JSON.stringify({ names: TOPICS }),
  });
  if (!res2.ok) {
    const t = await res2.text();
    console.error('Topics update failed:', res2.status, t);
    process.exit(1);
  }
  console.log('Topics set (' + TOPICS.length + '). Done.');
}

main();
