"""
BOLDR Self-Improving Customer Intelligence Engine
Rate Limiting Middleware — Token bucket rate limiter for FastAPI

Protects the API from abuse while allowing normal n8n workflow traffic.
Uses an in-memory token bucket per client IP with configurable limits.

Author: Steve Ng, Founder and CEO — Digital Futures Consultancy LLP
"""

import time
from collections import defaultdict
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware


class TokenBucket:
    """Token bucket rate limiter for a single client."""

    def __init__(self, rate: float, capacity: int):
        """
        Args:
            rate: Tokens added per second (e.g., 10 = 10 requests/sec sustained)
            capacity: Maximum burst capacity (e.g., 30 = allow 30 requests at once)
        """
        self.rate = rate
        self.capacity = capacity
        self.tokens = capacity
        self.last_refill = time.monotonic()

    def consume(self, tokens: int = 1) -> bool:
        """Try to consume tokens. Returns True if allowed, False if rate limited."""
        now = time.monotonic()
        elapsed = now - self.last_refill
        self.tokens = min(self.capacity, self.tokens + elapsed * self.rate)
        self.last_refill = now

        if self.tokens >= tokens:
            self.tokens -= tokens
            return True
        return False


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Rate limiting middleware for FastAPI.

    Configuration:
        - General API: 60 requests/minute per IP (1 req/sec sustained, burst of 30)
        - Intake endpoint: 30 requests/minute per IP (important to protect)
        - Stats/health: No limit (read-only, lightweight)

    Headers added to every response:
        - X-RateLimit-Limit: Maximum requests per window
        - X-RateLimit-Remaining: Requests remaining in current window
        - X-RateLimit-Reset: Seconds until window resets
    """

    # Rate limits per endpoint group
    RATE_LIMITS = {
        "intake": {"rate": 2.0, "capacity": 15},      # 2/sec sustained, 15 burst
        "general": {"rate": 5.0, "capacity": 30},      # 5/sec sustained, 30 burst
        "stats": {"rate": 10.0, "capacity": 60},        # 10/sec sustained, 60 burst (lightweight)
    }

    def __init__(self, app, rate_limit_response: bool = True):
        super().__init__(app)
        self.rate_limit_response = rate_limit_response
        self.buckets: dict[str, TokenBucket] = defaultdict(lambda: None)
        self._cleanup_interval = 300  # Clean up stale buckets every 5 minutes
        self._last_cleanup = time.monotonic()

    def _get_client_id(self, request: Request) -> str:
        """Get client identifier (IP address, or forwarded IP if behind proxy)."""
        forwarded = request.headers.get("X-Forwarded-For", "")
        if forwarded:
            return forwarded.split(",")[0].strip()
        return request.client.host if request.client else "unknown"

    def _get_endpoint_group(self, path: str) -> str:
        """Determine which rate limit group a path belongs to."""
        if "/intake" in path or "/intent" in path:
            return "intake"
        elif "/health" in path or "/stats" in path or "/audit" in path:
            return "stats"
        else:
            return "general"

    def _get_or_create_bucket(self, client_id: str, group: str) -> TokenBucket:
        """Get or create a token bucket for a client and endpoint group."""
        key = f"{client_id}:{group}"
        bucket = self.buckets.get(key)
        if bucket is None:
            config = self.RATE_LIMITS[group]
            bucket = TokenBucket(rate=config["rate"], capacity=config["capacity"])
            self.buckets[key] = bucket
        return bucket

    def _cleanup_stale_buckets(self):
        """Remove buckets that haven't been used recently."""
        now = time.monotonic()
        if now - self._last_cleanup < self._cleanup_interval:
            return
        stale_keys = []
        for key, bucket in self.buckets.items():
            # If bucket is full and hasn't been used recently, it's stale
            if bucket.tokens >= bucket.capacity and (now - bucket.last_refill) > self._cleanup_interval:
                stale_keys.append(key)
        for key in stale_keys:
            del self.buckets[key]
        self._last_cleanup = now

    async def dispatch(self, request: Request, call_next):
        """Process the request through rate limiting."""
        # Skip rate limiting for OPTIONS (CORS preflight)
        if request.method == "OPTIONS":
            return await call_next(request)

        client_id = self._get_client_id(request)
        group = self._get_endpoint_group(request.url.path)
        bucket = self._get_or_create_bucket(client_id, group)

        # Clean up stale buckets periodically
        self._cleanup_stale_buckets()

        # Try to consume a token
        allowed = bucket.consume(1)

        # Calculate remaining and reset
        config = self.RATE_LIMITS[group]
        remaining = int(bucket.tokens)
        reset_seconds = int((config["capacity"] - bucket.tokens) / config["rate"]) if bucket.tokens < config["capacity"] else 0

        if not allowed:
            if self.rate_limit_response:
                return Response(
                    content='{"detail":"Rate limit exceeded. Please try again later.","status_code":429}',
                    status_code=429,
                    media_type="application/json",
                    headers={
                        "X-RateLimit-Limit": str(config["capacity"]),
                        "X-RateLimit-Remaining": "0",
                        "X-RateLimit-Reset": str(reset_seconds),
                        "Retry-After": str(max(1, reset_seconds)),
                    }
                )

        # Process the request
        response = await call_next(request)

        # Add rate limit headers to successful responses
        response.headers["X-RateLimit-Limit"] = str(config["capacity"])
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        response.headers["X-RateLimit-Reset"] = str(reset_seconds)

        return response