"""Programmatic rendering for text-primary sticker designs.

Diffusion models garble text and leak their own words even when told not to
(a "no text" prompt for the keyword "thank you" still renders "thank you"),
which then collides with anything we overlay. For text-primary designs we skip
the model entirely and render the whole sticker — background shape + words — with
a real font. Spelling is correct by construction, there is no collage, and it's free.
"""
import io
import os
import random
import re

from loguru import logger
from PIL import Image, ImageDraw, ImageFont

# Styles that are inherently text-led
TEXT_STYLES = {"motivational_quote", "packaging_seal"}

# Keyword cues meaning the design *is* the words (greetings, quotes, packaging seals)
_TEXT_KEYWORD_RE = re.compile(
    r"\b(thank ?you|thanks|happy birthday|welcome|congrats|congratulations|quote|"
    r"motivational|affirmation|please|sorry|hello|good luck|well done|cheers|"
    r"merry christmas|happy holidays|get well|new baby|just married|handmade|fragile)\b",
    re.I,
)
_SUFFIX_RE = re.compile(r"\b(stickers?|labels?|decals?|designs?|prints?)\b", re.I)

# Curated, B2B-tasteful palettes. Solid: (background, text). Accents: ring/text on white.
_SOLID = [
    ((31, 79, 58), (255, 255, 255)),    # deep green / white
    ((31, 58, 102), (255, 255, 255)),   # navy / white
    ((124, 32, 64), (255, 255, 255)),   # maroon / white
    ((38, 38, 38), (255, 255, 255)),    # charcoal / white
    ((244, 232, 217), (74, 55, 40)),    # kraft / brown
    ((226, 240, 233), (31, 79, 58)),    # sage / deep green
    ((250, 228, 232), (124, 32, 64)),   # blush / maroon
]
_ACCENTS = [(31, 79, 58), (31, 58, 102), (124, 32, 64), (38, 38, 38), (74, 55, 40)]


def is_text_primary(style: str, keyword: str) -> bool:
    if style in TEXT_STYLES:
        return True
    return bool(_TEXT_KEYWORD_RE.search(keyword or ""))


def display_text(keyword: str) -> str:
    """Turn a trend keyword into the words to print: 'thank you stickers' -> 'Thank You'."""
    t = _SUFFIX_RE.sub("", keyword or "").strip()
    t = re.sub(r"\s+", " ", t)
    return (t or keyword or "").title()


# keyword -> decorative motif (themed WITHOUT naming the words, so the model doesn't render text)
_MOTIFS = [
    (re.compile(r"thank", re.I), "pastel hearts, blooming flowers and gentle sparkles"),
    (re.compile(r"birthday", re.I), "balloons, confetti, party streamers and a little cake"),
    (re.compile(r"wedding|married|favou?r", re.I), "delicate florals, rings and soft leaves"),
    (re.compile(r"christmas|holiday|merry", re.I), "holly, snowflakes, baubles and pine sprigs"),
    (re.compile(r"baby", re.I), "soft clouds, tiny stars and little hearts"),
    (re.compile(r"welcome|hello", re.I), "cheerful flowers and a smiling sun"),
    (re.compile(r"good luck|congrat|well done", re.I), "stars, sparkles and laurel leaves"),
    (re.compile(r"handmade|made with love", re.I), "botanical sprigs, dots and a needle and thread"),
    (re.compile(r"fragile", re.I), "simple leaves, dots and soft geometric shapes"),
    (re.compile(r"get well|sorry", re.I), "gentle flowers, leaves and a warm little sun"),
]
_DEFAULT_MOTIF = "pastel flowers, hearts and gentle sparkles"


def _motif_for(keyword: str) -> str:
    for rx, motif in _MOTIFS:
        if rx.search(keyword or ""):
            return motif
    return _DEFAULT_MOTIF


def illustration_overlay_prompt(keyword: str) -> dict:
    """A text-FREE decorative illustration prompt with a clear empty centre for the
    overlaid words. The motif is themed to the keyword WITHOUT naming it, so the model
    has no reason to render its own (garbled) text."""
    motif = _motif_for(keyword)
    return {
        "prompt": (
            f"kawaii sticker illustration of {motif}, cute soft pastel colours, charming "
            "hand-drawn style, arranged as a decorative frame around a large clear empty "
            "white centre, one single centered die-cut sticker, plain solid white background, "
            "entire design fully visible and not cropped, absolutely no text, no words, "
            "no letters, no captions, no numbers"
        ),
        "negative_prompt": (
            "text, words, letters, typography, captions, numbers, watermark, signature, "
            "multiple stickers, sticker sheet, collage, tiled, scattered stickers, grid, "
            "duplicated, repeated motif, cropped, cut off, photorealistic human faces, "
            "fingers, hands, copyrighted logos, brand names"
        ),
    }


