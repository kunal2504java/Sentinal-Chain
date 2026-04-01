SENTINELCHAIN
Complete Build Package
AI Surveillance × Avalanche Blockchain

Deliverables
6 Documents
Sprint Prompts
6 Sprints
Build Timeline
6 Weeks

CONFIDENTIAL  |  March 2026
1. What You Have & What's Left
You have completed the frontend. Here is the full picture of what remains to build the MVP end-to-end.

Layer
Status
What's Needed
Frontend (Next.js)
✅ Done
Content updates via Claude Code
AI Detection Engine
🔲 Sprint 1
detector.py, buffer.py, clipper.py, hasher.py
Smart Contract
🔲 Sprint 2
EventLogger.sol + deploy script
Blockchain Bridge
🔲 Sprint 2
web3.py contract.py + offline queue
IPFS Storage
🔲 Sprint 3
Pinata client + upload/verify
Alerts
🔲 Sprint 3
Telegram bot
Backend API
🔲 Sprint 4
FastAPI endpoints
Evidence Dashboard
🔲 Sprint 4
React event log + verify UI
Production Hardening
🔲 Sprint 5
RTSP, reconnect, false-positive suppression
Demo Package
🔲 Sprint 6
README, .env.example, demo script

2. Complete Project File Structure
Create this folder structure before starting Sprint 1. Every file Claude Code will build maps to a location below.

// sentinelchain/ — full tree
sentinelchain/
├── CLAUDE.md               ← Claude Code reads this automatically
├── PRD.md                  ← Product requirements
├── SPRINTS.md              ← Sprint prompts (this document)
├── .env.example            ← Environment variable template
├── .env                    ← Your actual secrets (git-ignored)
├── requirements.txt        ← Python dependencies
├── pipeline.py             ← Main entry point
├── config.py               ← All config from env vars
├── deploy.py               ← Contract deployment script
├── core/
│   ├── __init__.py
│   ├── detector.py         ← YOLOv8 inference
│   ├── buffer.py           ← Rolling frame buffer
│   ├── clipper.py          ← MP4 clip extraction
│   └── hasher.py           ← SHA-256 hashing
├── chain/
│   ├── __init__.py
│   ├── EventLogger.sol     ← Solidity smart contract
│   ├── abi.json            ← Contract ABI (generated)
│   ├── contract.py         ← web3.py interface
│   ├── ipfs.py             ← Pinata client
│   └── queue.py            ← Offline retry queue (SQLite)
├── alerts/
│   ├── __init__.py
│   └── telegram.py         ← Telegram bot alerts
├── api/
│   ├── __init__.py
│   └── main.py             ← FastAPI REST endpoints
├── dashboard/              ← React SPA
│   ├── src/
│   │   ├── App.jsx
│   │   ├── components/
│   │   │   ├── EventLog.jsx
│   │   │   ├── EventDetail.jsx
│   │   │   ├── StatsBar.jsx
│   │   │   ├── VerifyModal.jsx
│   │   │   └── ExportButton.jsx
│   │   └── main.jsx
│   ├── package.json
│   └── index.html
├── tests/
│   ├── test_detector.py
│   ├── test_hasher.py
│   ├── test_queue.py
│   ├── test_api.py
│   └── test_pipeline_integration.py
└── events/                 ← Saved clips (git-ignored)
    └── YYYY-MM-DD/
        └── event_type/
            └── ISO_timestamp.mp4

3. CLAUDE.md — The Master Instruction File
Why This Matters
CLAUDE.md sits in the project root and is read automatically by Claude Code at the start of every session. This is your most powerful configuration lever. Keep it updated — especially the 'Current Sprint' field — before each session.

Create this file at sentinelchain/CLAUDE.md with the following content:

// CLAUDE.md
# SentinelChain — CLAUDE.md

## What This Project Is
AI-powered real-time surveillance that detects events (fire, accidents, intrusion)
from live camera feeds and logs tamper-proof evidence on Avalanche blockchain.
Read PRD.md before writing any code. Read this file before every session.

