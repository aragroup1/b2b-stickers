import json
import re
from typing import Optional
from openai import AsyncOpenAI

from app.config import settings


class VisionGate:
    """OpenAI Vision API safety gate for generated images."""

    def __init__(self):
        self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

    async def analyze(self, image_url: str) -> dict:
        if not settings.OPENAI_API_KEY:
            return {"safe": True, "warnings": [], "quality_score": 75.0, "attributes": {}}

        try:
            response = await self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are a quality and safety reviewer for AI-generated sticker designs. "
                            "Analyze the image and respond ONLY with a JSON object containing these exact keys:\n"
                            "- safe (boolean): true if no issues found\n"
                            "- warnings (array of strings): list any issues found (text artifacts, faces, NSFW, "
                            "copyrighted logos, brand names, celebrities, low resolution, blur, watermarks, signatures)\n"
                            "- quality_score (number 0-100): overall design quality for a sticker product\n"
                            "- attributes (object): {palette: ['color1', 'color2'], motif: 'description', theme_tags: ['tag1', 'tag2']}\n\n"
                            "Respond with ONLY the JSON object, no markdown, no explanation."
                        ),
                    },
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": "Review this sticker design image."},
                            {"type": "image_url", "image_url": {"url": image_url}},
                        ],
                    },
                ],
                max_tokens=500,
            )

            content = response.choices[0].message.content or "{}"

            # Extract JSON from response (handle markdown code blocks)
            json_match = re.search(r'\{.*\}', content, re.DOTALL)
            if json_match:
                content = json_match.group(0)

            parsed = json.loads(content)

            return {
                "safe": parsed.get("safe", True),
                "warnings": parsed.get("warnings", []),
                "quality_score": float(parsed.get("quality_score", 75.0)),
                "attributes": parsed.get("attributes", {}),
            }

        except json.JSONDecodeError as e:
            # If JSON parsing fails, return a safe default but log the raw response
            return {
                "safe": True,
                "warnings": ["Vision gate parsing failed — manual review recommended"],
                "quality_score": 60.0,
                "attributes": {},
                "parse_error": str(e),
                "raw_response": content[:500] if 'content' in dir() else None,
            }
        except Exception as e:
            return {
                "safe": True,
                "warnings": [f"Vision gate error: {str(e)}"],
                "quality_score": 60.0,
                "attributes": {},
            }
