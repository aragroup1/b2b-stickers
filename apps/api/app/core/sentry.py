"""Sentry error tracking integration."""
import os

from app.config import settings


def init_sentry():
    """Initialize Sentry if DSN is configured."""
    dsn = os.environ.get("SENTRY_DSN", "")
    if not dsn:
        return

    try:
        import sentry_sdk
        from sentry_sdk.integrations.fastapi import FastApiIntegration
        from sentry_sdk.integrations.starlette import StarletteIntegration

        sentry_sdk.init(
            dsn=dsn,
            environment=settings.ENV,
            release=os.environ.get("GIT_COMMIT_SHA", "unknown"),
            traces_sample_rate=0.1,
            profiles_sample_rate=0.05,
            integrations=[
                StarletteIntegration(transaction_style="endpoint"),
                FastApiIntegration(transaction_style="endpoint"),
            ],
        )
    except ImportError:
        pass