def _find_font(size: int) -> ImageFont.FreeTypeFont:
    candidates = []
    try:
        import matplotlib
        candidates.append(os.path.join(matplotlib.get_data_path(), "fonts", "ttf", "DejaVuSans-Bold.ttf"))
    except Exception:
        pass
    candidates += [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/dejavu/DejaVuSans-Bold.ttf",
        "DejaVuSans-Bold.ttf",
    ]
    for path in candidates:
        try:
            return ImageFont.truetype(path, size)
        except Exception:
            continue
    logger.warning("No TrueType font found — falling back to PIL default (low quality)")
    return ImageFont.load_default()


def _wrap(words: list, n_lines: int) -> list:
    if n_lines <= 1 or len(words) <= 1:
        return [" ".join(words)]
    per = -(-len(words) // n_lines)  # ceil division
    return [" ".join(words[i:i + per]) for i in range(0, len(words), per)]


def _fit_font(draw, text: str, max_w: int, max_h: int, max_size: int):
    """Pick the line-wrapping + font size that fills the box as large as possible.

    Trying fewer lines first and returning early makes long phrases tiny (one line
    shrinks to fit the width); instead, evaluate each line count and keep whichever
    yields the biggest readable font.
    """
    words = text.split()
    best = None  # (size, lines, font)
    for n_lines in (1, 2, 3):
        if n_lines > len(words):
            break
        lines = _wrap(words, n_lines)
        size = max_size
        while size > 14:
            font = _find_font(size)
            w = max((draw.textlength(line, font=font) for line in lines), default=0)
            asc, desc = font.getmetrics()
            h = (asc + desc) * len(lines)
            if w <= max_w and h <= max_h:
                break
            size -= 4
        if best is None or size > best[0]:
            best = (size, lines, font)
    if best is None:
        return [text], _find_font(16)
    return best[1], best[2]


def _draw_lines(draw, W: int, H: int, lines: list, font, color, halo: bool, center_y: float = 0.5):
    asc, desc = font.getmetrics()
    line_h = asc + desc
    total_h = line_h * len(lines)
    y0 = int(H * center_y) - total_h // 2
    for i, line in enumerate(lines):
        lw = int(draw.textlength(line, font=font))
        lx = (W - lw) // 2
        ly = y0 + i * line_h
        if halo:
            for dx, dy in ((-3, 0), (3, 0), (0, -3), (0, 3), (-2, -2), (2, 2)):
                draw.text((lx + dx, ly + dy), line, font=font, fill=(255, 255, 255, 235))
        draw.text((lx, ly), line, font=font, fill=color)


def render_text_sticker(text: str, seed: int = 0) -> bytes:
    """Render a die-cut text sticker: a TRANSPARENT PNG (only the circle is opaque),
    with a white vinyl edge, the seal design, and the words. Supersampled 2x for
    smooth edges. Transparency is what lets it composite onto products as a real
    die-cut instead of a white square."""
    rnd = random.Random(seed)
    S = 2                       # supersample for smooth circle + text, then downscale
    W = H = 1024 * S
    c = W // 2
    R = 468 * S                 # die-cut radius
    margin = 18 * S             # white vinyl border just inside the cut edge
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # White die-cut base (the vinyl). Everything outside this circle stays transparent.
    draw.ellipse([c - R, c - R, c + R, c + R], fill=(255, 255, 255, 255))
    rin = R - margin

    if rnd.random() < 0.5:
        # Solid seal: filled colour face inside the white edge, contrasting text
        bg, txt = rnd.choice(_SOLID)
        draw.ellipse([c - rin, c - rin, c + rin, c + rin], fill=bg)
        r2 = rin - 24 * S
        draw.ellipse([c - r2, c - r2, c + r2, c + r2], outline=txt, width=4 * S)
        text_color = txt
    else:
        # Outline seal: white face, bold colour ring, matching text
        accent = rnd.choice(_ACCENTS)
        draw.ellipse([c - rin, c - rin, c + rin, c + rin], outline=accent, width=14 * S)
        r2 = rin - 22 * S
        draw.ellipse([c - r2, c - r2, c + r2, c + r2], outline=accent, width=4 * S)
        text_color = accent

    lines, font = _fit_font(draw, text, int(W * 0.60), int(H * 0.44), int(H * 0.21))
    _draw_lines(draw, W, H, lines, font, text_color, halo=False)

    img = img.resize((1024, 1024), Image.LANCZOS)
    out = io.BytesIO()
    img.save(out, "PNG")
    return out.getvalue()


def overlay(image_bytes: bytes, text: str) -> bytes:
    """Draw `text` centered onto an existing background image; returns PNG bytes.

    Kept for the case where we *do* want words on a supplied background; the
    generator uses render_text_sticker for text-primary designs instead.
    """
    img = Image.open(io.BytesIO(image_bytes)).convert("RGBA")
    W, H = img.size
    draw = ImageDraw.Draw(img)
    lines, font = _fit_font(draw, text, int(W * 0.64), int(H * 0.44), int(H * 0.20))
    _draw_lines(draw, W, H, lines, font, (36, 36, 36, 255), halo=True)
    out = io.BytesIO()
    img.convert("RGB").save(out, "PNG")
    return out.getvalue()
