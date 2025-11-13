"""Tests for rate limiter implementation."""

import time
import pytest
import threading
from datetime import datetime
from gov_uk_mcp.rate_limiter import (
    RateLimiter,
    TokenBucket,
    rate_limit,
    get_limiter,
    check_mot_limit,
    check_companies_house_limit,
    check_tfl_limit,
    check_default_limit,
)


class TestTokenBucket:
    """Test cases for TokenBucket class."""

    def test_bucket_initialization(self):
        """Test bucket initializes with correct values."""
        bucket = TokenBucket(capacity=100, tokens=100, rate=10)
        assert bucket.capacity == 100
        assert bucket.tokens == 100
        assert bucket.rate == 10

    def test_consume_tokens_success(self):
        """Test successful token consumption."""
        bucket = TokenBucket(capacity=100, tokens=100, rate=10)
        success, remaining, reset_time = bucket.consume(10)

        assert success is True
        assert remaining == 90
        assert reset_time > time.time()

    def test_consume_tokens_insufficient(self):
        """Test token consumption fails when insufficient tokens."""
        bucket = TokenBucket(capacity=100, tokens=5, rate=10)
        success, remaining, reset_time = bucket.consume(10)

        assert success is False
        assert remaining == 5
        assert reset_time > time.time()

    def test_token_refill(self):
        """Test tokens refill over time."""
        bucket = TokenBucket(capacity=100, tokens=50, rate=10)

        # Wait for tokens to refill (0.5 seconds = 5 tokens at rate 10/sec)
        time.sleep(0.5)

        available, _ = bucket.peek()
        assert available >= 54  # Should have ~55 tokens (allow small variance)
        assert available <= 56

    def test_bucket_capacity_limit(self):
        """Test bucket doesn't exceed capacity during refill."""
        bucket = TokenBucket(capacity=100, tokens=100, rate=10)

        # Wait and check - should not exceed capacity
        time.sleep(1.0)
        available, _ = bucket.peek()
        assert available == 100

    def test_peek_doesnt_consume(self):
        """Test peek operation doesn't consume tokens."""
        bucket = TokenBucket(capacity=100, tokens=50, rate=10)

        available_before, _ = bucket.peek()
        available_after, _ = bucket.peek()

        assert available_before == available_after == 50

    def test_concurrent_consumption(self):
        """Test thread-safe concurrent token consumption."""
        bucket = TokenBucket(capacity=100, tokens=100, rate=10)
        results = []

        def consume_token():
            success, _, _ = bucket.consume(1)
            results.append(success)

        # Try to consume 100 tokens concurrently
        threads = [threading.Thread(target=consume_token) for _ in range(100)]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()

        # All 100 should succeed
        assert sum(results) == 100
        assert bucket.tokens == 0