## Tech Stack (NON-NEGOTIABLE)
- Python 3.11+
- ultralytics (YOLOv8) — detection engine
- opencv-python — video/stream handling
- web3.py 6.x — Avalanche C-Chain interaction
- Pinata API — IPFS uploads
- FastAPI — backend REST API
- React + TailwindCSS — dashboard
- Solidity 0.8.x — smart contracts
- SQLite — local event cache
- Telegram Bot API — alerts

## Project Structure
sentinelchain/
├── core/
│   ├── detector.py        # YOLOv8 inference engine
│   ├── buffer.py          # Rolling video buffer
│   ├── clipper.py         # Event clip extraction
│   └── hasher.py          # SHA-256 hashing
├── chain/
│   ├── contract.py        # web3.py Avalanche interface
│   ├── ipfs.py            # Pinata upload client
│   ├── queue.py           # Offline retry queue
│   └── EventLogger.sol    # Smart contract
├── alerts/
│   └── telegram.py        # Telegram bot
├── api/
│   └── main.py            # FastAPI endpoints
├── dashboard/             # React frontend
├── tests/
├── config.py              # All config via env vars
├── pipeline.py            # Main orchestration loop
├── CLAUDE.md              # THIS FILE
└── PRD.md

## Network Config
- Testnet RPC: https://api.avax-test.network/ext/bc/C/rpc
- Chain ID: 43113
- Mainnet RPC: https://api.avax.network/ext/bc/C/rpc
- Mainnet Chain ID: 43114

## Coding Rules
- Every function must have a docstring and type hints

(Full file content — copy the text block below into sentinelchain/CLAUDE.md)

# SentinelChain — CLAUDE.md

## What This Project Is
AI-powered real-time surveillance that detects events (fire, accidents, intrusion)
from live camera feeds and logs tamper-proof evidence on Avalanche blockchain.
Read PRD.md before writing any code. Read this file before every session.

## Tech Stack (NON-NEGOTIABLE)
- Python 3.11+
- ultralytics (YOLOv8) — detection engine
- opencv-python — video/stream handling
- web3.py 6.x — Avalanche C-Chain interaction
- Pinata API — IPFS uploads
- FastAPI — backend REST API
- React + TailwindCSS — dashboard
- Solidity 0.8.x — smart contracts
- SQLite — local event cache
- Telegram Bot API — alerts

## Project Structure
sentinelchain/
├── core/
│   ├── detector.py        # YOLOv8 inference engine
│   ├── buffer.py          # Rolling video buffer
│   ├── clipper.py         # Event clip extraction
│   └── hasher.py          # SHA-256 hashing
├── chain/
│   ├── contract.py        # web3.py Avalanche interface
│   ├── ipfs.py            # Pinata upload client
│   ├── queue.py           # Offline retry queue
│   └── EventLogger.sol    # Smart contract
├── alerts/
│   └── telegram.py        # Telegram bot
├── api/
│   └── main.py            # FastAPI endpoints
├── dashboard/             # React frontend
├── tests/
├── config.py              # All config via env vars
├── pipeline.py            # Main orchestration loop
├── CLAUDE.md              # THIS FILE
└── PRD.md

## Network Config
- Testnet RPC: https://api.avax-test.network/ext/bc/C/rpc
- Chain ID: 43113
- Mainnet RPC: https://api.avax.network/ext/bc/C/rpc
- Mainnet Chain ID: 43114

## Coding Rules
- Every function must have a docstring and type hints
- All blockchain calls must have try/except with SQLite queue fallback
- Never hardcode keys — use environment variables only
- Log every event to SQLite first, then attempt chain submission
- Confidence threshold default: 0.75 (configurable per event type)
- Frame confirmation: event must appear in 4 of 6 consecutive frames

## Current Sprint
[UPDATE THIS each sprint — see SPRINTS.md]

4. Environment Variables (.env.example)
Create this file at sentinelchain/.env.example. Copy it to .env and fill in real values. Never commit .env to git.

