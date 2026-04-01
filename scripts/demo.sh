#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SAMPLE_URL="https://github.com/intel-iot-devkit/sample-videos/raw/master/fire-detection.mp4"
SAMPLE_VIDEO="$ROOT_DIR/test_video.mp4"

echo "Downloading sample fire video..."
curl -L "$SAMPLE_URL" -o "$SAMPLE_VIDEO"

echo "Starting FastAPI backend..."
cd "$ROOT_DIR"
python -m uvicorn api.main:app --host 0.0.0.0 --port 8000 &
API_PID=$!

echo "Starting Next.js frontend..."
cd "$ROOT_DIR/frontend"
pnpm dev &
FRONTEND_PID=$!

cleanup() {
  kill "$API_PID" "$FRONTEND_PID" 2>/dev/null || true
}
trap cleanup EXIT

cd "$ROOT_DIR"
echo "Running detection pipeline against sample video..."
python pipeline.py --source "$SAMPLE_VIDEO" --fps 10

echo "Dashboard: http://localhost:3000/dashboard"
echo "Landing page: http://localhost:3000/"

python - <<'PY'
import sqlite3

connection = sqlite3.connect("sentinelchain.db")
row = connection.execute(
    "SELECT tx_hash FROM events ORDER BY id DESC LIMIT 1"
).fetchone()
connection.close()

if row and row[0] and row[0] not in {"not-submitted"} and not row[0].startswith("queued:"):
    print(f"First event Avalanche explorer URL: https://testnet.snowtrace.io/tx/{row[0]}")
else:
    print("No confirmed on-chain transaction found for the latest event.")
PY