class TestRateLimiter:
    """Test cases for RateLimiter class."""

    def test_rate_limiter_initialization(self):
        """Test rate limiter initializes correctly."""
        limiter = RateLimiter()
        assert limiter._buckets == {}

    def test_check_limit_creates_bucket(self):
        """Test check_limit creates bucket on first call."""
        limiter = RateLimiter()
        allowed, info = limiter.check_limit("test_endpoint", requests_per_minute=60)

        assert allowed is True
        assert info["remaining"] == 59
        assert info["limit"] == 60
        assert "reset_time" in info

    def test_check_limit_respects_custom_rate(self):
        """Test custom rate limits are respected."""
        limiter = RateLimiter()
        allowed, info = limiter.check_limit("custom", requests_per_minute=120)

        assert allowed is True
        assert info["limit"] == 120
        assert info["remaining"] == 119

    def test_check_limit_uses_default_limits(self):
        """Test default limits are used for known endpoints."""
        limiter = RateLimiter()

        # Test MOT default (120 req/min)
        allowed, info = limiter.check_limit("mot_api")
        assert info["limit"] == 120

        # Test Companies House default (120 req/min)
        allowed, info = limiter.check_limit("companies_house")
        assert info["limit"] == 120

        # Test TfL default (500 req/min)
        allowed, info = limiter.check_limit("tfl")
        assert info["limit"] == 500

        # Test unknown endpoint (60 req/min default)
        allowed, info = limiter.check_limit("unknown")
        assert info["limit"] == 60

    def test_rate_limit_exceeded(self):
        """Test rate limit exceeded returns correct error info."""
        limiter = RateLimiter()

        # Consume all tokens
        for _ in range(10):
            limiter.check_limit("test", requests_per_minute=10)

        # Next request should be blocked
        allowed, info = limiter.check_limit("test", requests_per_minute=10)

        assert allowed is False
        assert "retry_after" in info
        assert info["retry_after"] > 0
        assert info["remaining"] == 0

    def test_get_status(self):
        """Test get_status returns current limit status."""
        limiter = RateLimiter()

        # Make some requests
        limiter.check_limit("test", requests_per_minute=100)
        limiter.check_limit("test", requests_per_minute=100)

        status = limiter.get_status("test")

        assert status["available"] == 98
        assert status["limit"] == 100
        assert "reset_time" in status

    def test_get_status_nonexistent_endpoint(self):
        """Test get_status for endpoint that hasn't been used yet."""
        limiter = RateLimiter()
        status = limiter.get_status("nonexistent")

        assert status["available"] == 60  # Default limit
        assert status["limit"] == 60

    def test_reset_specific_endpoint(self):
        """Test reset for specific endpoint."""
        limiter = RateLimiter()

        # Consume some tokens
        limiter.check_limit("test", requests_per_minute=100)
        limiter.check_limit("test", requests_per_minute=100)

        status_before = limiter.get_status("test")
        assert status_before["available"] == 98

        # Reset the endpoint
        limiter.reset("test")

        status_after = limiter.get_status("test")
        assert status_after["available"] == 100

    def test_reset_all_endpoints(self):
        """Test reset all endpoints."""
        limiter = RateLimiter()

        # Create multiple endpoints with consumed tokens
        limiter.check_limit("test1", requests_per_minute=100)
        limiter.check_limit("test2", requests_per_minute=100)

        # Reset all
        limiter.reset()

        # Both should be full
        assert limiter.get_status("test1")["available"] == 100
        assert limiter.get_status("test2")["available"] == 100

    def test_concurrent_requests(self):
        """Test concurrent requests to same endpoint."""
        limiter = RateLimiter()
        results = []

        def make_request():
            allowed, info = limiter.check_limit("concurrent_test", requests_per_minute=50)
            results.append(allowed)

        # Make 100 concurrent requests (limit is 50)
        threads = [threading.Thread(target=make_request) for _ in range(100)]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()

        # Exactly 50 should succeed
        assert sum(results) == 50

    def test_separate_endpoint_limits(self):
        """Test different endpoints have independent limits."""
        limiter = RateLimiter()

        # Exhaust endpoint1
        for _ in range(10):
            limiter.check_limit("endpoint1", requests_per_minute=10)

        # endpoint2 should still work
        allowed, info = limiter.check_limit("endpoint2", requests_per_minute=10)
        assert allowed is True
        assert info["remaining"] == 9


class TestRateLimitDecorator:
    """Test cases for rate_limit decorator."""

    def test_decorator_allows_request(self):
        """Test decorator allows request under limit."""
        limiter = RateLimiter()

        @rate_limit("test", requests_per_minute=60, limiter=limiter)
        def test_function():
            return {"status": "success", "data": "test"}

        result = test_function()

        assert result["status"] == "success"
        assert result["data"] == "test"
        assert "rate_limit" in result
        assert result["rate_limit"]["remaining"] == 59

    def test_decorator_blocks_request(self):
        """Test decorator blocks request over limit."""
        limiter = RateLimiter()

        @rate_limit("test", requests_per_minute=2, limiter=limiter)
        def test_function():
            return {"status": "success"}

        # Exhaust limit
        test_function()
        test_function()

        # Should be blocked
        result = test_function()

        assert "error" in result
        assert result["error_type"] == "rate_limit_exceeded"
        assert "retry_after" in result
        assert "reset_time" in result

    def test_decorator_preserves_function_metadata(self):
        """Test decorator preserves original function metadata."""
        @rate_limit("test", requests_per_minute=60)
        def test_function():
            """Test function docstring."""
            pass

        assert test_function.__name__ == "test_function"
        assert test_function.__doc__ == "Test function docstring."

    def test_decorator_with_arguments(self):
        """Test decorator works with function arguments."""
        limiter = RateLimiter()

        @rate_limit("test", requests_per_minute=60, limiter=limiter)
        def test_function(arg1, arg2, kwarg1=None):
            return {"arg1": arg1, "arg2": arg2, "kwarg1": kwarg1}

        result = test_function("value1", "value2", kwarg1="kwvalue")

        assert result["arg1"] == "value1"
        assert result["arg2"] == "value2"
        assert result["kwarg1"] == "kwvalue"

    def test_decorator_error_response_format(self):
        """Test decorator error response has correct format."""
        limiter = RateLimiter()

        @rate_limit("test", requests_per_minute=1, limiter=limiter)
        def test_function():
            return {"status": "success"}

        # Exhaust limit
        test_function()

        # Get error response
        error = test_function()

        assert error["error_type"] == "rate_limit_exceeded"
        assert "test" in error["error"]
        assert isinstance(error["retry_after"], int)
        assert error["retry_after"] > 0
        assert error["limit"] == 1
        assert "message" in error