// .env.example
# ── Camera ──────────────────────────────────────────────────
CAMERA_SOURCE=0                    # 0=webcam, rtsp://ip/stream
CAMERA_ID=CAM_001                  # Human-readable ID
CAMERA_LOCATION=Building A, Gate 2 # Human-readable location

# ── AI Model ─────────────────────────────────────────────────
MODEL_PATH=yolov8n.pt              # nano for speed, yolov8s for accuracy
CONFIDENCE_THRESHOLD=0.75
FRAME_CONFIRMATION_N=4             # N of M frames must confirm
FRAME_CONFIRMATION_M=6

# ── Video Buffer ─────────────────────────────────────────────
BUFFER_SECONDS=60
CLIP_BEFORE_SECONDS=15
CLIP_AFTER_SECONDS=15
EVENTS_DIR=./events

# ── Avalanche ────────────────────────────────────────────────
PRIVATE_KEY=0x...                  # Wallet private key (KEEP SECRET)
CONTRACT_ADDRESS=0x...             # Deployed EventLogger address
RPC_URL=https://api.avax-test.network/ext/bc/C/rpc
CHAIN_ID=43113                     # 43113=Fuji testnet, 43114=mainnet

# ── IPFS / Pinata ────────────────────────────────────────────
PINATA_API_KEY=your_key_here
PINATA_SECRET=your_secret_here

# ── Alerts ───────────────────────────────────────────────────
TELEGRAM_BOT_TOKEN=123456:ABC-DEF
TELEGRAM_CHAT_ID=-100123456789     # Group chat ID (negative)

# ── App ──────────────────────────────────────────────────────
LOG_LEVEL=INFO
API_PORT=8000
SQLITE_PATH=./sentinelchain.db

5. requirements.txt

// requirements.txt
# AI & Video
ultralytics>=8.0.0
opencv-python>=4.8.0
numpy>=1.24.0

# Blockchain
web3>=6.0.0
python-dotenv>=1.0.0

# API
fastapi>=0.104.0
uvicorn>=0.24.0
python-multipart>=0.0.6

# Alerts
python-telegram-bot>=20.0

# Storage
requests>=2.31.0

# Testing
pytest>=7.4.0
pytest-asyncio>=0.21.0
httpx>=0.25.0

6. Smart Contract Specification
Legal Note
The contract is intentionally immutable — no proxy, no upgradeability. This is a feature not a bug. Immutability is what makes blockchain timestamps legally trustworthy. If you need to fix a bug, deploy a new contract and migrate.

6.1 EventLogger.sol — Full Spec

Field
Solidity Type
Notes
eventType
string
'fire_smoke', 'person_down', 'intrusion'
timestamp
uint256
Set by block.timestamp — network-verified time
cameraId
string
Operator-assigned camera identifier
location
string
Human-readable location string
clipHash
string
SHA-256 hex of raw video clip
ipfsCid
string
IPFS Content Identifier from Pinata
confidence
uint256
AI score x100 (e.g., 94 = 94%)
reportedBy
address
msg.sender — operator wallet address

6.2 Evidence Verification Flow
This is the step-by-step process for verifying evidence in court or with law enforcement:

Download the video clip from IPFS using the stored CID
Compute its SHA-256 hash locally (any standard tool works)
Compare with the clipHash stored in the Avalanche event record
If they match: the clip is provably unaltered since it was logged
The block.timestamp is the court-admissible detection time
The Avalanche transaction is publicly verifiable by any third party

Verification Command
sha256sum evidence_clip.mp4  →  compare output to on-chain clipHash

7. Sprint Prompts for Claude Code
Use these prompts verbatim. One sprint at a time. Update CLAUDE.md 'Current Sprint' before each session.

Golden Rule
Never ask Claude Code to build everything at once. Each sprint prompt builds on the last and explicitly protects completed work by saying 'do not modify Sprint N files'.

Sprint 1 — Detection Pipeline (Week 1)
Goal: Working AI detection with clip extraction. No blockchain yet.

PASTE THIS INTO CLAUDE CODE:
Build Sprint 1: the core detection pipeline. Build ONLY these files:
  core/detector.py
  core/buffer.py
  core/clipper.py
  core/hasher.py
  pipeline.py
  config.py
  tests/test_detector.py

