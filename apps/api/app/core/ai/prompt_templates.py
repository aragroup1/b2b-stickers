STYLE_PROMPTS = {
    "kawaii": {
        "template": "Kawaii sticker illustration of {keyword}, cute pastel colours, soft rounded outlines, sticker-friendly die-cut shape, clean white background, no text",
        "negative": "photorealistic human faces, fingers, hands, copyrighted logos, brand names, celebrities, low resolution, blurry, watermark, signature, text artifacts, excessive fine detail, photographic background",
        "preferred_model": "flux-schnell",
        "sticker_optimized": True,
    },
    "retro_badge": {
        "template": "Vintage badge emblem sticker design for {keyword}, bold retro typography, distressed texture, circular layout, classic colour palette, sticker die-cut, clean background",
        "negative": "photorealistic human faces, fingers, hands, copyrighted logos, brand names, celebrities, low resolution, blurry, watermark, signature, text artifacts, excessive fine detail, photographic background",
        "preferred_model": "flux-1.1-pro",
        "sticker_optimized": True,
    },
    "minimal_logo": {
        "template": "Minimal geometric logo sticker for {keyword}, clean lines, single accent colour, modern flat design, die-cut sticker shape, white background",
        "negative": "photorealistic human faces, fingers, hands, copyrighted logos, brand names, celebrities, low resolution, blurry, watermark, signature, text artifacts, excessive fine detail, photographic background",
        "preferred_model": "flux-schnell",
        "sticker_optimized": True,
    },
    "vintage_americana": {
        "template": "Vintage Americana sticker for {keyword}, distressed sepia tones, traditional sign-painter style, weathered texture, bold lettering feel, die-cut sticker",
        "negative": "photorealistic human faces, fingers, hands, copyrighted logos, brand names, celebrities, low resolution, blurry, watermark, signature, text artifacts, excessive fine detail, photographic background",
        "preferred_model": "flux-1.1-pro",
        "sticker_optimized": True,
    },
    "holographic_ready": {
        "template": "Bold high-contrast sticker art for {keyword}, designed for holographic foil, vibrant saturated colours, strong silhouettes, no fine gradients, die-cut shape",
        "negative": "photorealistic human faces, fingers, hands, copyrighted logos, brand names, celebrities, low resolution, blurry, watermark, signature, text artifacts, excessive fine detail, photographic background",
        "preferred_model": "flux-1.1-pro",
        "sticker_optimized": True,
    },
    "hand_drawn": {
        "template": "Hand-drawn ink illustration sticker for {keyword}, sketchy line art, organic textures, artistic feel, die-cut sticker border, white background",
        "negative": "photorealistic human faces, fingers, hands, copyrighted logos, brand names, celebrities, low resolution, blurry, watermark, signature, text artifacts, excessive fine detail, photographic background",
        "preferred_model": "flux-dev",
        "sticker_optimized": True,
    },
    "brewery_emblem": {
        "template": "Craft beer label style emblem for {keyword}, ornate border, bold serif typography feel, rich colours, circular badge, die-cut sticker",
        "negative": "photorealistic human faces, fingers, hands, copyrighted logos, brand names, celebrities, low resolution, blurry, watermark, signature, text artifacts, excessive fine detail, photographic background",
        "preferred_model": "flux-dev",
        "sticker_optimized": True,
    },
    "motivational_quote": {
        "template": "Typography-led motivational sticker for {keyword}, bold modern lettering, clean layout, inspiring design, no photorealistic elements, die-cut sticker",
        "negative": "photorealistic human faces, fingers, hands, copyrighted logos, brand names, celebrities, low resolution, blurry, watermark, signature, text artifacts, excessive fine detail, photographic background",
        "preferred_model": "ideogram-turbo",
        "sticker_optimized": True,
    },
    "novelty_meme": {
        "template": "Cartoon meme style sticker for {keyword}, funny illustration, bold outlines, expressive characters, pop art colours, die-cut sticker shape",
        "negative": "photorealistic human faces, fingers, hands, copyrighted logos, brand names, celebrities, low resolution, blurry, watermark, signature, text artifacts, excessive fine detail, photographic background",
        "preferred_model": "flux-schnell",
        "sticker_optimized": True,
    },
    "packaging_seal": {
        "template": "Circular packaging seal sticker for {keyword}, stamp style, 'thank you' / 'handmade' / 'fresh' feel, elegant border, die-cut circular sticker",
        "negative": "photorealistic human faces, fingers, hands, copyrighted logos, brand names, celebrities, low resolution, blurry, watermark, signature, text artifacts, excessive fine detail, photographic background",
        "preferred_model": "ideogram-turbo",
        "sticker_optimized": True,
    },
    "cottagecore": {
        "template": "Cottagecore botanical sticker for {keyword}, soft watercolour flowers, delicate vines, pastel palette, romantic feel, die-cut sticker, white background",
        "negative": "photorealistic human faces, fingers, hands, copyrighted logos, brand names, celebrities, low resolution, blurry, watermark, signature, text artifacts, excessive fine detail, photographic background",
        "preferred_model": "flux-dev",
        "sticker_optimized": True,
    },
    "y2k": {
        "template": "Y2K chrome gradient sticker for {keyword}, bubble fonts, metallic shine, retro-futuristic, bold colours, die-cut sticker shape, white background",
        "negative": "photorealistic human faces, fingers, hands, copyrighted logos, brand names, celebrities, low resolution, blurry, watermark, signature, text artifacts, excessive fine detail, photographic background",
        "preferred_model": "flux-schnell",
        "sticker_optimized": True,
    },
}


# Applied to every style so designs come out as ONE clean die-cut sticker, not a
# scattered sheet/collage (the model's default for "sticker" prompts — see the
# garbled multi-sticker reject that motivated this).
_SINGLE_STICKER = (
    "single centered die-cut sticker, one isolated design, centered composition, "
    "plain solid white background, entire design fully visible and not cropped"
)
_ANTI_COLLAGE = (
    "multiple stickers, sticker sheet, collage, tiled, scattered stickers, "
    "grid of stickers, duplicated design, repeated motif, cropped, cut off"
)


def get_prompt(style: str, keyword: str) -> dict:
    """Return the full prompt config for a given style and keyword."""
    cfg = STYLE_PROMPTS.get(style, STYLE_PROMPTS["minimal_logo"])
    return {
        "prompt": f"{cfg['template'].format(keyword=keyword)}, {_SINGLE_STICKER}",
        "negative_prompt": f"{cfg['negative']}, {_ANTI_COLLAGE}",
        "preferred_model": cfg["preferred_model"],
        "sticker_optimized": cfg["sticker_optimized"],
    }
