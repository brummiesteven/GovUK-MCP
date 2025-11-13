"""Rate limiting implementation using token bucket algorithm.

This module provides thread-safe rate limiting for API endpoints with configurable
request rates per minute. It tracks requests per endpoint/key and returns quota
information including remaining tokens and reset times.

The token bucket algorithm allows for burst traffic while maintaining average rates,
making it ideal for API rate limiting scenarios.
"""

import time
import threading
from typing import Dict, Optional, Tuple, Callable, Any
from dataclasses import dataclass, field
from functools import wraps
from datetime import datetime, timedelta


@dataclass
class TokenBucket:
    """Token bucket for rate limiting using the token bucket algorithm.

    The token bucket algorithm allows requests up to a maximum burst size,
    refilling tokens at a constant rate. This provides smooth rate limiting
    while allowing temporary bursts of traffic.

    Attributes:
        capacity: Maximum number of tokens (requests) the bucket can hold
        tokens: Current number of available tokens
        rate: Number of tokens added per second
        last_refill: Timestamp of last token refill
        lock: Thread lock for concurrent access safety
    """
    capacity: float
    tokens: float
    rate: float  # tokens per second
    last_refill: float = field(default_factory=time.time)
    lock: threading.Lock = field(default_factory=threading.Lock)

    def _refill(self) -> None:
        """Refill tokens based on time elapsed since last refill.

        This method should only be called while holding the lock.
        """
        now = time.time()
        elapsed = now - self.last_refill

        # Add tokens based on elapsed time
        new_tokens = elapsed * self.rate
        self.tokens = min(self.capacity, self.tokens + new_tokens)
        self.last_refill = now

    def consume(self, tokens: float = 1.0) -> Tuple[bool, float, float]:
        """Attempt to consume tokens from the bucket.

        Args:
            tokens: Number of tokens to consume (default: 1.0)

        Returns:
            Tuple of (success, remaining_tokens, reset_time):
                - success: Whether the tokens were successfully consumed
                - remaining_tokens: Number of tokens remaining after consumption
                - reset_time: Unix timestamp when bucket will be full
        """
        with self.lock:
            self._refill()

            if self.tokens >= tokens:
                self.tokens -= tokens
                remaining = self.tokens
                # Calculate when bucket will be full
                time_to_full = (self.capacity - self.tokens) / self.rate
                reset_time = time.time() + time_to_full
                return True, remaining, reset_time
            else:
                # Calculate how long until we have enough tokens
                tokens_needed = tokens - self.tokens
                wait_time = tokens_needed / self.rate
                reset_time = time.time() + wait_time
                return False, self.tokens, reset_time

    def peek(self) -> Tuple[float, float]:
        """Check current token count without consuming.

        Returns:
            Tuple of (available_tokens, reset_time):
                - available_tokens: Current number of tokens
                - reset_time: Unix timestamp when bucket will be full
        """
        with self.lock:
            self._refill()
            time_to_full = (self.capacity - self.tokens) / self.rate
            reset_time = time.time() + time_to_full
            return self.tokens, reset_time


class RateLimiter:
    """Thread-safe rate limiter using token bucket algorithm.

    Tracks rate limits per endpoint/key combination. Each unique endpoint gets
    its own token bucket with configurable capacity and refill rate.

    Example:
        >>> limiter = RateLimiter()
        >>> # Check if request is allowed
        >>> allowed, info = limiter.check_limit("mot_api", requests_per_minute=120)
        >>> if allowed:
        ...     # Make API call
        ...     pass
        >>> else:
        ...     print(f"Rate limited. Retry after {info['retry_after']} seconds")
    """

    # Default rate limits based on actual API limits (requests per minute)
    DEFAULT_LIMITS = {
        "mot_api": 120,              # MOT API: 120 req/min
        "companies_house": 120,       # Companies House: 600 req/5min = 120 req/min
        "tfl": 500,                   # TfL: 500 req/min
        "default": 60,                # Default: 60 req/min for other APIs
    }

    def __init__(self):
        """Initialize the rate limiter with empty bucket storage."""
        self._buckets: Dict[str, TokenBucket] = {}
        self._lock = threading.Lock()

    def _get_bucket(self, endpoint: str, requests_per_minute: Optional[int] = None) -> TokenBucket:
        """Get or create a token bucket for an endpoint.

        Args:
            endpoint: Unique identifier for the endpoint (e.g., "mot_api")
            requests_per_minute: Rate limit in requests per minute.
                                If None, uses default for endpoint.

        Returns:
            TokenBucket instance for the endpoint
        """
        with self._lock:
            if endpoint not in self._buckets:
                # Determine rate limit
                if requests_per_minute is None:
                    requests_per_minute = self.DEFAULT_LIMITS.get(
                        endpoint,
                        self.DEFAULT_LIMITS["default"]
                    )

                # Convert to requests per second
                rate = requests_per_minute / 60.0

                # Create bucket with capacity equal to rate
                # This allows burst up to the per-minute limit
                self._buckets[endpoint] = TokenBucket(
                    capacity=requests_per_minute,
                    tokens=requests_per_minute,  # Start full
                    rate=rate
                )

            return self._buckets[endpoint]

    def check_limit(
        self,
        endpoint: str,
        requests_per_minute: Optional[int] = None,
        tokens: float = 1.0
    ) -> Tuple[bool, Dict[str, Any]]:
        """Check if a request is allowed under rate limit.

        Args:
            endpoint: Unique identifier for the endpoint
            requests_per_minute: Optional custom rate limit
            tokens: Number of tokens to consume (default: 1.0)

        Returns:
            Tuple of (allowed, info) where:
                - allowed: Boolean indicating if request is allowed
                - info: Dictionary with rate limit information:
                    - remaining: Number of requests remaining
                    - reset_time: ISO timestamp when limit resets
                    - retry_after: Seconds to wait before retry (if not allowed)
        """
        bucket = self._get_bucket(endpoint, requests_per_minute)
        success, remaining, reset_time = bucket.consume(tokens)

        reset_datetime = datetime.fromtimestamp(reset_time)

        info = {
            "remaining": int(remaining),
            "reset_time": reset_datetime.isoformat(),
            "limit": int(bucket.capacity),
        }

        if not success:
            info["retry_after"] = int(reset_time - time.time()) + 1

        return success, info

    def get_status(self, endpoint: str) -> Dict[str, Any]:
        """Get current rate limit status for an endpoint.

        Args:
            endpoint: Unique identifier for the endpoint

        Returns:
            Dictionary with current status:
                - available: Number of requests currently available
                - limit: Maximum requests per minute
                - reset_time: ISO timestamp when limit resets to full
        """
        with self._lock:
            if endpoint not in self._buckets:
                # Return default limit info if bucket doesn't exist yet
                limit = self.DEFAULT_LIMITS.get(endpoint, self.DEFAULT_LIMITS["default"])
                return {
                    "available": limit,
                    "limit": limit,
                    "reset_time": datetime.now().isoformat()
                }

        bucket = self._buckets[endpoint]
        available, reset_time = bucket.peek()

        return {
            "available": int(available),
            "limit": int(bucket.capacity),
            "reset_time": datetime.fromtimestamp(reset_time).isoformat()
        }

    def reset(self, endpoint: Optional[str] = None) -> None:
        """Reset rate limits for testing or manual intervention.

        Args:
            endpoint: Specific endpoint to reset, or None to reset all
        """
        with self._lock:
            if endpoint:
                if endpoint in self._buckets:
                    bucket = self._buckets[endpoint]
                    with bucket.lock:
                        bucket.tokens = bucket.capacity
                        bucket.last_refill = time.time()
            else:
                # Reset all buckets
                for bucket in self._buckets.values():
                    with bucket.lock:
                        bucket.tokens = bucket.capacity
                        bucket.last_refill = time.time()


