# SentinelChain

SentinelChain is an AI-powered surveillance pipeline that detects critical incidents from live or recorded camera feeds and produces tamper-evident evidence packages. When an event is confirmed, SentinelChain extracts a clip, hashes it, uploads it to IPFS, and records the proof trail against Avalanche so the evidence can be independently verified later.

This repository contains the full MVP stack: the public landing page and operator dashboard in `frontend/`, the Python detection pipeline at the repo root, Avalanche contract integration in `chain/`, alerting in `alerts/`, and a FastAPI backend in `api/`. The dashboard is mounted inside the existing Next.js app at `/dashboard`, while the public marketing page remains at `/`.

## Prerequisites

- Python 3.11+
- Node.js 20+ and a package manager compatible with the existing `frontend/pnpm-lock.yaml`
- An Avalanche wallet funded with Fuji testnet AVAX
- Pinata API credentials
- A Telegram bot token and target chat ID
- A YOLO model file such as `yolov8n.pt`

## Installation

Install the Python backend dependencies:

```bash
pip install -r requirements.txt
```

Install the frontend dependencies:

```bash
cd frontend
pnpm install
```

## Environment Setup

Copy the environment template and fill in your real values:

```bash
cp .env.example .env
```

At minimum, set:

- `PRIVATE_KEY`
- `CONTRACT_ADDRESS` after deployment
- `PINATA_API_KEY`
- `PINATA_SECRET`
- `TELEGRAM_BOT_TOKEN`
- `TELEGRAM_CHAT_ID`
- `NEXT_PUBLIC_API_BASE_URL`

## Deploy Contract

Deploy the immutable `EventLogger` contract to Avalanche Fuji:

```bash
python deploy.py
```

After deployment, copy the printed address into `.env` as `CONTRACT_ADDRESS`.

## Run Pipeline

Use the default camera:

```bash
python pipeline.py
```

Run against an RTSP stream:

```bash
python pipeline.py --source rtsp://ip
```

Run against a local video file:

```bash
python pipeline.py --source test_video.mp4
```

You can also limit processing rate:

```bash
python pipeline.py --source test_video.mp4 --fps 10
```

## Run Backend API

Start the FastAPI server:

```bash
uvicorn api.main:app --host 0.0.0.0 --port 8000
```

Swagger docs will be available at `http://localhost:8000/docs`.

## Run Frontend

Start the existing Next.js frontend:

```bash
cd frontend
pnpm dev
```

Routes:

- `http://localhost:3000/` for the landing page
- `http://localhost:3000/signin` for the temporary operator sign-in
- `http://localhost:3000/dashboard` for the evidence dashboard

Current temporary access rule:

- any valid 10-digit phone number works
- any valid email works
- the OTP is `123456`

## How To Verify Evidence

1. Open the dashboard and select an event.
2. Use the `Verify` action to re-hash the local clip and compare it against the on-chain hash.
3. Use the `Export` action to download the evidence ZIP containing the clip, `manifest.json`, and `proof.txt`.
4. Independently compute the SHA-256 of the exported clip:

```bash
sha256sum evidence_clip.mp4
```

On Windows:

```powershell
certutil -hashfile evidence_clip.mp4 SHA256
```

5. Confirm that the local hash, manifest hash, and Avalanche record match.
6. Confirm that the IPFS CID in the exported proof resolves to the same clip content.

## Tests

Run the available tests:

```bash
pytest tests/
```

Notes:

- In this environment, `tests/test_detector.py` passes.
- `tests/test_pipeline_integration.py` may skip if the installed OpenCV build is incompatible with the installed NumPy version.

## Project Layout

```text
alerts/     Telegram alerting
api/        FastAPI endpoints
chain/      Solidity contract, ABI, chain client, retry queue, IPFS client
core/       Detection, buffering, clip writing, hashing
events/     Saved evidence clips
frontend/   Landing page + sign-in + dashboard
tests/      Detector and integration tests
```