class TestConvenienceFunctions:
    """Test cases for convenience functions."""

    def test_check_mot_limit(self):
        """Test MOT API limit check."""
        # Reset global limiter
        get_limiter().reset()

        allowed, info = check_mot_limit()
        assert allowed is True
        assert info["limit"] == 120

    def test_check_companies_house_limit(self):
        """Test Companies House API limit check."""
        get_limiter().reset()

        allowed, info = check_companies_house_limit()
        assert allowed is True
        assert info["limit"] == 120

    def test_check_tfl_limit(self):
        """Test TfL API limit check."""
        get_limiter().reset()

        allowed, info = check_tfl_limit()
        assert allowed is True
        assert info["limit"] == 500

    def test_check_default_limit(self):
        """Test default limit check."""
        get_limiter().reset()

        allowed, info = check_default_limit("custom_endpoint")
        assert allowed is True
        assert info["limit"] == 60

    def test_get_limiter_returns_singleton(self):
        """Test get_limiter returns the same instance."""
        limiter1 = get_limiter()
        limiter2 = get_limiter()
        assert limiter1 is limiter2


class TestRealWorldScenarios:
    """Test real-world usage scenarios."""

    def test_burst_traffic(self):
        """Test handling of burst traffic."""
        limiter = RateLimiter()

        # Simulate burst of 50 requests (limit is 60/min)
        results = []
        for _ in range(50):
            allowed, _ = limiter.check_limit("burst_test", requests_per_minute=60)
            results.append(allowed)

        # All should succeed
        assert all(results)

        # 11 more should fail
        for _ in range(11):
            allowed, info = limiter.check_limit("burst_test", requests_per_minute=60)
            assert allowed is False

    def test_refill_allows_new_requests(self):
        """Test tokens refill and allow new requests."""
        limiter = RateLimiter()

        # Use 10 requests (10 req/min = 1 token per 6 seconds)
        for _ in range(10):
            limiter.check_limit("refill_test", requests_per_minute=10)

        # Should be blocked now
        allowed, _ = limiter.check_limit("refill_test", requests_per_minute=10)
        assert allowed is False

        # Wait for 1 second (should get ~1.67 tokens back at 10/min rate)
        time.sleep(1.0)

        # Should work now
        allowed, info = limiter.check_limit("refill_test", requests_per_minute=10)
        assert allowed is True

    def test_mixed_endpoint_usage(self):
        """Test realistic mixed usage of multiple endpoints."""
        limiter = RateLimiter()

        # Simulate real usage pattern
        for _ in range(50):
            limiter.check_limit("mot_api", requests_per_minute=120)

        for _ in range(200):
            limiter.check_limit("tfl", requests_per_minute=500)

        for _ in range(80):
            limiter.check_limit("companies_house", requests_per_minute=120)

        # Check status of each
        mot_status = limiter.get_status("mot_api")
        tfl_status = limiter.get_status("tfl")
        ch_status = limiter.get_status("companies_house")

        assert mot_status["available"] == 70  # 120 - 50
        assert tfl_status["available"] == 300  # 500 - 200
        assert ch_status["available"] == 40   # 120 - 80

    def test_rate_limit_info_in_response(self):
        """Test rate limit info is added to successful responses."""
        limiter = RateLimiter()

        @rate_limit("test", requests_per_minute=100, limiter=limiter)
        def api_call():
            return {"data": "success", "value": 42}

        result = api_call()

        assert result["data"] == "success"
        assert result["value"] == 42
        assert "rate_limit" in result
        assert result["rate_limit"]["remaining"] == 99
        assert result["rate_limit"]["limit"] == 100
        assert isinstance(result["rate_limit"]["reset_time"], str)

        # Verify reset_time is valid ISO format
        datetime.fromisoformat(result["rate_limit"]["reset_time"])
