import json
import re
from typing import Optional

from anthropic import AsyncAnthropic
from loguru import logger

from app.config import settings


class VisionGate:
    """Claude-vision QA gate for AI-generated sticker designs.

    Checks safety + quality and — critically for a sticker/label shop — whether any
    rendered TEXT is correctly spelled. Diffusion models routinely garble text, which
    is unsellable, so this gate reads the text back and flags mismatches.

    No-ops gracefully (approves at a neutral score) if no Anthropic key is configured.
    """

    def __init__(self):
        self.client = AsyncAnthropic(api_key=settings.ANTHROPIC_API_KEY) if settings.ANTHROPIC_API_KEY else None
        self.model = settings.VISION_MODEL

    async def analyze(self, image_url: str, keyword: Optional[str] = None) -> dict:
        if not self.client:
            return {
                "safe": True, "warnings": [], "quality_score": 75.0,
                "text_present": False, "text_correct": True, "rendered_text": "", "attributes": {},
            }

        intended = f" The design is for the keyword: '{keyword}'." if keyword else ""
        system = (
            "You are a strict QA reviewer for AI-generated sticker/label designs sold to UK businesses. "
            "Respond with ONLY a JSON object (no markdown) with these exact keys:\n"
            "- safe (boolean): false for NSFW, real faces, celebrities, copyrighted logos, or brand names\n"
            "- text_present (boolean): true if the image contains any letters or words\n"
            "- rendered_text (string): the exact text visible in the image, verbatim\n"
            "- text_correct (boolean): true ONLY if EVERY visible word is correctly spelled, a real word, and "
            "cleanly rendered. false if ANY text is garbled, misspelled, duplicated, cut off, or has malformed letters\n"
            "- quality_score (number 0-100): overall suitability as a sticker product\n"
            "- warnings (array of strings): specific issues, e.g. 'garbled text: thanko', 'blurry edges'\n"
            "- attributes (object): {palette: ['#..'], motif: '..', theme_tags: ['..']}"
        )
        try:
            resp = await self.client.messages.create(
                model=self.model,
                max_tokens=700,
                system=system,
                messages=[{
                    "role": "user",
                    "content": [
                        {"type": "text", "text": f"Review this sticker design.{intended}"},
                        {"type": "image", "source": {"type": "url", "url": image_url}},
                    ],
                }],
            )
            content = "".join(b.text for b in resp.content if getattr(b, "type", None) == "text") or "{}"
            match = re.search(r"\{.*\}", content, re.DOTALL)
            if match:
                content = match.group(0)
            parsed = json.loads(content)
            return {
                "safe": parsed.get("safe", True),
                "text_present": parsed.get("text_present", False),
                "text_correct": parsed.get("text_correct", True),
                "rendered_text": parsed.get("rendered_text", ""),
                "quality_score": float(parsed.get("quality_score", 70.0)),
                "warnings": parsed.get("warnings", []),
                "attributes": parsed.get("attributes", {}),
            }
        except json.JSONDecodeError as e:
            return {
                "safe": True, "warnings": ["vision gate parse failed — manual review"],
                "quality_score": 60.0, "text_present": False, "text_correct": True,
                "rendered_text": "", "attributes": {}, "parse_error": str(e),
            }
        except Exception as e:
            logger.error(f"Vision gate failed: {e}")
            return {
                "safe": True, "warnings": [f"vision gate error: {e}"],
                "quality_score": 60.0, "text_present": False, "text_correct": True,
                "rendered_text": "", "attributes": {},
            }
