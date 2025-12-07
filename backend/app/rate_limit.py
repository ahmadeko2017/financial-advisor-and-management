import time
from collections import deque
from typing import Deque, Dict

from fastapi import HTTPException, status

# Simple in-memory rate limiter per user + scope.
_buckets: Dict[str, Deque[float]] = {}


def check_rate_limit(user_id: str, scope: str, limit: int = 60, window_seconds: int = 60) -> None:
    """
    Raises HTTP 429 if user exceeds `limit` requests in rolling `window_seconds`.
    Intended for light protection; replace with Redis/gateway in production.
    """
    now = time.time()
    key = f"{user_id}:{scope}"
    bucket = _buckets.get(key)
    if bucket is None:
        bucket = deque()
        _buckets[key] = bucket

    # Drop expired timestamps
    cutoff = now - window_seconds
    while bucket and bucket[0] <= cutoff:
        bucket.popleft()

    if len(bucket) >= limit:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded, try again shortly",
        )

    bucket.append(now)
