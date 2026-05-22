from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/b2b_stickers"

    # Redis / Celery
    REDIS_URL: str = "redis://localhost:6379/0"
    CELERY_BROKER_URL: str = "redis://localhost:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/0"

    # AI
    REPLICATE_API_TOKEN: str = ""
    OPENAI_API_KEY: str = ""

    # Storage
    AWS_ACCESS_KEY_ID: str = ""
    AWS_SECRET_ACCESS_KEY: str = ""
    AWS_REGION: str = "eu-west-2"
    S3_BUCKET: str = ""

    # Stripe
    STRIPE_SECRET_KEY: str = ""
    STRIPE_WEBHOOK_SECRET: str = ""
    STRIPE_PUBLISHABLE_KEY: str = ""
    STRIPE_SUBSCRIPTION_PRODUCT_ID: str = ""
    SUBSCRIBE_AND_SAVE_DISCOUNT_PERCENT: int = 10

    # Companies House
    COMPANIES_HOUSE_API_KEY: str = ""

    # Prodigi Print Provider
    PRODIGI_API_KEY: str = ""

    # Amazon SP-API
    AMAZON_LWA_CLIENT_ID: str = ""
    AMAZON_LWA_CLIENT_SECRET: str = ""
    AMAZON_REFRESH_TOKEN: str = ""
    AMAZON_MARKETPLACE_ID: str = "A1F83G8C2ARO7P"

    # eBay
    EBAY_CLIENT_ID: str = ""
    EBAY_CLIENT_SECRET: str = ""
    EBAY_REFRESH_TOKEN: str = ""
    EBAY_MARKETPLACE: str = "EBAY_GB"

    # Auth
    JWT_SECRET: str = "change-me"
    MAGIC_LINK_BASE_URL: str = "http://localhost:3000"
    ADMIN_PASSWORD_HASH: str = ""  # bcrypt hash of admin password — generate with scripts/hash_password.py

    # Email
    RESEND_API_KEY: str = ""
    EMAIL_FROM: str = "B2B Stickers <noreply@b2b-stickers.co.uk>"
    SMTP_HOST: str = ""
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""

    # VAT
    VAT_RATE_PERCENT: float = 20.0
    VAT_NUMBER: str = ""  # Your UK VAT number

    # App
    API_BASE_URL: str = "http://localhost:8000"
    DASHBOARD_BASE_URL: str = "http://localhost:3001"
    SITE_BASE_URL: str = "http://localhost:3000"
    ENV: str = "development"

    @property
    def VAT_MULTIPLIER(self) -> float:
        return 1 + (self.VAT_RATE_PERCENT / 100)

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()