# Global rate limiter instance
_global_limiter = RateLimiter()


def rate_limit(
    endpoint: str,
    requests_per_minute: Optional[int] = None,
    limiter: Optional[RateLimiter] = None
) -> Callable:
    """Decorator to apply rate limiting to tool functions.

    This decorator wraps tool functions to enforce rate limits. If the limit
    is exceeded, it returns an error dictionary instead of calling the function.

    Args:
        endpoint: Unique identifier for the endpoint being rate limited
        requests_per_minute: Optional custom rate limit (default: uses endpoint default)
        limiter: Optional custom RateLimiter instance (default: uses global limiter)

    Returns:
        Decorator function that wraps the tool function

    Example:
        >>> @rate_limit("mot_api", requests_per_minute=120)
        ... def check_mot(registration):
        ...     # API call here
        ...     pass
    """
    if limiter is None:
        limiter = _global_limiter

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Dict[str, Any]:
            # Check rate limit
            allowed, info = limiter.check_limit(endpoint, requests_per_minute)

            if not allowed:
                # Rate limit exceeded - return error with retry information
                retry_after = info.get("retry_after", 60)
                reset_time = info.get("reset_time", "")

                return {
                    "error": f"Rate limit exceeded for {endpoint}",
                    "error_type": "rate_limit_exceeded",
                    "retry_after": retry_after,
                    "reset_time": reset_time,
                    "limit": info.get("limit"),
                    "message": f"Please retry after {retry_after} seconds"
                }

            # Rate limit OK - call the original function
            result = func(*args, **kwargs)

            # Add rate limit info to successful responses
            if isinstance(result, dict) and "error" not in result:
                result["rate_limit"] = {
                    "remaining": info.get("remaining"),
                    "limit": info.get("limit"),
                    "reset_time": info.get("reset_time")
                }

            return result

        return wrapper
    return decorator


def get_limiter() -> RateLimiter:
    """Get the global rate limiter instance.

    Returns:
        Global RateLimiter instance
    """
    return _global_limiter


# Convenience functions for checking limits without decorator

def check_mot_limit() -> Tuple[bool, Dict[str, Any]]:
    """Check MOT API rate limit (120 req/min).

    Returns:
        Tuple of (allowed, info) with rate limit status
    """
    return _global_limiter.check_limit("mot_api", requests_per_minute=120)


def check_companies_house_limit() -> Tuple[bool, Dict[str, Any]]:
    """Check Companies House API rate limit (600 req/5min = 120 req/min).

    Returns:
        Tuple of (allowed, info) with rate limit status
    """
    return _global_limiter.check_limit("companies_house", requests_per_minute=120)


def check_tfl_limit() -> Tuple[bool, Dict[str, Any]]:
    """Check TfL API rate limit (500 req/min).

    Returns:
        Tuple of (allowed, info) with rate limit status
    """
    return _global_limiter.check_limit("tfl", requests_per_minute=500)


def check_default_limit(endpoint: str) -> Tuple[bool, Dict[str, Any]]:
    """Check default rate limit (60 req/min) for any endpoint.

    Args:
        endpoint: Unique identifier for the endpoint

    Returns:
        Tuple of (allowed, info) with rate limit status
    """
    return _global_limiter.check_limit(endpoint, requests_per_minute=60)
