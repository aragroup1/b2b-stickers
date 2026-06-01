# B2B Stickers — Deployment Status

## Deployed Services

| Service | URL | Status |
|---------|-----|--------|
| **Dashboard** | https://dashboard-delta-three-65.vercel.app | Live |
| **Site** | https://site-flame-xi-86.vercel.app | Live |
| **API** | https://positive-achievement-production-f5e4.up.railway.app | Online |
| **Old Dashboard** | https://dashboard-btqe9odbl-aras-projects-28d1fa5b.vercel.app | Blocked by Vercel SSO |
| **Old Site** | https://site-oqu6tej3b-aras-projects-28d1fa5b.vercel.app | Blocked by Vercel SSO |

## Quick Links

- **Customer Storefront**: https://site-flame-xi-86.vercel.app
- **Admin Dashboard**: https://dashboard-delta-three-65.vercel.app
- **API Base URL**: https://positive-achievement-production-f5e4.up.railway.app
- **API Health Check**: https://positive-achievement-production-f5e4.up.railway.app/health

## Admin Access

- **Dashboard URL**: https://dashboard-delta-three-65.vercel.app
- **Admin Password**: `admin123`

## Recent Fixes

### Fixed: Dashboard Client-Side Error (2026-06-01)
**Problem**: Dashboard showed "Application error: a client-side exception has occurred"
**Root cause**: Frontend was calling `/api/analytics/dashboard` but the API expected `/api/v1/analytics/dashboard`
**Fix**: Updated Next.js rewrite rules in both `apps/dashboard/next.config.js` and `apps/site/next.config.js` to proxy `/api/*` to `/api/v1/*` on the backend.

### Fixed: API Proxy Configuration
**Problem**: API_BASE_URL was pointing to old/incorrect URL
**Fix**: Updated Vercel environment variables for both dashboard and site projects.

## What's Working

- ✅ Site storefront is live and accessible
- ✅ Dashboard login page works (password: `admin123`)
- ✅ API is deployed and responding
- ✅ API proxy/rewrite is working correctly
- ✅ Admin authentication works

## What's Pending

### 1. Database Initialization (CRITICAL - BLOCKING DASHBOARD DATA)
The Postgres database is running but **not initialized**. The dashboard login works, but data pages (products, orders, customers) will be empty.

**To fix**:
```bash
cd apps/api
railway connect Postgres
# Then in psql, run:
\i ../../../scripts/init_db.sql
\i ../../../scripts/seed_industries.sql
\i ../../../scripts/seed_pricing_matrix.sql
\q

# Run migrations
railway run -- alembic upgrade head

# Seed demo data (optional)
railway run -- python scripts/seed_demo_products.py
```

### 2. Stripe Setup (REQUIRED FOR PAYMENTS)
Add your Stripe keys to process payments:
```bash
cd apps/api
railway variables set STRIPE_SECRET_KEY="sk_test_..."
railway variables set STRIPE_WEBHOOK_SECRET="whsec_..."
railway variables set STRIPE_PUBLISHABLE_KEY="pk_test_..."
railway variables set STRIPE_SUBSCRIPTION_PRODUCT_ID="prod_..."
```

### 3. Configure Stripe Webhooks
In Stripe Dashboard → Developers → Webhooks:
- Endpoint URL: `https://positive-achievement-production-f5e4.up.railway.app/api/v1/webhooks/stripe`
- Events: `checkout.session.completed`, `customer.subscription.updated`, `customer.subscription.deleted`, `invoice.paid`, `invoice.payment_failed`

## Architecture

```
Dashboard (Vercel)  ──▶  API (Railway)  ◄──  PostgreSQL (Railway)
     │                         │
Site (Vercel)       ◄─────────┘
                             │
                        Redis (Railway)
```

## GitHub Repository

https://github.com/aragroup1/b2b-stickers
