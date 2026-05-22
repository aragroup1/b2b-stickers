# B2B Stickers & Labels Print-on-Demand Platform

AI-powered print-on-demand platform for UK B2B buyers. Mass-generates sticker/label designs with AI, auto-lists on Amazon UK + eBay UK, and runs a Stripe-powered subscribe-and-save storefront.

## Quick Start

```bash
# 1. Install dependencies
pnpm install

# 2. Start infrastructure
docker-compose up -d postgres redis

# 3. Seed database
python scripts/seed_keywords.py

# 4. Start API
cd apps/api && uvicorn app.main:app --reload

# 5. Start workers
celery -A app.workers.celery_app worker --loglevel=info
celery -A app.workers.celery_app beat --loglevel=info

# 6. Start frontends
pnpm run dashboard:dev
pnpm run site:dev
```

## Structure

- `apps/api` — FastAPI backend
- `apps/dashboard` — Next.js admin dashboard
- `apps/site` — Next.js customer-facing subscribe-and-save storefront
- `packages/types` — Shared TypeScript types
- `packages/api-client` — Generated API client
- `packages/ui` — Shared shadcn/ui components

## Deployment

- **Vercel:** `apps/dashboard`, `apps/site`
- **Railway:** `apps/api` + Celery workers
- **Neon:** Postgres
- **Upstash:** Redis

## v1 Scope

See build spec for full details. Key surfaces:
1. Marketplace catalog (Amazon UK + eBay UK)
2. Subscribe-and-save storefront (Stripe subscriptions)
