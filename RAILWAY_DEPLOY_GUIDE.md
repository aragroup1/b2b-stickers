# B2B Stickers — Railway Deployment Guide

## Overview

This guide covers deploying the B2B Stickers platform to Railway.

**Architecture:**
- **API + Workers** → Railway (Docker)
- **Dashboard** → Vercel (Next.js)
- **Site** → Vercel (Next.js)
- **Database** → Neon / Railway Postgres
- **Redis** → Railway Redis / Upstash
- **Storage** → AWS S3 / Cloudflare R2

---

## 1. Prerequisites

- Railway CLI installed: `npm install -g @railway/cli`
- Railway account connected: `railway login`
- Stripe account with products configured
- Resend account for emails
- (Optional) Replicate account for AI generation
- (Optional) AWS S3 bucket for image storage

---

## 2. Create Railway Project

```bash
# Create project
railway init --name b2b-stickers

# Add services
railway add --database postgres
railway add --database redis
```

---

## 3. Environment Variables

Set these in Railway Dashboard → Variables:

### Required (Application won't start without these)

```env
# Database (auto-populated by Railway Postgres)
DATABASE_URL=${{Postgres.DATABASE_URL}}

# Redis (auto-populated by Railway Redis)
REDIS_URL=${{Redis.REDIS_URL}}
CELERY_BROKER_URL=${{Redis.REDIS_URL}}
CELERY_RESULT_BACKEND=${{Redis.REDIS_URL}}

# Stripe (get from Stripe Dashboard)
STRIPE_SECRET_KEY=sk_live_...
STRIPE_PUBLISHABLE_KEY=pk_live_...
STRIPE_WEBHOOK_SECRET=whsec_...
STRIPE_SUBSCRIPTION_PRODUCT_ID=prod_...

# Auth
JWT_SECRET=your-super-secret-jwt-key-min-32-chars

# App URLs (update after deploying each service)
API_BASE_URL=https://b2b-stickers-api.up.railway.app
SITE_BASE_URL=https://b2b-stickers-site.vercel.app
DASHBOARD_BASE_URL=https://b2b-stickers-dashboard.vercel.app
ENV=production
```

### Required for Core Features

```env
# Email (Resend)
RESEND_API_KEY=re_...
EMAIL_FROM=B2B Stickers <hello@b2b-stickers.co.uk>

# VAT
VAT_RATE_PERCENT=20.0
VAT_NUMBER=GB123456789
```

### Optional (Features degrade gracefully)

```env
# AI Generation (Replicate)
REPLICATE_API_TOKEN=r8_...
OPENAI_API_KEY=sk-...

# Storage (AWS S3 or R2)
AWS_ACCESS_KEY_ID=...
AWS_SECRET_ACCESS_KEY=...
AWS_REGION=eu-west-2
S3_BUCKET=b2b-stickers-images

# Print Provider (Prodigi)
PRODIGI_API_KEY=...

# Companies House
COMPANIES_HOUSE_API_KEY=...

# Marketplaces (Amazon/eBay)
AMAZON_LWA_CLIENT_ID=...
AMAZON_LWA_CLIENT_SECRET=...
AMAZON_REFRESH_TOKEN=...
EBAY_CLIENT_ID=...
EBAY_CLIENT_SECRET=...
```

---

## 4. Deploy API to Railway

### Option A: Railway CLI

```bash
cd apps/api

# Link to project
railway link

# Deploy
railway up

# View logs
railway logs
```

### Option B: GitHub Integration (Recommended)

1. Push code to GitHub
2. Railway Dashboard → New Project → Deploy from GitHub repo
3. Select `apps/api` as root directory
4. Add environment variables
5. Deploy

### Post-Deploy: Database Setup

```bash
# Connect to Railway Postgres
railway connect postgres

# Run init script
\i scripts/init_db.sql
\i scripts/seed_industries.sql
\i scripts/seed_pricing_matrix.sql

# Or use the API container
railway run --service api -- python scripts/seed_keywords.py
```

### Post-Deploy: Run Migrations

```bash
# Alembic migration
railway run --service api -- alembic upgrade head
```

### Post-Deploy: Seed Demo Products

```bash
railway run --service api -- python scripts/seed_demo_products.py --count 50
```

---

## 5. Deploy Dashboard to Vercel

```bash
cd apps/dashboard

# Deploy to Vercel
vercel --prod

# Set environment variables in Vercel Dashboard:
# API_BASE_URL=https://your-railway-api.up.railway.app
```

