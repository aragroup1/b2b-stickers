import io
import uuid
from pathlib import Path
from typing import List, Optional
from PIL import Image, ImageFilter
from loguru import logger


MOCKUP_DIR = Path(__file__).parent.parent.parent / "templates" / "mockups"


class MockupCompositor:
    """PIL-based mockup compositor for sticker products.

    Generates product mockups by compositing sticker designs onto backgrounds.
    Falls back to simple white-background output if base photos unavailable.
    """

    def __init__(self):
        self.mockup_dir = MOCKUP_DIR
        # Ensure mockup directory exists
        self.mockup_dir.mkdir(parents=True, exist_ok=True)

    async def generate_mockups(self, sticker_image_path: str) -> List[str]:
        """Generate mockups for a sticker product.

        Priority:
        1. If base mockup photos exist, composite onto them
        2. Otherwise, generate clean product shots on white/transparent backgrounds
        """
        mockups = []

        # Try to load the sticker image
        try:
            sticker = Image.open(sticker_image_path).convert("RGBA")
        except Exception as e:
            logger.warning(f"Could not load sticker image {sticker_image_path}: {e}")
            return []

        # Strategy 1: Composite onto base photos if available
        base_photos = list(self.mockup_dir.glob("*.jpg")) + list(self.mockup_dir.glob("*.png"))
        # Exclude our generated mockups
        base_photos = [p for p in base_photos if not p.name.startswith("mockup_")]
        if base_photos:
            for photo_path in base_photos[:3]:  # Max 3 base photos
                try:
                    mockup = self._composite_onto_photo(sticker, str(photo_path))
                    if mockup:
                        mockups.append(mockup)
                except Exception as e:
                    logger.warning(f"Mockup compositing failed for {photo_path}: {e}")

        # Strategy 2: Always generate clean product shots
        clean_mockups = self._generate_clean_mockups(sticker)
        mockups.extend(clean_mockups)

        return mockups

    def _composite_onto_photo(self, sticker: Image.Image, photo_path: str) -> Optional[str]:
        """Composite sticker onto a base photo with shadow and perspective."""
        try:
            base = Image.open(photo_path).convert("RGBA")

            # Resize sticker to reasonable size relative to base
            base_w, base_h = base.size
            sticker_size = min(base_w, base_h) // 3
            sticker_resized = sticker.resize((sticker_size, sticker_size), Image.Resampling.LANCZOS)

            # Create shadow
            shadow_offset = 8

            # Paste sticker with shadow onto base
            paste_x = (base_w - sticker_size) // 2
            paste_y = (base_h - sticker_size) // 2

            # Create shadow layer
            shadow_layer = Image.new("RGBA", base.size, (0, 0, 0, 0))
            shadow_sticker = Image.new("RGBA", sticker_resized.size, (0, 0, 0, 80))
            shadow_layer.paste(shadow_sticker, (paste_x + shadow_offset, paste_y + shadow_offset))
            shadow_layer = shadow_layer.filter(ImageFilter.GaussianBlur(radius=6))

            # Composite: base + shadow + sticker
            result = Image.alpha_composite(base, shadow_layer)
            result = Image.alpha_composite(result, sticker_resized.convert("RGBA").copy())
            result = result.convert("RGB")

            # Save
            output_path = str(self.mockup_dir / f"mockup_{Path(photo_path).stem}_{id(sticker)}.jpg")
            result.save(output_path, "JPEG", quality=90)
            return output_path

        except Exception as e:
            logger.warning(f"Photo compositing failed: {e}")
            return None

    def _generate_clean_mockups(self, sticker: Image.Image) -> List[str]:
        """Generate clean product shots on various backgrounds."""
        mockups = []
        sticker = sticker.convert("RGBA")

        configs = [
            {"name": "white", "bg": (255, 255, 255), "size": (1200, 1200)},
            {"name": "grey", "bg": (245, 245, 247), "size": (1200, 1200)},
            {"name": "lifestyle", "bg": None, "gradient": True, "size": (1200, 1200)},
        ]

        for cfg in configs:
            try:
                w, h = cfg["size"]

                if cfg.get("gradient"):
                    # Create a subtle gradient background
                    bg = Image.new("RGB", (w, h), (250, 248, 245))
                else:
                    bg = Image.new("RGB", (w, h), cfg["bg"])

                # Resize sticker to fit nicely
                sticker_size = min(w, h) // 2
                sticker_resized = sticker.resize((sticker_size, sticker_size), Image.Resampling.LANCZOS)

                # Create a subtle shadow
                shadow = Image.new("RGBA", (sticker_size + 40, sticker_size + 40), (0, 0, 0, 0))
                shadow_draw = Image.new("RGBA", (sticker_size, sticker_size), (0, 0, 0, 60))
                shadow.paste(shadow_draw, (20, 20))
                shadow = shadow.filter(ImageFilter.GaussianBlur(radius=15))
                shadow = shadow.resize((sticker_size + 40, sticker_size + 40))

                # Center everything
                paste_x = (w - sticker_size) // 2
                paste_y = (h - sticker_size) // 2

                # Paste shadow
                bg_rgba = bg.convert("RGBA")
                bg_rgba.paste(shadow, (paste_x - 20, paste_y - 20), shadow)

                # Paste sticker
                bg_rgba.paste(sticker_resized, (paste_x, paste_y), sticker_resized)

                # Convert back to RGB and save
                result = bg_rgba.convert("RGB")
                output_path = str(self.mockup_dir / f"mockup_{cfg['name']}_{id(sticker)}.jpg")
                result.save(output_path, "JPEG", quality=92, optimize=True)
                mockups.append(output_path)

            except Exception as e:
                logger.warning(f"Clean mockup generation failed for {cfg['name']}: {e}")

        return mockups

    async def generate_simple_mockup(self, sticker_image_path: str) -> str:
        """Generate a single simple mockup on white background.

        Fast, reliable fallback for when full mockup generation isn't needed.
        """
        try:
            sticker = Image.open(sticker_image_path).convert("RGBA")
            mockups = self._generate_clean_mockups(sticker)
            return mockups[0] if mockups else sticker_image_path
        except Exception as e:
            logger.error(f"Simple mockup generation failed: {e}")
            return sticker_image_path  # Fallback to original

    async def composite_and_store(self, sticker_url: str, industry_name: Optional[str] = None) -> List[str]:
        """Composite the sticker onto relevant product backdrops + a clean shot,
        upload each to object storage, and return permanent public URLs.

        Returns [] (no-op) if storage isn't configured, so it's safe to call before
        R2/S3 is set up.
        """
        from app.services.s3_storage import S3Storage
        from app.core.stickers.backdrops import ensure_backdrops, backdrops_for_industry

        storage = S3Storage()
        if not storage.is_configured():
            logger.warning("Storage not configured — skipping lifestyle mockups (set up R2/S3 first)")
            return []

        sticker = await self._load_image(sticker_url)
        if sticker is None:
            return []

        backdrops = await ensure_backdrops()
        urls: List[str] = []

        for name in backdrops_for_industry(industry_name):
            base = await self._load_image(backdrops.get(name))
            if base is None:
                continue
            try:
                urls.append(await self._store_jpeg(storage, self._paste_centered(base, sticker)))
            except Exception as e:
                logger.warning(f"Mockup compositing failed for backdrop '{name}': {e}")

        # Always add a clean white product shot
        try:
            urls.append(await self._store_jpeg(storage, self._clean_shot(sticker)))
        except Exception as e:
            logger.warning(f"Clean shot failed: {e}")

        return urls

    @staticmethod
    async def _load_image(url: Optional[str]) -> Optional[Image.Image]:
        if not url:
            return None
        try:
            import httpx
            async with httpx.AsyncClient(timeout=60) as client:
                resp = await client.get(url)
                resp.raise_for_status()
            return Image.open(io.BytesIO(resp.content)).convert("RGBA")
        except Exception as e:
            logger.warning(f"Could not load image {url}: {e}")
            return None

    @staticmethod
    async def _store_jpeg(storage, image: Image.Image) -> str:
        buf = io.BytesIO()
        image.save(buf, "JPEG", quality=90, optimize=True)
        key = f"mockups/{uuid.uuid4().hex}.jpg"
        await storage.upload_bytes(buf.getvalue(), key, content_type="image/jpeg")
        return storage.public_url(key)

    def _paste_centered(self, base: Image.Image, sticker: Image.Image) -> Image.Image:
        base = base.convert("RGBA")
        bw, bh = base.size
        size = min(bw, bh) // 3
        st = sticker.resize((size, size), Image.Resampling.LANCZOS)
        px, py = (bw - size) // 2, (bh - size) // 2
        shadow = Image.new("RGBA", base.size, (0, 0, 0, 0))
        shadow.paste(Image.new("RGBA", st.size, (0, 0, 0, 80)), (px + 8, py + 8))
        shadow = shadow.filter(ImageFilter.GaussianBlur(6))
        out = Image.alpha_composite(base, shadow)
        out.paste(st, (px, py), st)
        return out.convert("RGB")

    def _clean_shot(self, sticker: Image.Image) -> Image.Image:
        w = h = 1200
        bg = Image.new("RGBA", (w, h), (255, 255, 255, 255))
        size = min(w, h) // 2
        st = sticker.resize((size, size), Image.Resampling.LANCZOS)
        px, py = (w - size) // 2, (h - size) // 2
        shadow = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        shadow.paste(Image.new("RGBA", (size, size), (0, 0, 0, 60)), (px, py))
        shadow = shadow.filter(ImageFilter.GaussianBlur(15))
        bg = Image.alpha_composite(bg, shadow)
        bg.paste(st, (px, py), st)
        return bg.convert("RGB")
