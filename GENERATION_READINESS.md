# Generation Readiness

Status of the pipeline that turns AI generation into sellable, SEO-ready, imaged products.
Last updated 2026-06-14.

## ⛔ Blockers before a real batch
- [ ] **Image storage (R2/S3)** — *your action*: create a Cloudflare R2 bucket + API token, then set these on Railway (web **and** worker): `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `AWS_REGION=auto`, `S3_BUCKET`, `S3_ENDPOINT_URL`, `S3_PUBLIC_BASE_URL`. Code is ready. Without it, generated images expire (~daily).
- [ ] **Worker running** — `railway up -s fortunate-flow` (parked to save cost). Needed during generate + approve. `railway down -s fortunate-flow -y` afterwards.

## ✅ Done
- [x] **Replicate** — connected, token valid (web + worker).
- [x] **Persistent storage code** — R2/S3 endpoints + permanent public URLs (replaces the expiring-URL bug).
- [x] **SEO content** — title/description/tags auto-generated at creation (deterministic, free; `app/core/listings/seo_content.py`).
- [x] **Approval / rejection** — `/api/v1/approval/*` (approve, reject, auto-approve-by-quality); approved → storefront catalog.
- [x] **Priced variants** — size × pack with retail + subscribe-and-save pricing.

## 🧩 Built (code complete) — activates once R2 is live
- [x] **Lifestyle Tier 1 (composite):** on approval, composites the sticker onto industry-relevant AI-generated backdrops + a clean shot → R2 (`composite_product_mockups`). Backdrops auto-generate on first approval. No-ops gracefully until R2 is configured.
- [x] **Lifestyle Tier 2 (AI for winners):** wired stub (`generate_winner_lifestyle`) — deferred until Stripe + real sales data exist.

## ⏭️ Later (not generation-blocking)
- [ ] **Stripe** — to actually take money (separate from generation).
- [ ] **One-time "Buy Once" fulfillment bug** + webhook idempotency.

## ▶️ How to run a batch (once unblocked)
1. `railway up -s fortunate-flow` (worker up).
2. Dashboard → Generate, or `POST /api/v1/generation/batch` / `/generation/volume-weighted`.
3. Review in the approval queue → approve/reject.
4. Approved products appear on the storefront, SEO + priced.
5. `railway down -s fortunate-flow -y` (worker down to save cost).
