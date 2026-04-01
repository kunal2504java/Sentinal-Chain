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
