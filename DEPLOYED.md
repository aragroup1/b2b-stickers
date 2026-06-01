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

## Recent Fixes (2026-06-01)

### Fixed: Dashboard Client-Side Crash
**Problem**: "Application error: Cannot read properties of undefined (reading 'total')"
**Root cause**: Frontend called `/api/analytics/dashboard` but API expected `/api/v1/analytics/dashboard`
**Fix**: Updated Next.js rewrite rules to proxy `/api/*` → `/api/v1/*`

### Fixed: Database Connection
**Problem**: API couldn't connect to PostgreSQL
**Fix**: Deployed new Postgres instance, initialized schema, seeded demo data

### Fixed: Demo Product Seeder
**Problem**: `TypeError: expected str, got dict` when seeding metadata
**Fix**: Added `json.dumps()` to convert dict to JSON string

## What's Working

- ✅ Site storefront is live
- ✅ Dashboard login works (password: `admin123`)
- ✅ API is deployed and responding
- ✅ Database initialized with 20 demo products
- ✅ Dashboard shows product analytics (20 products, 20 trends)

## What's Pending

### 1. Stripe Setup (REQUIRED FOR PAYMENTS)
Add your Stripe keys to process payments:
```bash
cd apps/api
railway variables set STRIPE_SECRET_KEY="sk_test_..."
railway variables set STRIPE_WEBHOOK_SECRET="whsec_..."
railway variables set STRIPE_PUBLISHABLE_KEY="pk_test_..."
railway variables set STRIPE_SUBSCRIPTION_PRODUCT_ID="prod_..."
```

### 2. Configure Stripe Webhooks
In Stripe Dashboard → Developers → Webhooks:
- Endpoint URL: `https://positive-achievement-production-f5e4.up.railway.app/api/v1/webhooks/stripe`
- Events: `checkout.session.completed`, `customer.subscription.updated`, `customer.subscription.deleted`, `invoice.paid`, `invoice.payment_failed`

### 3. Set Up Custom Domain (OPTIONAL)
- Add custom domain in Vercel for both site and dashboard
- Update `SITE_BASE_URL` and `DASHBOARD_BASE_URL` in Railway

### 4. Generate Real Products (OPTIONAL)
The demo products are placeholder data. To generate real AI products:
1. Log into dashboard
2. Go to Industries page
3. Use the product generation tools

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
