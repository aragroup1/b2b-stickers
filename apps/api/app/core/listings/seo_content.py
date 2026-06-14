"""Deterministic SEO content for storefront products (no API cost).

Builds title, description, and tags from the trend keyword, industry, and the
variant size/pack range. Good enough for launch and free to run; can be swapped
for LLM-written copy later (set OPENAI_API_KEY and wire it in here).
"""
from typing import Optional


def generate_seo(
    keyword: str,
    industry_name: Optional[str] = None,
    sizes: Optional[list] = None,
    packs: Optional[list] = None,
) -> dict:
    """Return {title, description, tags} for a sticker/label product."""
    kw = (keyword or "").strip()
    kw_title = kw.title()
    audience = industry_name or "your business"

    title = f"{kw_title} - Custom Vinyl Stickers & Labels (UK Made)"

    size_str = ""
    if sizes:
        lo, hi = min(sizes), max(sizes)
        size_str = f' from {lo:g}" to {hi:g}"'
    pack_str = f", in packs of {min(packs)}-{max(packs)}" if packs else ""

    description = (
        f"Premium {kw} for {audience}. Printed on durable die-cut vinyl and shipped "
        f"from the UK{size_str}{pack_str}. Waterproof and fade-resistant. Order a "
        f"one-off batch or subscribe & save on a recurring schedule. All prices include UK VAT."
    )

    first_word = kw.split()[0] if kw.split() else kw
    raw_tags = [
        kw.lower(),
        "stickers",
        "labels",
        "vinyl stickers",
        "custom labels",
        f"{first_word.lower()} labels",
        "uk made",
        "waterproof stickers",
        "business stickers",
    ]
    if industry_name:
        raw_tags.append(industry_name.lower())

    seen, tags = set(), []
    for t in raw_tags:
        if t and t not in seen:
            seen.add(t)
            tags.append(t)

    return {"title": title, "description": description, "tags": tags[:10]}
