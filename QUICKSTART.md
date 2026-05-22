# B2B Stickers — Quickstart Deployment

## Status: Code Ready, Needs Your Accounts

All code is committed to git. You just need to connect external services.

---

## Step 1: Create GitHub Repo & Push

```bash
# Go to https://github.com/new
# Create a public repo called "b2b-stickers" (don't initialize with README)

# Then run:
git remote add origin https://github.com/YOUR_USERNAME/b2b-stickers.git
git push -u origin main
```

---

## Step 2: Sign Up for Services (5 minutes)

| Service | URL | Cost |
|---------|-----|------|
| **Railway** | https://railway.app | Free tier |
| **Stripe** | https://dashboard.stripe.com/register | Pay per transaction |
| **Resend** | https://resend.com | Free: 3,000 emails/mo |

---

## Step 3: Deploy API to Railway

```bash
# Install Railway CLI
npm install -g @railway/cli

# Login (opens browser)
railway login

# Link project
cd apps/api
railway link

# Add PostgreSQL + Redis
railway add --database postgres
railway add --database redis

# Set required environment variables
railway variables set JWT_SECRET="$(openssl rand -hex 32)"
railway variables set ADMIN_PASSWORD_HASH="$(cd .. && python scripts/hash_password.py 'your-admin-password' | grep '\$2b\$')"

# Set Stripe keys (get from Stripe Dashboard)
railway variables set STRIPE_SECRET_KEY="sk_test_..."
railway variables set STRIPE_WEBHOOK_SECRET="whsec_..."
railway variables set STRIPE_PUBLISHABLE_KEY="pk_test_..."

# Set other required vars
railway variables set STRIPE_SUBSCRIPTION_PRODUCT_ID="prod_..."
railway variables set RESEND_API_KEY="re_..."
railway variables set VAT_RATE_PERCENT="20.0"
railway variables set VAT_NUMBER="GB123456789"
railway variables set ENV="production"

# Deploy
railway up

# Get your API URL
railway domain
# → https://b2b-stickers-api.up.railway.app
```

---

## Step 4: Initialize Database

```bash
# Connect to Postgres
railway connect postgres

# Run these inside psql:
\i ../../../scripts/init_db.sql
\i ../../../scripts/seed_industries.sql
\i ../../../scripts/seed_pricing_matrix.sql
\q

# Run migrations
railway run -- alembic upgrade head

# Seed demo products
railway run -- python scripts/seed_demo_products.py --count 50
```

---

## Step 5: Configure Stripe Webhooks

In Stripe Dashboard → Developers → Webhooks:

1. Add endpoint: `https://your-api.up.railway.app/api/v1/webhooks/stripe`
2. Select events:
   - `checkout.session.completed`
   - `customer.subscription.updated`
   - `customer.subscription.deleted`
   - `invoice.paid`
   - `invoice.payment_failed`
3. Copy signing secret → set as `STRIPE_WEBHOOK_SECRET` in Railway
4. Redeploy: `railway up`

---

## Step 6: Deploy Dashboard to Vercel

```bash
cd apps/dashboard

# Install Vercel CLI
npm install -g vercel

# Deploy (opens browser to login)
vercel --prod
```

In Vercel Dashboard → Project Settings → Environment Variables:
```
API_BASE_URL=https://your-api.up.railway.app
```

Redeploy from Vercel dashboard.

---

## Step 7: Deploy Site to Vercel

```bash
cd apps/site
vercel --prod
```

In Vercel Dashboard → Environment Variables:
```
API_BASE_URL=https://your-api.up.railway.app
NEXT_PUBLIC_SITE_URL=https://your-site.vercel.app
```

---

## Step 8: Update API URLs & Redeploy

Back in Railway Dashboard, update:
```
SITE_BASE_URL=https://your-site.vercel.app
DASHBOARD_BASE_URL=https://your-dashboard.vercel.app
```

```bash
cd apps/api
railway up
```

---

## Done!

- **Dashboard**: https://your-dashboard.vercel.app/login
- **Site**: https://your-site.vercel.app
- **API**: https://your-api.up.railway.app/health

Login with the password you set in Step 3.

---

## Files I Created/Modified

See `DEPLOY.md` for full details.
