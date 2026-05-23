-- B2B Stickers & Labels Platform — Initial Schema
-- Run this after database creation; Alembic handles migrations thereafter.

-- Taxonomy
CREATE TABLE IF NOT EXISTS industries (
  id SERIAL PRIMARY KEY,
  slug TEXT UNIQUE NOT NULL,
  name TEXT NOT NULL,
  parent_id INT REFERENCES industries(id),
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Keyword / trend research
CREATE TABLE IF NOT EXISTS trends (
  id SERIAL PRIMARY KEY,
  keyword TEXT UNIQUE NOT NULL,
  industry_id INT REFERENCES industries(id),
  search_volume INT,
  trend_score NUMERIC(5,2),
  category TEXT,
  region TEXT DEFAULT 'UK',
  designs_allocated INT DEFAULT 0,
  designs_generated INT DEFAULT 0,
  last_generated_at TIMESTAMPTZ,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Generated AI artwork
CREATE TABLE IF NOT EXISTS artwork (
  id SERIAL PRIMARY KEY,
  trend_id INT REFERENCES trends(id),
  prompt TEXT NOT NULL,
  negative_prompt TEXT,
  provider TEXT,
  model_used TEXT,
  style TEXT,
  image_url TEXT NOT NULL,
  generation_cost NUMERIC(8,4),
  quality_score NUMERIC(5,2),
  attributes JSONB,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Products
DO $$ BEGIN
  CREATE TYPE product_status AS ENUM (
    'draft','pending_approval','approved','active','paused','archived'
  );
EXCEPTION WHEN duplicate_object THEN NULL;
END $$;

CREATE TABLE IF NOT EXISTS products (
  id SERIAL PRIMARY KEY,
  artwork_id INT REFERENCES artwork(id),
  industry_id INT REFERENCES industries(id),
  slug TEXT UNIQUE NOT NULL,
  title TEXT NOT NULL,
  description TEXT,
  tags TEXT[],
  status product_status DEFAULT 'pending_approval',
  metadata JSONB,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_products_status ON products(status);
CREATE INDEX IF NOT EXISTS idx_products_slug ON products(slug);
CREATE INDEX IF NOT EXISTS idx_products_industry ON products(industry_id);

-- Simplified sticker variants: size × pack only
CREATE TABLE IF NOT EXISTS sticker_variants (
  id SERIAL PRIMARY KEY,
  product_id INT REFERENCES products(id) ON DELETE CASCADE,
  size_inches NUMERIC(3,1) NOT NULL,
  pack_quantity INT NOT NULL,
  unit_cost NUMERIC(10,2),
  retail_price NUMERIC(10,2) NOT NULL,
  sku TEXT UNIQUE NOT NULL,
  stock_quantity INT DEFAULT 999,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_sticker_variants_product ON sticker_variants(product_id);

-- Multi-channel listings
DO $$ BEGIN
  CREATE TYPE platform_type AS ENUM ('amazon_uk','ebay_uk','subscription');
EXCEPTION WHEN duplicate_object THEN NULL;
END $$;

DO $$ BEGIN
  CREATE TYPE listing_status AS ENUM ('queued','live','paused','failed','retired');
EXCEPTION WHEN duplicate_object THEN NULL;
END $$;

CREATE TABLE IF NOT EXISTS platform_listings (
  id SERIAL PRIMARY KEY,
  product_id INT REFERENCES products(id),
  platform platform_type NOT NULL,
  platform_product_id TEXT,
  platform_url TEXT,
  status listing_status DEFAULT 'queued',
  last_synced_at TIMESTAMPTZ,
  performance_data JSONB,
  error_message TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW(),
  UNIQUE (product_id, platform)
);

-- Customers (storefront users)
CREATE TABLE IF NOT EXISTS customers (
  id SERIAL PRIMARY KEY,
  email TEXT UNIQUE NOT NULL,
  stripe_customer_id TEXT UNIQUE,
  name TEXT,
  company_name TEXT,
  company_number TEXT,  -- UK Companies House number
  vat_number TEXT,       -- Customer's VAT number for B2B
  shipping_address JSONB,
  billing_address JSONB,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_customers_email ON customers(email);
CREATE INDEX IF NOT EXISTS idx_customers_stripe ON customers(stripe_customer_id);

-- Subscriptions
DO $$ BEGIN
  CREATE TYPE subscription_status AS ENUM (
    'trialing','active','past_due','canceled','paused'
  );
EXCEPTION WHEN duplicate_object THEN NULL;
END $$;

CREATE TABLE IF NOT EXISTS subscriptions (
  id SERIAL PRIMARY KEY,
  customer_id INT REFERENCES customers(id),
  variant_id INT REFERENCES sticker_variants(id),
  stripe_subscription_id TEXT UNIQUE,
  stripe_price_id TEXT,
  recurring_amount NUMERIC(10,2) NOT NULL,
  discount_percent INT NOT NULL DEFAULT 10,
  status subscription_status DEFAULT 'active',
  current_period_start TIMESTAMPTZ,
  current_period_end TIMESTAMPTZ,
  cancel_at_period_end BOOLEAN DEFAULT FALSE,
  shipping_address JSONB NOT NULL,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_subscriptions_customer ON subscriptions(customer_id);
CREATE INDEX IF NOT EXISTS idx_subscriptions_status ON subscriptions(status);
CREATE INDEX IF NOT EXISTS idx_subscriptions_stripe ON subscriptions(stripe_subscription_id);

-- Subscription shipments
DO $$ BEGIN
  CREATE TYPE shipment_status AS ENUM (
    'scheduled','submitted','shipped','delivered','failed'
  );
EXCEPTION WHEN duplicate_object THEN NULL;
END $$;

CREATE TABLE IF NOT EXISTS subscription_shipments (
  id SERIAL PRIMARY KEY,
  subscription_id INT REFERENCES subscriptions(id),
  scheduled_for DATE NOT NULL,
  status shipment_status DEFAULT 'scheduled',
  variant_id INT REFERENCES sticker_variants(id),
  print_provider_order_id TEXT,
  tracking_number TEXT,
  tracking_url TEXT,
  shipped_at TIMESTAMPTZ,
  delivered_at TIMESTAMPTZ,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW(),
  UNIQUE (subscription_id, scheduled_for)
);
CREATE INDEX IF NOT EXISTS idx_shipments_status ON subscription_shipments(status);
CREATE INDEX IF NOT EXISTS idx_shipments_scheduled ON subscription_shipments(scheduled_for);

-- Orders (unified)
DO $$ BEGIN
  CREATE TYPE order_source AS ENUM ('amazon_uk','ebay_uk','subscription','onetime_store');
EXCEPTION WHEN duplicate_object THEN NULL;
END $$;

DO $$ BEGIN
  CREATE TYPE order_status AS ENUM (
    'pending','processing','fulfilled','shipped','delivered','cancelled','refunded'
  );
EXCEPTION WHEN duplicate_object THEN NULL;
END $$;

CREATE TABLE IF NOT EXISTS orders (
  id SERIAL PRIMARY KEY,
  source order_source NOT NULL,
  external_order_id TEXT,
  customer_id INT REFERENCES customers(id),
  product_id INT REFERENCES products(id),
  variant_id INT REFERENCES sticker_variants(id),
  subscription_shipment_id INT REFERENCES subscription_shipments(id),
  customer_data JSONB,
  order_value NUMERIC(10,2),         -- ex-VAT
  vat_amount NUMERIC(10,2),          -- VAT amount
  order_total NUMERIC(10,2),         -- inc-VAT
  profit NUMERIC(10,2),
  fulfillment_provider TEXT,
  fulfillment_status order_status DEFAULT 'pending',
  shipping_address JSONB,
  invoice_number TEXT,
  invoice_generated_at TIMESTAMPTZ,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW(),
  UNIQUE (source, external_order_id)
);
CREATE INDEX IF NOT EXISTS idx_orders_customer ON orders(customer_id);
CREATE INDEX IF NOT EXISTS idx_orders_status ON orders(fulfillment_status);
CREATE INDEX IF NOT EXISTS idx_orders_created ON orders(created_at);

-- One-time purchases (stored alongside subscriptions)
CREATE TABLE IF NOT EXISTS onetime_purchases (
  id SERIAL PRIMARY KEY,
  customer_id INT REFERENCES customers(id),
  variant_id INT REFERENCES sticker_variants(id),
  quantity INT NOT NULL DEFAULT 1,
  unit_price NUMERIC(10,2) NOT NULL,
  vat_amount NUMERIC(10,2),
  total_price NUMERIC(10,2) NOT NULL,
  stripe_payment_intent_id TEXT,
  status TEXT DEFAULT 'pending',  -- pending, paid, shipped, delivered
  shipping_address JSONB NOT NULL,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Sample/trial orders
CREATE TABLE IF NOT EXISTS sample_orders (
  id SERIAL PRIMARY KEY,
  customer_id INT REFERENCES customers(id),
  product_id INT REFERENCES products(id),
  sample_sku TEXT NOT NULL,  -- e.g. "SAMPLE-001"
  status TEXT DEFAULT 'pending',
  shipping_address JSONB NOT NULL,
  stripe_payment_intent_id TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Daily analytics rollup
CREATE TABLE IF NOT EXISTS analytics_daily (
  id SERIAL PRIMARY KEY,
  date DATE NOT NULL,
  source order_source,
  product_id INT REFERENCES products(id),
  views INT DEFAULT 0,
  clicks INT DEFAULT 0,
  orders INT DEFAULT 0,
  revenue NUMERIC(12,2) DEFAULT 0,
  profit NUMERIC(12,2) DEFAULT 0,
  new_subscriptions INT DEFAULT 0,
  cancellations INT DEFAULT 0,
  mrr NUMERIC(12,2) DEFAULT 0,
  UNIQUE (date, source, product_id)
);

-- Abandoned carts
CREATE TABLE IF NOT EXISTS abandoned_carts (
  id SERIAL PRIMARY KEY,
  customer_email TEXT NOT NULL,
  variant_id INT REFERENCES sticker_variants(id),
  reminder_sent BOOLEAN DEFAULT FALSE,
  recovered BOOLEAN DEFAULT FALSE,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Background jobs
CREATE TABLE IF NOT EXISTS jobs (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  kind TEXT NOT NULL,
  status TEXT NOT NULL,
  params JSONB,
  progress JSONB,
  result JSONB,
  error TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Update triggers for updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

DO $$
DECLARE
    t text;
BEGIN
    FOR t IN
        SELECT tablename FROM pg_tables WHERE schemaname = 'public'
        AND tablename IN ('products', 'sticker_variants', 'platform_listings', 'customers',
                          'subscriptions', 'subscription_shipments', 'orders', 'onetime_purchases',
                          'sample_orders', 'analytics_daily', 'abandoned_carts', 'jobs')
    LOOP
        EXECUTE format('CREATE TRIGGER trg_%s_updated_at
            BEFORE UPDATE ON %s
            FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();',
            t, t);
    END LOOP;
END $$;
