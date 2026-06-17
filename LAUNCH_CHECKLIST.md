# Launch checklist — b2b-stickers

What stands between the current build and a real revenue launch.
**v1 revenue = the Stripe subscribe-and-save storefront (`apps/site`).** Marketplace (Amazon/eBay) is stubbed and is not v1.

## Revenue-blocking
- [ ] **Permanent public image URLs.** Product/mockup images are currently presigned S3 URLs that **expire after 7 days** (the shared POD bucket has Block-Public-Access ON). Storefront images will break after a week. Fix: serve the `b2b-stickers/` objects via CloudFront (OAC — bucket stays private) or a dedicated public bucket, then set `S3_PUBLIC_BASE_URL` on Railway. Code already honours it (`s3_storage.public_url`).
- [ ] **Lifestyle mockups populated.** Approving a design enqueues `composite_product_mockups`, which composites the sticker onto product backdrops. Backdrops must be generated once or `mockup_urls` stays empty. Verify approve → `mockup_urls` populated.
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
- [x] **Storage** reused from the POD AWS bucket (presigned URLs for now — see Revenue-blocking #1).
