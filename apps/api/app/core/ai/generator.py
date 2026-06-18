import asyncio
import tempfile
import uuid
from pathlib import Path
from typing import Optional

from loguru import logger

from app.config import settings
from app.core.ai.model_selector import IntelligentModelSelector, ModelConfig
from app.core.ai.prompt_templates import get_prompt
from app.core.ai.providers.replicate import ReplicateProvider
from app.services.s3_storage import S3Storage
from app.services.vision_gate import VisionGate


class AIGenerator:
    """Orchestrates AI image generation via Replicate with vision gating."""

    def __init__(self):
        self.selector = IntelligentModelSelector()
        self.provider = ReplicateProvider()
        self.storage = S3Storage()
        self.vision = VisionGate()

    async def generate(
        self,
        keyword: str,
        style: str,
        mode: str = "production",
        budget_per_image: Optional[float] = None,
    ) -> dict:
        from app.core.ai.text_overlay import is_text_primary

        model_cfg = self.selector.select(style, keyword, mode, budget_per_image)
        logger.info(f"Generating '{keyword}' with {model_cfg.key} ({model_cfg.replicate_model})")

        # Text-led designs (thank you, quotes, packaging seals): a text-FREE decorative
        # illustration with the EXACT words overlaid in a real font — the cute illustrated
        # look, but spelling guaranteed by the overlay (the model never renders the words).
        # Falls back to a programmatic seal if generation fails.
        if is_text_primary(style, keyword) and self.storage.is_configured():
            return await self._generate_text_design(keyword, style)

        prompt_cfg = get_prompt(style, keyword)

        # Mock generation mode when no valid Replicate token is configured
        if not settings.REPLICATE_API_TOKEN or settings.REPLICATE_API_TOKEN in ("r8_...", "r8_", ""):
            logger.warning(f"No valid REPLICATE_API_TOKEN configured, using mock generation for '{keyword}'")
            # Use placehold.co with unique colors per style for visual variety
            style_colors = {
                "kawaii": "FFB6C1",
                "retro_badge": "CD853F",
                "minimal_logo": "2F4F4F",
                "hand_drawn": "DEB887",
                "brewery_emblem": "8B4513",
                "vintage_americana": "B22222",
                "holographic_ready": "9932CC",
                "motivational_quote": "4682B4",
                "novelty_meme": "FF6347",
                "packaging_seal": "20B2AA",
                "cottagecore": "F0E68C",
                "y2k": "FF1493",
            }
            color = style_colors.get(style, "808080")
            label = f"{keyword[:15]}|{style[:10]}"
            return {
                "image_url": f"https://placehold.co/600x600/{color}/FFFFFF/png?text={label}",
                "model_used": model_cfg.key,
                "prompt": prompt_cfg["prompt"],
                "negative_prompt": prompt_cfg["negative_prompt"],
                "generation_cost": 0.0,
                "quality_score": 75.0,
                "attributes": {"mock": True, "style": style},
                "vision_warnings": ["Mock generation - no Replicate token configured"],
            }

        # Run Replicate inference
        output_urls = await self.provider.generate(
            model=model_cfg.replicate_model,
            prompt=prompt_cfg["prompt"],
            negative_prompt=prompt_cfg["negative_prompt"],
            width=1024,
            height=1024,
            num_outputs=1,
        )

        if not output_urls:
            raise RuntimeError("Replicate returned no output URLs")

        temp_image_url = output_urls[0]

        # Upload to S3 (illustration path — text-primary designs returned above).
        image_url = temp_image_url
        if settings.S3_BUCKET:
            try:
                image_url = await self._upload_to_s3(temp_image_url)
            except Exception as e:
                logger.warning(f"S3 upload failed, using Replicate URL: {e}")

        # Vision gate (safety + quality). Illustrations shouldn't carry text; if the model
        # leaked garbled words, reject by zeroing quality.
        vision_result = await self.vision.analyze(image_url, keyword)
        quality_score = vision_result.get("quality_score", 75.0)
        if vision_result.get("text_present") and not vision_result.get("text_correct", True):
            quality_score = min(quality_score, 10.0)
            vision_result.setdefault("warnings", []).append("text failed spelling check — auto-rejected")

        return {
            "image_url": image_url,
            "model_used": model_cfg.key,
            "prompt": prompt_cfg["prompt"],
            "negative_prompt": prompt_cfg["negative_prompt"],
            "generation_cost": model_cfg.cost_per_image,
            "quality_score": quality_score,
            "attributes": vision_result.get("attributes", {}),
            "vision_warnings": vision_result.get("warnings", []),
        }

    async def _generate_text_design(self, keyword: str, style: str) -> dict:
        """Text-led design: a text-free decorative illustration with the exact words
        overlaid in a real font (correct spelling), with a programmatic-seal fallback."""
        from app.core.ai.text_overlay import (
            display_text,
            illustration_overlay_prompt,
            overlay,
            render_text_sticker,
        )
        import httpx

        words = display_text(keyword)
        cfg = illustration_overlay_prompt(keyword)
        cost, model_used = 0.0, "programmatic-text"
        try:
            urls = await self.provider.generate(
                model="black-forest-labs/flux-dev",  # more prompt-obedient than schnell: single subject, no text
                prompt=cfg["prompt"],
                negative_prompt=cfg["negative_prompt"],
                width=1024,
                height=1024,
                num_outputs=1,
            )
            if not urls:
                raise RuntimeError("no illustration output")
            async with httpx.AsyncClient(timeout=60) as client:
                resp = await client.get(urls[0])
                resp.raise_for_status()
            composed = overlay(resp.content, words)
            cost, model_used = 0.025, "flux-dev+overlay"
        except Exception as e:
            logger.warning(f"Illustrated text design failed ({e}); falling back to programmatic seal")
            composed = render_text_sticker(words, seed=uuid.uuid4().int % (10 ** 9))

        key = f"uploads/{uuid.uuid4()}.png"
        await self.storage.upload_bytes(composed, key, content_type="image/png")
        image_url = self.storage.public_url(key)
        vision_result = await self.vision.analyze(image_url, keyword)
        return {
            "image_url": image_url,
            "model_used": model_used,
            "prompt": cfg["prompt"],
            "negative_prompt": cfg["negative_prompt"],
            "generation_cost": cost,
            "quality_score": vision_result.get("quality_score", 85.0),
            "attributes": {
                **vision_result.get("attributes", {}),
                "text_overlay": True,
                "display_text": words,
                "style": style,
            },
            "vision_warnings": vision_result.get("warnings", []),
        }

    async def _upload_to_s3(self, image_url: str) -> str:
        """Download from Replicate URL and upload to S3."""
        import httpx
        async with httpx.AsyncClient() as client:
            resp = await client.get(image_url)
            resp.raise_for_status()

        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
            f.write(resp.content)
            tmp_path = f.name

        key = await self.storage.upload(tmp_path)
        Path(tmp_path).unlink(missing_ok=True)
        return self.storage.public_url(key)

    async def batch_generate(
        self,
        keyword: str,
        styles: list[str],
        designs_per_combo: int = 3,
        mode: str = "production",
    ) -> list[dict]:
        results = []
        for style in styles:
            for i in range(designs_per_combo):
                try:
                    result = await self.generate(keyword, style, mode)
                    results.append(result)
                except Exception as e:
                    logger.error(f"Generation failed for {keyword}/{style}/{i}: {e}")
                    results.append({
                        "error": str(e),
                        "keyword": keyword,
                        "style": style,
                    })
        return results
