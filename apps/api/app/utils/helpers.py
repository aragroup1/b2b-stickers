import re
import uuid

from app.database import get_pool


def slugify(text: str) -> str:
    """Convert text to URL-safe kebab-case slug."""
    text = text.lower()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[\s_]+", "-", text)
    text = re.sub(r"-+", "-", text)
    return text.strip("-")


def generate_sku(product_id: int, size: float, pack: int) -> str:
    return f"STK-{product_id:05d}-{int(size*10):02d}-{pack:03d}"


async def generate_unique_slug(base: str) -> str:
    """Generate a unique slug, checking the database for collisions."""
    slug = slugify(base)
    pool = await get_pool()
    
    # Check if slug exists
    existing = await pool.fetchval("SELECT 1 FROM products WHERE slug = $1", slug)
    if not existing:
        return slug
    
    # Add random suffix if collision
    slug = f"{slug}-{uuid.uuid4().hex[:6]}"
    return slug
