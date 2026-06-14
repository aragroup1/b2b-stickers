"""Blank product-photo backdrops for lifestyle mockups.

Generated once via Replicate, stored in object storage (R2/S3), then composited
with stickers on approval. No-ops gracefully if storage isn't configured yet
(placeholder state until Cloudflare R2 / S3 is set up).
"""
from loguru import logger

from app.services.s3_storage import S3Storage

# name -> Replicate prompt for a blank, label-less product photo
BACKDROP_SPECS = {
    "water_bottle": "professional studio product photo of a plain matte stainless-steel water bottle on a neutral light-grey surface, soft lighting, blank, no text, no logo, photorealistic",
    "kraft_box": "professional studio product photo of a plain brown kraft cardboard shipping box on a neutral light-grey surface, soft lighting, blank, no text, photorealistic",
    "glass_jar": "professional studio product photo of a plain clear glass jar with a blank front on a neutral light-grey surface, soft lighting, no text, photorealistic",
    "laptop": "professional photo of a closed silver laptop on a neutral light-grey desk, soft lighting, blank lid, no logo, photorealistic",
    "notebook": "professional studio product photo of a plain hardcover notebook on a neutral light-grey surface, soft lighting, blank cover, no text, photorealistic",
    "tote_bag": "professional studio product photo of a plain natural canvas tote bag against a neutral light-grey wall, soft lighting, blank, no text, photorealistic",
}

# loose industry-name substring -> preferred backdrops (most relevant first)
INDUSTRY_BACKDROPS = {
    "food": ["kraft_box", "glass_jar"],
    "bever": ["water_bottle", "glass_jar"],
    "drink": ["water_bottle", "glass_jar"],
    "brew": ["glass_jar", "kraft_box"],
    "cosmet": ["glass_jar", "water_bottle"],
    "skincare": ["glass_jar", "water_bottle"],
    "soap": ["kraft_box", "glass_jar"],
    "pet": ["kraft_box", "glass_jar"],
    "candle": ["glass_jar", "kraft_box"],
    "apparel": ["tote_bag", "notebook"],
    "clothing": ["tote_bag", "notebook"],
    "tech": ["laptop", "notebook"],
}
DEFAULT_BACKDROPS = ["laptop", "kraft_box", "notebook"]


def backdrops_for_industry(industry_name):
    """Return the backdrop names most relevant to an industry (or sensible defaults)."""
    if industry_name:
        low = industry_name.lower()
        for key, names in INDUSTRY_BACKDROPS.items():
            if key in low:
                return names
    return DEFAULT_BACKDROPS


async def ensure_backdrops() -> dict:
    """Ensure backdrop images exist in storage; generate any missing via Replicate.

    Returns {name: public_url}. Returns {} if storage isn't configured (placeholder
    state until R2/S3 is set up).
    """
    storage = S3Storage()
    if not storage.is_configured():
        logger.warning("Storage not configured — skipping backdrop generation (set up R2/S3 first)")
        return {}

    from app.core.ai.providers.replicate import ReplicateProvider
    import httpx

    provider = ReplicateProvider()
    result = {}
    for name, prompt in BACKDROP_SPECS.items():
        key = f"backdrops/{name}.png"
        if storage.exists(key):
            result[name] = storage.public_url(key)
            continue
        try:
            urls = await provider.generate(
                model="black-forest-labs/flux-schnell",  # cheap; backdrops don't need flagship quality
                prompt=prompt,
                negative_prompt="text, watermark, logo, label, sticker, words, letters",
                width=1024,
                height=1024,
                num_outputs=1,
            )
            if not urls:
                continue
            async with httpx.AsyncClient(timeout=60) as client:
                resp = await client.get(urls[0])
                resp.raise_for_status()
            await storage.upload_bytes(resp.content, key, content_type="image/png")
            result[name] = storage.public_url(key)
            logger.info(f"Generated backdrop '{name}'")
        except Exception as e:
            logger.error(f"Backdrop '{name}' generation failed: {e}")
    return result
