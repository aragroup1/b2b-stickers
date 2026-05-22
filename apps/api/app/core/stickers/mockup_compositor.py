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
