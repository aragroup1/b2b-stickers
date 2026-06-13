from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from loguru import logger

from app.config import settings
from app.database import init_pool, close_pool, ensure_schema
from app.core.sentry import init_sentry

# Initialize Sentry before app creation
init_sentry()
from app.api.v1 import (
    abandoned_cart,
    admin,
    analytics,
    approval,
    catalog,
    company,
    customers,
    debug,
    generation,
    industries,
    jobs,
    listings,
    onetime,
    orders,
    products,
    samples,
    search,
    shipping,
    subscriptions,
    trends,
    vat,
    webhooks,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting up B2B Stickers API...")
    await init_pool()
    try:
        await ensure_schema()
    except Exception as e:
        logger.error(f"ensure_schema failed (continuing without it): {e}")
    yield
    logger.info("Shutting down B2B Stickers API...")
    await close_pool()


app = FastAPI(
    title="B2B Stickers API",
    version="0.1.0",
    lifespan=lifespan,
    docs_url="/docs" if settings.ENV != "production" else None,
    redoc_url="/redoc" if settings.ENV != "production" else None,
    redirect_slashes=True,
)

# Compression middleware
app.add_middleware(GZipMiddleware, minimum_size=1000)

_cors_origins = [
    settings.DASHBOARD_BASE_URL,
    settings.SITE_BASE_URL,
]
if settings.ENV == "development":
    _cors_origins.extend([
        "http://localhost:3000",
        "http://localhost:3001",
    ])

app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH"],
    allow_headers=["Content-Type", "Authorization", "Stripe-Signature"],
)

# Health check
@app.get("/health")
async def health():
    return {"status": "ok", "version": "0.1.0"}

# API v1 routers
v1_prefix = "/api/v1"
app.include_router(abandoned_cart, prefix=v1_prefix)
app.include_router(admin, prefix=v1_prefix)
app.include_router(analytics, prefix=v1_prefix)
app.include_router(approval, prefix=v1_prefix)
app.include_router(catalog, prefix=v1_prefix)
app.include_router(company, prefix=v1_prefix)
app.include_router(customers, prefix=v1_prefix)
app.include_router(debug, prefix=v1_prefix)
app.include_router(generation, prefix=v1_prefix)
app.include_router(industries, prefix=v1_prefix)
app.include_router(jobs, prefix=v1_prefix)
app.include_router(listings, prefix=v1_prefix)
app.include_router(onetime, prefix=v1_prefix)
app.include_router(orders, prefix=v1_prefix)
app.include_router(products, prefix=v1_prefix)
app.include_router(samples, prefix=v1_prefix)
app.include_router(search, prefix=v1_prefix)
app.include_router(shipping, prefix=v1_prefix)
app.include_router(subscriptions, prefix=v1_prefix)
app.include_router(trends, prefix=v1_prefix)
app.include_router(vat, prefix=v1_prefix)
app.include_router(webhooks, prefix=v1_prefix)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
