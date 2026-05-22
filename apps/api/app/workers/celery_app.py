from celery import Celery
from celery.schedules import crontab

from app.config import settings

celery_app = Celery(
    "b2b_stickers",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=["app.workers.tasks"],
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    beat_schedule={
        "sync-amazon-orders": {
            "task": "app.workers.tasks.sync_amazon_orders",
            "schedule": crontab(minute="*/15"),
        },
        "sync-ebay-orders": {
            "task": "app.workers.tasks.sync_ebay_orders",
            "schedule": crontab(minute="*/15"),
        },
        "schedule-subscription-shipments": {
            "task": "app.workers.tasks.schedule_subscription_shipments",
            "schedule": crontab(hour=3, minute=0),
        },
        "submit-scheduled-shipments": {
            "task": "app.workers.tasks.submit_scheduled_shipments",
            "schedule": crontab(minute=0),
        },
        "sync-shipment-status": {
            "task": "app.workers.tasks.sync_shipment_status",
            "schedule": crontab(minute="*/30"),
        },
        "analytics-rollup": {
            "task": "app.workers.tasks.analytics_rollup",
            "schedule": crontab(hour=2, minute=0),
        },
        "send-renewal-reminders": {
            "task": "app.workers.tasks.send_renewal_reminders",
            "schedule": crontab(hour=9, minute=0),
        },
        "abandoned-cart-recovery": {
            "task": "app.workers.tasks.abandoned_cart_recovery",
            "schedule": crontab(hour="*/4", minute=0),
        },
    },
)
