# Plan2Takeoff V2 — 1-Link Zero-Touch Integration Guide

No starter prompt copying required! The system prompt instructions are embedded directly at the top of the manifest link itself.

---

## 🌐 The Single Link for Claude Web

Simply send this single URL to **Claude Web**:

👉 **`https://rude-wasp-82.loca.lt/api/v1/manifest`**

---

## ⚡ How It Works

1. When Claude Web opens **`https://rude-wasp-82.loca.lt/api/v1/manifest`**, the **very first field** it reads is `START_HERE_PROMPT_INSTRUCTION`.
2. The prompt automatically instructs Claude Web to:
   - Read `00_INSTRUCTIONS_FOR_WEB_AI.md`, `tech_spec_v2.md`, and `log.md`.
   - Adhere to the 13 trade divisions (`UY_Louis.xlsx`) and Fajardo formulas.
   - Enforce strict V1 isolation (never touch V1 database or cloud storage).
   - Post code updates directly to `POST https://rude-wasp-82.loca.lt/api/v1/agent-sync` (Token: `p2t_v2_agent_relay_token_9981`).
3. Your local server automatically writes code, commits to Git, and prepends to `log.md`.

**True 1-Link Zero-Touch Setup!**
