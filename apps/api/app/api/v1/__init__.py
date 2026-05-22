# API v1 routers
from app.api.v1.abandoned_cart import router as abandoned_cart
from app.api.v1.admin import router as admin
from app.api.v1.analytics import router as analytics
from app.api.v1.approval import router as approval
from app.api.v1.catalog import router as catalog
from app.api.v1.company import router as company
from app.api.v1.customers import router as customers
from app.api.v1.debug import router as debug
from app.api.v1.generation import router as generation
from app.api.v1.industries import router as industries
from app.api.v1.jobs import router as jobs
from app.api.v1.listings import router as listings
from app.api.v1.onetime import router as onetime
from app.api.v1.orders import router as orders
from app.api.v1.products import router as products
from app.api.v1.samples import router as samples
from app.api.v1.search import router as search
from app.api.v1.shipping import router as shipping
from app.api.v1.subscriptions import router as subscriptions
from app.api.v1.trends import router as trends
from app.api.v1.vat import router as vat
from app.api.v1.webhooks import router as webhooks

__all__ = [
    "abandoned_cart",
    "admin",
    "analytics",
    "approval",
    "catalog",
    "company",
    "customers",
    "debug",
    "generation",
    "industries",
    "jobs",
    "listings",
    "onetime",
    "orders",
    "products",
    "samples",
    "search",
    "shipping",
    "subscriptions",
    "trends",
    "vat",
    "webhooks",
]
