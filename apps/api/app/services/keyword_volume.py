"""Google Trends search-interest fetcher (free, unofficial, via pytrends).

Used to fill `trends.search_volume` for keywords that lack Keyword Planner data.
Google Trends is rate-limited and unofficial, so this is best-effort: failures are
logged and skipped, never fatal. Keyword Planner data always takes precedence.

Trends returns *relative* interest (0-100, normalised within each <=5-term request).
To compare across batches we include a fixed ANCHOR_KEYWORD in every batch and rescale
each keyword's score relative to the anchor.
"""

import time
from typing import Optional

from loguru import logger

ANCHOR_KEYWORD = "stickers"   # appears in every batch to normalise across batches
GEO = "GB"                    # UK — this is a UK B2B seller
TIMEFRAME = "today 12-m"      # last 12 months
BATCH_SIZE = 4                # 4 keywords + 1 anchor = pytrends' 5-term limit
# Maps anchor-normalised interest -> pseudo search_volume. Kept small so Trends-only
# keywords sit *below* typical Keyword Planner volumes (intended: trusted data leads).
SCALE = 10


class KeywordVolumeService:
    """Fetches anchor-normalised Google Trends interest for a list of keywords."""

    def __init__(self) -> None:
        from pytrends.request import TrendReq

        self.pytrends = TrendReq(hl="en-GB", tz=0)

    def fetch_interest(self, keywords: list[str]) -> dict[str, int]:
        """Return {keyword: anchor-normalised interest} for the given keywords.

        Synchronous + blocking (sleeps between batches to respect rate limits).
        Intended to run inside a Celery task, not a request handler.
        """
        results: dict[str, int] = {}
        unique = [
            k for k in dict.fromkeys(keywords)
            if k and k.lower() != ANCHOR_KEYWORD.lower()
        ]
        batches = [unique[i:i + BATCH_SIZE] for i in range(0, len(unique), BATCH_SIZE)]
        anchor_baseline: Optional[float] = None

        for batch in batches:
            terms = [ANCHOR_KEYWORD] + batch
            interest = self._query(terms)
            if not interest:
                continue
            anchor_val = interest.get(ANCHOR_KEYWORD, 0) or 0
            if anchor_baseline is None and anchor_val > 0:
                anchor_baseline = anchor_val
            for kw in batch:
                raw = interest.get(kw, 0) or 0
                if anchor_val > 0 and anchor_baseline:
                    norm = raw / anchor_val * anchor_baseline
                else:
                    norm = raw
                results[kw] = int(round(norm))
            time.sleep(2)
        return results

    def _query(self, terms: list[str]) -> Optional[dict[str, int]]:
        for attempt in range(3):
            try:
                self.pytrends.build_payload(terms, timeframe=TIMEFRAME, geo=GEO)
                df = self.pytrends.interest_over_time()
                if df is None or df.empty:
                    return None
                return {
                    t: int(round(float(df[t].mean())))
                    for t in terms if t in df.columns
                }
            except Exception as e:  # pytrends raises various errors incl. 429s
                wait = 5 * (attempt + 1)
                logger.warning(
                    f"pytrends query failed (attempt {attempt + 1}/3): {e}; retry in {wait}s"
                )
                time.sleep(wait)
        logger.error(f"pytrends query failed permanently for terms: {terms}")
        return None
