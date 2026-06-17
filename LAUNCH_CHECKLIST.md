# Launch checklist — b2b-stickers

What stands between the current build and a real revenue launch.
**v1 revenue = the Stripe subscribe-and-save storefront (`apps/site`).** Marketplace (Amazon/eBay) is stubbed and is not v1.

## Revenue-blocking
- [ ] **Subscription flow tested end-to-end.** Stripe checkout → subscription created → recurring fulfillment. This is v1 revenue — must work before launch.
- [ ] **Replicate + Anthropic billing funded** for an illustration-scale run (text designs are free; illustrations ~$0.003–0.04 each + vision QA per design).

## Security (pre-launch)
- [ ] **Rotate the admin password.** `admin123` is hardcoded in committed `DEPLOYED.md`. Generate a new hash (`scripts/hash_password.py`), set `ADMIN_PASSWORD_HASH` on Railway, scrub it from `DEPLOYED.md`.
- [ ] **Remove `apps/api/cookies.txt` from git** (committed session cookie).
- [ ] **CORS origins.** Confirm `DASHBOARD_BASE_URL` and `SITE_BASE_URL` are the real prod URLs on Railway (misconfig = silent CORS failures from the frontends).
- [ ] **Stripe webhook secret.** `STRIPE_WEBHOOK_SECRET` matches the live endpoint signing secret.

## Done
- [x] **Spelling/grammar correct on text stickers** — text-primary designs (thank you, quotes, seals, etc.) rendered programmatically with a real font, bypassing the diffusion model. Guaranteed spelling, £0/design, varied palettes. Validated live (#1146–#1150, q82–92). See memory `text-designs-programmatic`.
- [x] **Claude vision gate** rejects garbled/leaked text on AI illustrations.
- [x] **Generation hub** — volume-weighted generation, SEO content, approval workflow.
- [x] **Lifestyle mockups** — approval composites the transparent die-cut sticker onto industry-matched product backdrops + a clean studio shot (`mockup_urls`). Validated live (#1149, #1151).
- [x] **Permanent public image URLs** — serving from a dedicated public S3 bucket. `S3_PUBLIC_BASE_URL` set on both Railway services; verified a generated object loads HTTP 200 with no expiry (#1152).

## Storage config (non-secret)
- Bucket: `b2b-stickers-assets` — AWS S3, region `eu-north-1`, public-read on `s3:GetObject` (policy in `infra/s3-bucket-policy.json`)
- Public base: `https://b2b-stickers-assets.s3.eu-north-1.amazonaws.com`
- Key prefix: `b2b-stickers` (`S3_KEY_PREFIX`); `S3_ENDPOINT_URL` unset (AWS S3, not R2)
- Railway vars on **both** `b2bLabels` + `fortunate-flow`: `S3_BUCKET`, `S3_PUBLIC_BASE_URL`, `AWS_REGION`, `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`
- Pre-#1152 products still point at the old bucket (expiring) — regenerate or treat as test data. Future: front with CloudFront to cut S3 egress.
