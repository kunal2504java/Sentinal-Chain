# SentinelChain - AGENTS.md

## What This Project Is
SentinelChain is an AI-powered real-time surveillance system that detects critical events from live or recorded camera feeds and creates tamper-evident evidence using Avalanche blockchain, IPFS, SQLite, and a web dashboard.

This repository already contains a completed public landing page in `frontend/`. The operator dashboard was intentionally added into the same Next.js app under new routes instead of creating a separate frontend app.

Read this file before making changes.

## Current Repo Structure
```text
SentinalChain/
|- alerts/
|  \- telegram.py              # Telegram alert delivery
|- api/
|  |- __init__.py
|  \- main.py                  # FastAPI backend endpoints
|- chain/
|  |- EventLogger.sol          # Solidity smart contract
|  |- abi.json                 # Contract ABI
|  |- contract.py              # Avalanche logger client
|  |- ipfs.py                  # Pinata upload client
|  \- queue.py                 # SQLite-backed retry queue
|- core/
|  |- buffer.py                # Rolling video buffer
|  |- clipper.py               # MP4 clip extraction
|  |- detector.py              # YOLOv8 inference + suppression logic
|  \- hasher.py                # SHA-256 hashing
|- events/                     # Saved evidence clips
|- frontend/
|  |- app/
|  |  |- page.tsx              # Public landing page
|  |  |- signin/page.tsx       # Temporary operator sign-in
|  |  \- dashboard/page.tsx    # Operator dashboard route
|  |- components/
|  |  |- landing/              # Existing landing page components
|  |  |- dashboard/            # Dashboard UI components
|  |  \- auth/                 # Temporary auth helpers/components
|  \- package.json
|- tests/
|  |- test_detector.py
|  \- test_pipeline_integration.py
|- .env.example
|- config.py
|- deploy.py
|- pipeline.py
|- README.md
|- requirements.txt
\- agents.md
```

## Tech Stack
- Python 3.11+
- ultralytics (YOLOv8)
- opencv-python
- web3.py 6.x
- Pinata API
- FastAPI
- Next.js + React + Tailwind CSS
- Solidity 0.8.x
- SQLite
- Telegram Bot API

## Network Config
- Testnet RPC: `https://api.avax-test.network/ext/bc/C/rpc`
- Chain ID: `43113`
- Mainnet RPC: `https://api.avax.network/ext/bc/C/rpc`
- Mainnet Chain ID: `43114`

## Implementation Rules
- Every function should keep docstrings and type hints.
- Never hardcode secrets. Use environment variables only.
- Keep blockchain submission wrapped in fallback logic through the SQLite queue.
- Event flow is: detect -> clip -> hash -> IPFS -> chain -> alert -> SQLite record.
- Confidence threshold default is `0.75`.
- Frame confirmation default is `4 of 6` consecutive frames.
- Preserve the existing landing page code and design language.
- Add new frontend work inside the current `frontend/` app unless there is a strong reason not to.

## Frontend Rules
- Do not break or redesign the existing landing page.
- Keep new UI aligned with the existing visual language in `frontend/app/globals.css` and existing UI primitives.
- The dashboard lives inside the existing Next.js app, not in a separate `dashboard/` folder.
- Operator routes currently are:
  - `/signin`
  - `/dashboard`

## Temporary Auth Rule
- The dashboard is gated by a temporary client-side sign-in flow.
- Any valid 10-digit phone number is accepted.
- Any valid email address is accepted.
- The OTP is `123456`.
- This is demo-only behavior and should not be silently replaced with stricter auth unless requested.

## Current State
- Sprint 1 complete: detection pipeline, buffer, clip writer, hashing, detector tests.
- Sprint 2 complete: contract, ABI, deploy script, Avalanche logger, retry queue.
- Sprint 3 complete: Pinata upload flow, Telegram alerts, SQLite event persistence.
- Sprint 4 complete: FastAPI event endpoints and dashboard added into `frontend/`.
- Sprint 5 complete: RTSP reconnect behavior, FPS throttling, detector suppression controls, queue backoff, integration test.
- Sprint 6 complete: README, finalized `.env.example`, demo script, run instructions.

## Verification Status
- Python syntax checks pass.
- `tests/test_detector.py` passes.
- `tests/test_pipeline_integration.py` passes.
- Frontend TypeScript check passes.
- A full `next build` may still be sensitive to local Windows/Turbopack/workspace restrictions, so do not assume a build failure is automatically a code failure without checking the actual error.

## Environment Variables In Use
- `CAMERA_SOURCE`
- `CAMERA_ID`
- `CAMERA_LOCATION`
- `MODEL_PATH`
- `CONFIDENCE_THRESHOLD`
- `FRAME_CONFIRMATION_N`
- `FRAME_CONFIRMATION_M`
- `NMS_IOU_THRESHOLD`
- `MIN_BBOX_AREA`
- `IGNORE_ZONES`
- `BUFFER_SECONDS`
- `CLIP_BEFORE_SECONDS`
- `CLIP_AFTER_SECONDS`
- `EVENTS_DIR`
- `PRIVATE_KEY`
- `CONTRACT_ADDRESS`
- `RPC_URL`
- `CHAIN_ID`
- `PINATA_API_KEY`
- `PINATA_SECRET`
- `TELEGRAM_BOT_TOKEN`
- `TELEGRAM_CHAT_ID`
- `LOG_LEVEL`
- `SQLITE_PATH`
- `API_PORT`
- `NEXT_PUBLIC_API_BASE_URL`
- `RETRY_INTERVAL_SECONDS`
- `RECONNECT_INTERVAL_SECONDS`
- `PROCESS_FPS`

## Run Commands
- Deploy contract:
  - `python deploy.py`
- Run pipeline:
  - `python pipeline.py`
  - `python pipeline.py --source test_video.mp4 --fps 10`
- Run API:
  - `uvicorn api.main:app --host 0.0.0.0 --port 8000`
- Run frontend:
  - `cd frontend`
  - `pnpm dev`

## Current Priority
The MVP is built end-to-end. Future work should preserve the current landing page, keep dashboard work inside `frontend/`, and make changes in a way that does not regress the existing operator flow.
