r"""Test real YouTube download end-to-end. Run with backend at http://127.0.0.1:8001 (or set BASE_URL).
   Usage: python scripts/test_download_real.py
   Or from backend: .\venv\Scripts\python scripts\test_download_real.py
"""
import os
import sys
import tempfile
import time

# Run from backend directory
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import httpx

BASE_URL = os.environ.get("BASE_URL", "http://127.0.0.1:8001")
TEST_URL = "https://youtu.be/R3GfuzLMPkA?si=_v5kQ2lio-bc7-JG"
POLL_INTERVAL = 2
MAX_WAIT = 600  # 10 minutes


def main():
    with tempfile.TemporaryDirectory() as tmpdir:
        print(f"Download folder: {tmpdir}")
        print(f"Backend: {BASE_URL}")
        print(f"URL: {TEST_URL}")
        print()

        with httpx.Client(base_url=BASE_URL, timeout=30.0) as client:
            # Health
            r = client.get("/health")
            if r.status_code != 200:
                print(f"Backend not ready: GET /health -> {r.status_code}")
                sys.exit(1)
            print("Backend OK")

            # Start download with explicit download_path
            r = client.post("/api/download", json={"url": TEST_URL, "download_path": tmpdir})
            if r.status_code != 200:
                print(f"POST /api/download failed: {r.status_code} {r.text}")
                sys.exit(1)
            job_id = r.json()["job_id"]
            print(f"Job created: {job_id}")
            print("Polling until completed or failed...")

            start = time.monotonic()
            while True:
                elapsed = time.monotonic() - start
                if elapsed > MAX_WAIT:
                    print("Timeout waiting for download")
                    sys.exit(1)
                time.sleep(POLL_INTERVAL)
                r = client.get("/api/downloads")
                if r.status_code != 200:
                    print(f"GET /api/downloads -> {r.status_code}")
                    continue
                jobs = r.json()
                job = next((j for j in jobs if j["id"] == job_id), None)
                if not job:
                    print("Job not found in list")
                    continue
                status = job["status"]
                progress = job.get("progress", 0)
                print(f"  status={status} progress={progress}%")
                if status == "completed":
                    fp = job.get("filepath") or "N/A"
                    try:
                        print(f"SUCCESS. File: {fp}")
                    except UnicodeEncodeError:
                        print(f"SUCCESS. File: {fp.encode('ascii', 'replace').decode('ascii')}")
                    if job.get("filepath") and os.path.isfile(job["filepath"]):
                        print("File exists on disk.")
                    sys.exit(0)
                if status == "failed":
                    print("FAILED")
                    sys.exit(1)
                if status == "cancelled":
                    print("Cancelled")
                    sys.exit(1)


if __name__ == "__main__":
    main()