### core/detector.py
YOLOv8 wrapper class with:
- Configurable model path and confidence threshold (default 0.75)
- Support for event types: fire_smoke, person_down, intrusion
- Consecutive frame confirmation: event must appear in 4 of 6 frames
  before triggering (use a sliding window deque)
- Returns Event dataclass: type, confidence, timestamp (UTC ISO),
  frame_snapshot (numpy array), camera_id

### core/buffer.py
RollingBuffer class:
- collections.deque with maxlen = fps * buffer_seconds (default 60s)
- push_frame(frame, timestamp) method
- get_clip(seconds_before, seconds_after, event_timestamp) method
  returns list of (frame, timestamp) tuples

### core/clipper.py
ClipWriter class:
- Takes frame list from buffer, writes to MP4 using cv2.VideoWriter
- Saves to: events/{YYYY-MM-DD}/{event_type}/{ISO_timestamp}.mp4
- Returns absolute path of saved clip
- Creates directories if they don't exist

### core/hasher.py
Single function: hash_file(filepath: str) -> str
- SHA-256 hash of file at path
- Reads in 8192 byte chunks
- Returns lowercase hex string

### config.py
Load all config from environment variables with sensible defaults:
- CAMERA_SOURCE (default: 0 for webcam, supports rtsp:// URLs)
- MODEL_PATH (default: yolov8n.pt)
- CONFIDENCE_THRESHOLD (default: 0.75)
- BUFFER_SECONDS (default: 60)
- CLIP_BEFORE_SECONDS (default: 15)
- CLIP_AFTER_SECONDS (default: 15)
- EVENTS_DIR (default: ./events)
- LOG_LEVEL (default: INFO)

### pipeline.py
Main loop (not async for MVP):
- Initialize RollingBuffer and Detector
- Open video source with cv2.VideoCapture
- For each frame: push to buffer, run detection
- On event trigger: extract clip, hash it, print event summary
- Graceful shutdown on KeyboardInterrupt
- Accept --source flag to override CAMERA_SOURCE

### tests/test_detector.py
- Test Event dataclass creation
- Test consecutive frame confirmation logic (mock frames)
- Test confidence threshold filtering
- Use pytest, no real model needed (mock YOLOv8 results)

Do not touch chain/, alerts/, api/, or dashboard/. Do not install
anything not in requirements.txt. After building, run the tests

Sprint 2 — Blockchain Integration (Week 2)
Goal: Events logged on Avalanche Fuji testnet. Smart contract deployed.

and confirm they pass before stopping.

---

## SPRINT 2 — Blockchain Integration

Read CLAUDE.md. Sprint 1 is complete. Do not modify any Sprint 1 files
unless fixing a bug I explicitly describe.

Build Sprint 2: blockchain logging. Build ONLY:
  chain/EventLogger.sol
  chain/contract.py
  chain/queue.py
  chain/abi.json (generate from contract)

### chain/EventLogger.sol
Solidity ^0.8.0 contract:
- Struct Event { eventType, timestamp, cameraId, location,
  clipHash, ipfsCid, confidence (uint256 x100), reportedBy (address) }
- mapping(uint256 => Event) public events
- uint256 public eventCount
- address public owner
- constructor sets owner = msg.sender
- logEvent() — only callable by owner
  params: eventType, cameraId, location, clipHash, ipfsCid, confidence
  sets timestamp = block.timestamp internally
  increments eventCount, emits EventLogged
- getEvent(uint256 id) public view returns (Event memory)
- event EventLogged(uint256 indexed id, string eventType,
  uint256 timestamp, string clipHash)
- Contract must be immutable — no upgradeability, no proxy

### chain/contract.py
AvalancheLogger class:
- __init__: connect to RPC (from config), load contract from ABI file,
  load wallet from PRIVATE_KEY env var
- log_event(event: Event, clip_hash: str, ipfs_cid: str) -> str
  returns tx_hash hex string
  tries chain first, on any exception calls queue.add_to_queue()
  and returns "queued:{local_id}"
- verify_event(event_id: int) -> dict
  fetches on-chain record and returns as dict
- get_explorer_url(tx_hash: str) -> str
  returns Fuji testnet explorer URL

### chain/queue.py
SQLite-backed retry queue:
- SQLite table: pending_events (id, event_json, clip_hash,
  ipfs_cid, created_at, attempts, last_attempt)
- add_to_queue(event, clip_hash, ipfs_cid)
- get_pending() -> list of queued events
- mark_submitted(id, tx_hash)
- retry_pending(logger: AvalancheLogger) — tries all pending,
  marks successful ones as submitted
  Call this on pipeline startup and every 60 seconds

After building: deploy EventLogger.sol to Fuji testnet using
web3.py (write a deploy.py script), save the deployed address
to .env as CONTRACT_ADDRESS, generate chain/abi.json.
Print the Fuji explorer link to the deployed contract.

Sprint 3 — IPFS + Alerts (Week 3)
Goal: Clips on IPFS, Telegram alerts firing, SQLite events table populated.


---

## SPRINT 3 — IPFS + Alerts

Read CLAUDE.md. Sprints 1 and 2 are complete and working.
Do not modify Sprint 1 or 2 files unless fixing a bug I describe.

Build Sprint 3: IPFS storage and Telegram alerts. Build ONLY:
  chain/ipfs.py
  alerts/telegram.py
  Update pipeline.py to call IPFS and alerts after clip is saved

### chain/ipfs.py
PinataClient class:
- __init__: load PINATA_API_KEY and PINATA_SECRET from env
- upload_clip(filepath: str, metadata: dict) -> str
  uploads file to Pinata, returns IPFS CID
  metadata dict includes event_type, timestamp, camera_id
  raises exception if upload fails (do not silently swallow)
- get_ipfs_url(cid: str) -> str
  returns "https://gateway.pinata.cloud/ipfs/{cid}"
- verify_upload(cid: str) -> bool
  pings the gateway to confirm clip is accessible

### alerts/telegram.py
TelegramAlerter class:
- __init__: load TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID from env
- send_event_alert(event: Event, tx_hash: str, ipfs_url: str,
  clip_path: str) async method
  Message format:
  🚨 {EVENT_TYPE} DETECTED
  📍 Camera: {camera_id}
  🕐 Time: {timestamp}
  🎯 Confidence: {confidence}%
  🔗 Avalanche TX: {explorer_url}
  📹 Evidence: {ipfs_url}
- send_snapshot(chat_id, image_bytes) — sends the frame snapshot
- Gracefully skip (log warning) if TOKEN not configured

### Update pipeline.py
After clip is extracted and hashed:
1. Upload to IPFS → get CID
2. Log to Avalanche → get tx_hash  
3. Send Telegram alert with tx_hash and IPFS url
4. Log full event record to SQLite events table

Add SQLite events table (separate from queue):
  id, event_type, camera_id, timestamp, clip_path, clip_hash,
  ipfs_cid, tx_hash, confidence, created_at

---

## SPRINT 4 — Dashboard


Sprint 4 — Dashboard (Week 4)
Goal: Web dashboard showing event log with verify and export.

Read CLAUDE.md. Sprints 1–3 are complete.
Do not modify any previous sprint files unless fixing a described bug.

Build Sprint 4: web dashboard. Build ONLY the dashboard/ directory
and api/main.py.

### api/main.py
FastAPI app:
GET  /api/events          — list events, supports ?limit=50&offset=0
GET  /api/events/{id}     — single event detail
GET  /api/events/{id}/verify — re-hash clip, compare to on-chain hash,
                               return {match: bool, on_chain_hash, local_hash}
GET  /api/stats           — {total_events, events_today, integrity_rate}
POST /api/events/{id}/export — returns ZIP: clip + manifest.json + proof.txt
     manifest.json contains all metadata
     proof.txt contains: chain TX, IPFS CID, hash, verification instructions
GET  /health              — {status: ok}
CORS: allow localhost:3000

### dashboard/
React + TailwindCSS SPA (single index.html if simple,
or Vite React app if complex):

Components needed:
- EventLog: table of all events, columns: timestamp, type, camera,
  confidence (%), IPFS link, Avalanche TX link, Verify button
- EventDetail: full detail view for a single event
- StatsBar: total events, integrity rate, events today
- VerifyModal: shows hash comparison result with green/red indicator
- ExportButton: triggers ZIP download

Data polling: refresh EventLog every 10 seconds
On Verify click: call /api/events/{id}/verify, show modal with result
If hashes match: green checkmark + "Evidence is intact"
If hashes differ: red warning + "WARNING: Evidence may be compromised"

---

## SPRINT 5 — Live Camera + Hardening

Read CLAUDE.md. Sprints 1–4 are complete.

Build Sprint 5: production hardening. Update existing files only:

1. pipeline.py: Add RTSP stream support with reconnect logic
   - If cv2.VideoCapture fails, retry every 30 seconds
   - Log disconnect/reconnect events to SQLite
   - Add --fps flag to control processing rate (default: skip to 10fps)

2. core/detector.py: Add false positive suppression
   - Add NMS (non-max suppression) parameter
   - Add minimum bounding box size filter (ignore tiny detections)
   - Add ignore_zones config: list of polygons to exclude from detection
     (e.g., a TV screen that shows fire-like images)

3. chain/queue.py: Add exponential backoff
   - Retry delays: 30s, 60s, 120s, 300s, then every 300s
   - Max attempts: 20, then mark as failed and alert operator

4. config.py: Add all new config options with defaults

Sprint 5 — Live Camera + Hardening (Week 5)
Goal: RTSP streams, reconnect logic, false-positive suppression, integration tests.


5. Write integration test: tests/test_pipeline_integration.py
   - Uses a sample video file (tests/fixtures/sample_fire.mp4)
   - Runs full pipeline end-to-end with mocked chain/IPFS
   - Verifies clip is saved, hashed, and event is in SQLite

---

## SPRINT 6 — Testnet Demo

Read CLAUDE.md. All previous sprints complete.

Prepare Sprint 6: demo-ready build.

1. Write README.md:
   - What SentinelChain is (2 paragraphs)
   - Prerequisites
   - Installation (pip install -r requirements.txt)
   - .env setup (copy .env.example, fill in values)
   - Deploy contract (python deploy.py)
   - Run pipeline (python pipeline.py --source test_video.mp4)
   - Run dashboard (cd dashboard && npm start)
   - How to verify evidence (step by step)

2. Write .env.example with all required variables and comments

3. Write scripts/demo.sh:
   - Downloads a sample fire video from a public URL
   - Runs pipeline against it
   - Opens dashboard in browser
   - Prints first event's Avalanche explorer URL

4. Final check: run all tests, confirm zero failures
   Print a summary of what was built.

Sprint 6 — Demo Package (Week 6)
Goal: README, demo script, all tests passing. Ready to show stakeholders.


8. Debugging Prompts
When things break, use these templates. Constraint-first debugging saves enormous time.

8.1 When Code Breaks
// debug-template.txt
This error occurred when running [filename]:

[PASTE FULL STACK TRACE HERE]

The issue is in [filename] around line [N].
Fix only that file.
Do not change [file1.py], [file2.py], or any other file.
Do not refactor anything. Just fix the specific error.

8.2 When Claude Starts Refactoring
// stop-refactoring.txt
Stop.
You changed [filename] which is a Sprint [N] file.
Sprint [N] files are locked — do not modify them.
Revert your last change to [filename].
Only fix the specific issue in [target file].

8.3 When Blockchain TX Fails
// blockchain-debug.txt
The Avalanche transaction is failing with:
[ERROR MESSAGE]

Check in this order:
1. Is the wallet funded with test AVAX? (Fuji faucet: faucet.avax.network)
2. Is CONTRACT_ADDRESS set correctly in .env?
3. Is the private key the same wallet that deployed the contract?
4. Is RPC_URL pointing to Fuji (chain ID 43113)?

Fix only chain/contract.py. Do not touch other files.

8.4 Starting a New Session
// new-session.txt
Read CLAUDE.md.
We are on Sprint [N].

Files completed so far:
- [list completed files]

Those files work correctly. Do not modify them.

Continue from where we left off.
The next thing to build is [specific file or function].

9. External Services Setup Checklist
Complete these before Sprint 2. Each takes 10–20 minutes.

Service
What to Do
Where
Avalanche Wallet
Create wallet, save private key
core.app.avax.network
Fuji Test AVAX
Get test tokens from faucet
faucet.avax.network
Pinata
Create account, generate API key
pinata.cloud
Telegram Bot
Message @BotFather, create bot, get token
t.me/BotFather
Telegram Chat ID
Add bot to group, get group chat ID
t.me/userinfobot
Test Video
Download fire/accident sample for testing
Roboflow Universe

10. Evidence Verification Guide
This is the document to share with law enforcement or courts explaining how to verify SentinelChain evidence independently.

For Law Enforcement / Courts
The following steps allow any third party to verify that a SentinelChain video clip is authentic and unaltered, without relying on any central authority or trusting SentinelChain itself.

Step 1 — Obtain the Evidence Package
The operator exports a ZIP containing: the video clip (.mp4), the evidence manifest (manifest.json), and the blockchain proof (proof.txt).

Step 2 — Verify the Video Clip Hash
On any computer with standard tools:
// verify.sh
# On Linux/Mac:
sha256sum evidence_clip.mp4

# On Windows:
certutil -hashfile evidence_clip.mp4 SHA256

# The output must exactly match the 'clipHash' field
# in manifest.json and in the Avalanche transaction.

Step 3 — Verify the Blockchain Record
Open the Avalanche explorer URL from proof.txt in any web browser:
// explorer-url.txt
# Testnet:
https://testnet.snowtrace.io/tx/0x[TX_HASH]

# Mainnet:
https://snowtrace.io/tx/0x[TX_HASH]

# The transaction shows:
# - Block timestamp (detection time — set by Avalanche network)
# - clipHash (must match Step 2 output)
# - eventType, cameraId, location, confidence

Step 4 — Verify the IPFS Copy
The clip stored on IPFS is content-addressed — its address is its hash. Accessing the IPFS URL independently confirms the clip has not been altered.
// ipfs-verify.txt
https://gateway.pinata.cloud/ipfs/[CID]

# The CID (Content Identifier) is derived from the clip's hash.
# If the clip were modified, the CID would change.
# This means the IPFS address itself is a second proof of integrity.

Legal Summary
Three independent proofs converge: (1) The SHA-256 hash of the physical clip file. (2) The same hash stored immutably on a public blockchain with a network-verified timestamp. (3) The clip stored on IPFS where the storage address is derived from the hash. All three must agree. If they do, the evidence is intact.

11. Quick Reference Card

Command
What It Does
python pipeline.py
Run detection on default camera (webcam)
python pipeline.py --source rtsp://ip
Run on IP camera stream
python pipeline.py --source video.mp4
Run on video file (for testing)
python deploy.py
Deploy EventLogger.sol to Fuji testnet
uvicorn api.main:app --port 8000
Start FastAPI backend
cd dashboard && npm start
Start React dashboard
pytest tests/
Run all tests
python -c "from chain.queue import retry_pending"
Retry failed chain submissions

URL / Resource
Purpose
faucet.avax.network
Get free Fuji testnet AVAX
testnet.snowtrace.io
Fuji blockchain explorer
snowtrace.io
Mainnet blockchain explorer
gateway.pinata.cloud/ipfs/{CID}
View IPFS-stored clip
localhost:8000/docs
FastAPI auto-generated docs (Swagger)
localhost:3000
React evidence dashboard
docs.avax.network
Avalanche developer docs
docs.pinata.cloud
Pinata IPFS API docs

SentinelChain Build Package v1.0  |  CONFIDENTIAL  |  March 2026