**Or use GitHub Integration:**
1. Vercel Dashboard → Add New Project
2. Import GitHub repo
3. Root Directory: `apps/dashboard`
4. Framework Preset: Next.js
5. Add env var: `API_BASE_URL`
6. Deploy

---

## 6. Deploy Site to Vercel

```bash
cd apps/site

# Deploy to Vercel
vercel --prod

# Set environment variables:
# API_BASE_URL=https://your-railway-api.up.railway.app
# NEXT_PUBLIC_SITE_URL=https://your-domain.com
```

---

## 7. Configure Stripe Webhooks

In Stripe Dashboard → Developers → Webhooks:

```
Endpoint URL: https://your-railway-api.up.railway.app/api/v1/webhooks/stripe
Events to listen to:
  ✓ checkout.session.completed
  ✓ customer.subscription.updated
  ✓ customer.subscription.deleted
  ✓ invoice.paid
  ✓ invoice.payment_failed
```

Copy the webhook signing secret to `STRIPE_WEBHOOK_SECRET`.

---

## 8. Configure Custom Domain (Optional)

### Railway API
```bash
railway domain
# Creates: https://b2b-stickers-api.up.railway.app
```

### Vercel Site/Dashboard
```bash
vercel domains add b2b-stickers.co.uk
```

Update `SITE_BASE_URL`, `DASHBOARD_BASE_URL`, `API_BASE_URL` to match.

---

## 9. Celery Workers on Railway

Railway doesn't natively support Celery workers. Options:

### Option A: Separate Railway Service
Create a new service in Railway with the same Dockerfile but override the start command:

```dockerfile
# railway-worker.json
{
  "$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "DOCKERFILE",
    "dockerfilePath": "apps/api/Dockerfile"
  },
  "deploy": {
    "startCommand": "celery -A app.workers.celery_app worker --loglevel=info",
    "healthcheckPath": "/health"
  }
}
```

### Option B: Railway Cron + API Endpoints
Use Railway's cron feature to hit API endpoints that trigger tasks.

### Option C: Separate Worker Process (Recommended)
Add a `Procfile` to `apps/api/`:

```
web: uvicorn app.main:app --host 0.0.0.0 --port $PORT
worker: celery -A app.workers.celery_app worker --loglevel=info
beat: celery -A app.workers.celery_app beat --loglevel=info
```

Then create separate Railway services for each process.

---

## 10. Health Checks & Monitoring

### API Health Endpoint
```bash
curl https://your-api.up.railway.app/health
# Expected: {"status":"ok","version":"0.1.0"}
```

### Railway Health Checks
Set in Railway Dashboard:
- Path: `/health`
- Interval: 30s

### Recommended Monitoring
- **Sentry**: Error tracking (already in requirements.txt)
- **UptimeRobot**: External uptime monitoring
- **Stripe Dashboard**: Payment monitoring
- **Railway Metrics**: Built-in resource monitoring

---

## 11. Troubleshooting

### Issue: "Module not found" errors
```bash
# Ensure __init__.py files exist
find apps/api/app -name "__init__.py" | wc -l
# Should be ~15+ files
```

### Issue: Database connection failed
```bash
# Check DATABASE_URL format
# Must be: postgresql+asyncpg://user:pass@host:port/db
# Railway provides this automatically
```

### Issue: Stripe webhooks not working
```bash
# Verify webhook URL is accessible
curl -I https://your-api.up.railway.app/api/v1/webhooks/stripe
# Should return 405 (POST only) not 404
```

### Issue: Static assets 404 on Vercel
```bash
# Ensure next.config.js has correct output settings
cd apps/dashboard && cat next.config.js
```

---

## 12. Production Checklist

- [ ] All environment variables set
- [ ] Database initialized and seeded
- [ ] Alembic migrations run
- [ ] Stripe webhooks configured
- [ ] Custom domain configured
- [ ] SSL certificate active
- [ ] CORS origins restricted to production URLs
- [ ] Debug endpoints disabled (`ENV=production`)
- [ ] JWT secret changed from default
- [ ] Email service configured
- [ ] Celery workers running
- [ ] Health checks passing
- [ ] Error monitoring (Sentry) active
- [ ] Backup strategy configured (Neon has automatic backups)

---

## 13. Scaling

### Railway
- **API**: Auto-scales based on traffic
- **Workers**: Add more worker instances
- **Database**: Upgrade to Pro plan for connection pooling

### Vercel
- **Site/Dashboard**: Auto-scales, edge-cached globally

### Database
- **Neon**: Serverless Postgres, auto-scales
- **Connection pooling**: Use PgBouncer for high traffic

---

*Last updated: 2026-05-22*
