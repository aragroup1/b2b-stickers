from typing import Optional
import httpx
from loguru import logger

from app.config import settings


class EmailService:
    """Transactional email service using Resend (recommended) or SMTP fallback."""

    @staticmethod
    async def send_magic_link(email: str, link: str) -> bool:
        """Send a magic link login email."""
        if settings.RESEND_API_KEY:
            return await EmailService._send_via_resend(email, link)
        elif settings.SMTP_HOST:
            return await EmailService._send_via_smtp(email, link)
        else:
            logger.warning("No email provider configured; magic link logged only")
            return False

    @staticmethod
    async def _send_via_resend(email: str, link: str) -> bool:
        """Send via Resend API (best for transactional emails)."""
        try:
            async with httpx.AsyncClient() as client:
                resp = await client.post(
                    "https://api.resend.com/emails",
                    headers={
                        "Authorization": f"Bearer {settings.RESEND_API_KEY}",
                        "Content-Type": "application/json",
                    },
                    json={
                        "from": settings.EMAIL_FROM or "B2B Stickers <noreply@b2b-stickers.co.uk>",
                        "to": email,
                        "subject": "Your login link for B2B Stickers",
                        "html": EmailService._magic_link_html(email, link),
                        "text": EmailService._magic_link_text(email, link),
                    },
                )
                resp.raise_for_status()
                logger.info(f"Magic link sent to {email} via Resend")
                return True
        except Exception as e:
            logger.error(f"Resend email failed: {e}")
            return False

    @staticmethod
    async def _send_via_smtp(email: str, link: str) -> bool:
        """Send via SMTP fallback."""
        import aiosmtplib
        from email.mime.text import MIMEText
        from email.mime.multipart import MIMEMultipart

        try:
            msg = MIMEMultipart("alternative")
            msg["Subject"] = "Your login link for B2B Stickers"
            msg["From"] = settings.EMAIL_FROM or "noreply@b2b-stickers.co.uk"
            msg["To"] = email
            msg.attach(MIMEText(EmailService._magic_link_text(email, link), "plain"))
            msg.attach(MIMEText(EmailService._magic_link_html(email, link), "html"))

            await aiosmtplib.send(
                msg,
                hostname=settings.SMTP_HOST,
                port=settings.SMTP_PORT or 587,
                username=settings.SMTP_USER,
                password=settings.SMTP_PASSWORD,
                start_tls=True,
            )
            logger.info(f"Magic link sent to {email} via SMTP")
            return True
        except Exception as e:
            logger.error(f"SMTP email failed: {e}")
            return False

    @staticmethod
    def _magic_link_html(email: str, link: str) -> str:
        return f"""<!DOCTYPE html>
<html>
<head><meta charset="utf-8"></head>
<body style="font-family: system-ui, sans-serif; max-width: 600px; margin: 0 auto; padding: 40px 20px;">
  <h2 style="color: #1a1a1a;">Login to B2B Stickers</h2>
  <p>Hi there,</p>
  <p>Click the button below to log in to your B2B Stickers account. This link expires in 1 hour.</p>
  <a href="{link}" style="display: inline-block; background: #2563eb; color: white; padding: 14px 28px; text-decoration: none; border-radius: 6px; font-weight: 500; margin: 16px 0;">Log In</a>
  <p style="color: #666; font-size: 14px;">Or copy and paste this URL:<br>{link}</p>
  <p style="color: #666; font-size: 14px; margin-top: 32px;">Didn't request this? You can safely ignore this email.</p>
</body>
</html>"""

    @staticmethod
    def _magic_link_text(email: str, link: str) -> str:
        return f"""Login to B2B Stickers

Hi there,

Click this link to log in (expires in 1 hour):
{link}

Didn't request this? You can safely ignore this email.
"""

    @staticmethod
    async def send_welcome(email: str, name: Optional[str] = None) -> bool:
        """Send welcome email after first subscription."""
        if not settings.RESEND_API_KEY:
            return False
        try:
            async with httpx.AsyncClient() as client:
                resp = await client.post(
                    "https://api.resend.com/emails",
                    headers={
                        "Authorization": f"Bearer {settings.RESEND_API_KEY}",
                        "Content-Type": "application/json",
                    },
                    json={
                        "from": settings.EMAIL_FROM or "B2B Stickers <hello@b2b-stickers.co.uk>",
                        "to": email,
                        "subject": "Welcome to B2B Stickers — Your subscription is active!",
                        "html": f"""<p>Hi {name or 'there'},</p>
                        <p>Welcome to B2B Stickers! Your subscription is now active.</p>
                        <p>You'll receive your first shipment soon. Manage your subscription anytime from your account.</p>
                        <p>Questions? Just reply to this email.</p>""",
                    },
                )
                resp.raise_for_status()
                return True
        except Exception as e:
            logger.error(f"Welcome email failed: {e}")
            return False

    @staticmethod
    async def send_shipping_notification(email: str, tracking_number: Optional[str] = None) -> bool:
        """Send shipping confirmation with tracking."""
        if not settings.RESEND_API_KEY:
            return False
        tracking_msg = f"<p>Tracking number: <strong>{tracking_number}</strong></p>" if tracking_number else ""
        try:
            async with httpx.AsyncClient() as client:
                resp = await client.post(
                    "https://api.resend.com/emails",
                    headers={
                        "Authorization": f"Bearer {settings.RESEND_API_KEY}",
                        "Content-Type": "application/json",
                    },
                    json={
                        "from": settings.EMAIL_FROM or "B2B Stickers <hello@b2b-stickers.co.uk>",
                        "to": email,
                        "subject": "Your stickers are on their way!",
                        "html": f"""<p>Hi there,</p>
                        <p>Great news — your monthly sticker shipment has been dispatched!</p>
                        {tracking_msg}
                        <p>Thanks for subscribing.</p>""",
                    },
                )
                resp.raise_for_status()
                return True
        except Exception as e:
            logger.error(f"Shipping email failed: {e}")
            return False

    @staticmethod
    async def send_recovery_email(email: str, product_title: str, product_url: str, size: float, pack: int, price: float) -> bool:
        """Send abandoned cart recovery email."""
        if not settings.RESEND_API_KEY:
            return False
        try:
            async with httpx.AsyncClient() as client:
                resp = await client.post(
                    "https://api.resend.com/emails",
                    headers={
                        "Authorization": f"Bearer {settings.RESEND_API_KEY}",
                        "Content-Type": "application/json",
                    },
                    json={
                        "from": settings.EMAIL_FROM or "B2B Stickers <hello@b2b-stickers.co.uk>",
                        "to": email,
                        "subject": f"Still thinking about {product_title}?",
                        "html": f"""<p>Hi there,</p>
                        <p>You were looking at <strong>{product_title}</strong> ({size}" — Pack of {pack}).</p>
                        <p>Subscribe now for just <strong>£{price:.2f}/month</strong> and save 10%.</p>
                        <p><a href="{settings.SITE_BASE_URL}{product_url}">Complete your order →</a></p>
                        <p>Questions? Just reply to this email.</p>""",
                    },
                )
                resp.raise_for_status()
                return True
        except Exception as e:
            logger.error(f"Recovery email failed: {e}")
            return False

    @staticmethod
    async def send_renewal_reminder(email: str, renewal_date: str) -> bool:
        """Send renewal reminder 3 days before charge."""
        if not settings.RESEND_API_KEY:
            return False
        try:
            async with httpx.AsyncClient() as client:
                resp = await client.post(
                    "https://api.resend.com/emails",
                    headers={
                        "Authorization": f"Bearer {settings.RESEND_API_KEY}",
                        "Content-Type": "application/json",
                    },
                    json={
                        "from": settings.EMAIL_FROM or "B2B Stickers <hello@b2b-stickers.co.uk>",
                        "to": email,
                        "subject": "Your sticker subscription renews soon",
                        "html": f"""<p>Hi there,</p>
                        <p>Just a heads up — your B2B Stickers subscription will renew on <strong>{renewal_date}</strong>.</p>
                        <p>No action needed. Your next batch of stickers will ship shortly after.</p>
                        <p>Want to pause, skip, or cancel? <a href="{settings.SITE_BASE_URL}/account">Manage your subscription</a>.</p>""",
                    },
                )
                resp.raise_for_status()
                return True
        except Exception as e:
            logger.error(f"Renewal reminder failed: {e}")
            return False
