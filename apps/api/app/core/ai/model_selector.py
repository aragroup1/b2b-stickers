from dataclasses import dataclass
from typing import Literal


ModelKey = Literal["flux-schnell", "flux-dev", "flux-1.1-pro", "ideogram-turbo"]


@dataclass
class ModelConfig:
    key: ModelKey
    replicate_model: str
    cost_per_image: float
    description: str


MODELS: dict[ModelKey, ModelConfig] = {
    "flux-schnell": ModelConfig(
        key="flux-schnell",
        replicate_model="black-forest-labs/flux-schnell",
        cost_per_image=0.003,
        description="Fast, cheap. Best for minimalist, kawaii, novelty, testing.",
    ),
    "flux-dev": ModelConfig(
        key="flux-dev",
        replicate_model="black-forest-labs/flux-dev",
        cost_per_image=0.025,
        description="High quality. Best for hand_drawn, cottagecore, brewery_emblem.",
    ),
    "flux-1.1-pro": ModelConfig(
        key="flux-1.1-pro",
        replicate_model="black-forest-labs/flux-1.1-pro",
        cost_per_image=0.04,
        description="Best quality. Best for retro_badge, vintage_americana, holographic_ready.",
    ),
    "ideogram-turbo": ModelConfig(
        key="ideogram-turbo",
        replicate_model="ideogram-ai/ideogram-turbo",
        cost_per_image=0.025,
        description="Typography specialist. Best for motivational_quote, packaging_seal.",
    ),
}


class IntelligentModelSelector:
    """Selects the optimal Replicate model for a given style, keyword, and budget."""

    @staticmethod
    def select(
        style: str,
        keyword: str = "",
        mode: str = "production",
        budget_per_image: float | None = None,
    ) -> ModelConfig:
        from app.core.ai.prompt_templates import STYLE_PROMPTS

        preferred = STYLE_PROMPTS.get(style, {}).get("preferred_model", "flux-schnell")
        cfg = MODELS.get(preferred, MODELS["flux-schnell"])

        if mode == "testing":
            return MODELS["flux-schnell"]

        # flux-schnell tiles designs into sticker-sheets and ignores single-subject
        # instructions, so never use it for real products (only "testing" mode above).
        if cfg.key == "flux-schnell":
            cfg = MODELS["flux-dev"]

        if budget_per_image is not None and cfg.cost_per_image > budget_per_image:
            # Downgrade to fit budget, but never below flux-dev (schnell clusters).
            for key in ["flux-dev", "ideogram-turbo", "flux-1.1-pro"]:
                candidate = MODELS[key]
                if candidate.cost_per_image <= budget_per_image:
                    return candidate

        return cfg
