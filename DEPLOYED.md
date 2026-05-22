# B2B Stickers — Deployment Status

## Deployed Services

| Service | URL | Status |
|---------|-----|--------|
| **Dashboard** | https://dashboard-btqe9odbl-aras-projects-28d1fa5b.vercel.app | Live |
| **Site** | https://site-oqu6tej3b-aras-projects-28d1fa5b.vercel.app | Live |
| **API** | *Needs Railway deployment* | Not deployed |

## GitHub Repository

https://github.com/aragroup1/b2b-stickers

## What's Working

- Dashboard login page is live
- Site storefront is live
- Both builds pass TypeScript checks
- GitHub repo is set up with CI/CD

## What You Need To Do Next

### 1. Deploy API to Railway (5 minutes)

```bash
# Install Railway CLI
npm install -g @railway/cli

# Login
railway login

# Create project from GitHub repo
cd apps/api
railway init
# Select "Deploy from GitHub repo"
# Choose: aragroup1/b2b-stickers
# Set root directory: apps/api

# Add databases
railway add --database postgres
railway add --database redis

# Set environment variables
railway variables set JWT_SECRET="$(openssl rand -hex 32)"
railway variables set ADMIN_PASSWORD_HASH="$(python ../scripts/hash_password.py 'your-password' | grep '\$2b\$')"
railway variables set STRIPE_SECRET_KEY="sk_test_..."
railway variables set STRIPE_WEBHOOK_SECRET="whsec_..."
railway variables set STRIPE_PUBLISHABLE_KEY="pk_test_..."
railway variables set ENV="production"
railway variables set API_BASE_URL="https://your-api.up.railway.app"
railway variables set SITE_BASE_URL="https://site-oqu6tej3b-aras-projects-28d1fa5b.vercel.app"
railway variables set DASHBOARD_BASE_URL="https://dashboard-btqe9odbl-aras-projects-28d1fa5b.vercel.app"

# Deploy
railway up

# Get API URL
railway domain
```

### 2. Initialize Database

```bash
# Connect to Postgres
railway connect postgres

# Run in psql:
\i ../../../scripts/init_db.sql
\i ../../../scripts/seed_industries.sql
\i ../../../scripts/seed_pricing_matrix.sql
\q

# Run migrations
railway run -- alembic upgrade head
```

### 3. Configure Stripe Webhooks

In Stripe Dashboard → Developers → Webhooks:
- Endpoint URL: `https://your-api.up.railway.app/api/v1/webhooks/stripe`
- Events: `checkout.session.completed`, `customer.subscription.updated`, `customer.subscription.deleted`, `invoice.paid`, `invoice.payment_failed`

### 4. Update Vercel Environment Variables

In Vercel Dashboard for both projects, set:
```
API_BASE_URL=https://your-api.up.railway.app
```

## Architecture

```
Dashboard (Vercel)  ──▶  API (Railway)  ◄──  PostgreSQL (Railway)
     │                         │
Site (Vercel)       ◄─────────┘
                             │
                        Redis (Railway)
```
