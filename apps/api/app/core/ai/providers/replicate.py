import asyncio
import random
from typing import Optional

import httpx
import replicate
from loguru import logger

from app.config import settings


class ReplicateProvider:
    """Production-grade Replicate wrapper with retries, exponential backoff, and error classification."""

    def __init__(self):
        self.client = replicate.Client(api_token=settings.REPLICATE_API_TOKEN)

    async def generate(
        self,
        model: str,
        prompt: str,
        negative_prompt: str = "",
        width: int = 1024,
        height: int = 1024,
        num_outputs: int = 1,
        max_retries: int = 3,
        base_delay: float = 2.0,
    ) -> list[str]:
        """Run inference with retries and return list of output image URLs.

        Retries on:
        - Rate limits (429)
        - Server errors (5xx)
        - Timeouts
        - Transient network errors

        Does NOT retry on:
        - 4xx client errors (except 429)
        - Invalid prompts (400)
        - Authentication failures (401/403)
        """
        if not settings.REPLICATE_API_TOKEN:
            raise RuntimeError("REPLICATE_API_TOKEN not configured")

        last_exception: Optional[Exception] = None

        for attempt in range(1, max_retries + 1):
            try:
                logger.info(
                    f"Replicate call attempt {attempt}/{max_retries}: model={model} "
                    f"prompt_len={len(prompt)}"
                )

                # Run inference (synchronous SDK call in thread pool)
                loop = asyncio.get_event_loop()
                output = await loop.run_in_executor(
                    None,
                    lambda: self.client.run(
                        model,
                        input={
                            "prompt": prompt,
                            "negative_prompt": negative_prompt,
                            "width": width,
                            "height": height,
                            "num_outputs": num_outputs,
                        },
                    ),
                )

                urls = output if isinstance(output, list) else [output]
                urls = [u for u in urls if isinstance(u, str) and u.startswith("http")]

                if not urls:
                    raise RuntimeError(f"Replicate returned no valid URLs: {output}")

                logger.info(f"Replicate success: {len(urls)} image(s) generated")
                return urls

            except replicate.exceptions.ReplicateError as e:
                last_exception = e
                status_code = getattr(e, "status", None)

                # Don't retry auth or bad request errors
                if status_code in (400, 401, 403, 422):
                    logger.error(f"Replicate client error {status_code}, not retrying: {e}")
                    raise

                # Retry on rate limit or server errors
                if status_code in (429, 500, 502, 503, 504) or status_code is None:
                    if attempt < max_retries:
                        delay = base_delay * (2 ** (attempt - 1)) + random.uniform(0, 1)
                        logger.warning(
                            f"Replicate error (attempt {attempt}/{max_retries}), "
                            f"retrying in {delay:.1f}s: {e}"
                        )
                        await asyncio.sleep(delay)
                        continue

                logger.error(f"Replicate error after {attempt} attempts: {e}")
                raise

            except (httpx.TimeoutException, asyncio.TimeoutError) as e:
                last_exception = e
                if attempt < max_retries:
                    delay = base_delay * (2 ** (attempt - 1)) + random.uniform(0, 1)
                    logger.warning(f"Replicate timeout (attempt {attempt}), retrying in {delay:.1f}s")
                    await asyncio.sleep(delay)
                    continue
                logger.error(f"Replicate timeout after {max_retries} attempts")
                raise

            except Exception as e:
                last_exception = e
                if attempt < max_retries:
                    delay = base_delay * (2 ** (attempt - 1)) + random.uniform(0, 1)
                    logger.warning(f"Replicate unexpected error (attempt {attempt}), retrying in {delay:.1f}s: {e}")
                    await asyncio.sleep(delay)
                    continue
                logger.error(f"Replicate failed after {max_retries} attempts: {e}")
                raise

        # Should never reach here, but just in case
        raise last_exception or RuntimeError("Replicate generation failed after all retries")

    async def download_image(self, url: str, timeout: float = 30.0) -> bytes:
        """Download an image from a Replicate output URL."""
        async with httpx.AsyncClient(timeout=timeout) as client:
            resp = await client.get(url)
            resp.raise_for_status()
            return resp.content
