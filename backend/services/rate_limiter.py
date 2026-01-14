"""
Rate Limiter - Redis-based rate limiting for email and SMS sending

CRC: crc-RateLimiter.md
Seq: seq-email-process.md, seq-sms-process.md
"""
import redis
import os
import time
from dotenv import load_dotenv

load_dotenv()


class RateLimiter:
    """
    Redis-based rate limiter for email and SMS sending

    Uses sliding window counter pattern with Redis INCR and EXPIRE
    """

    def __init__(self):
        redis_url = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
        self.redis = redis.from_url(redis_url)

        # Configurable limits (from environment or defaults)
        self.email_rate_limit = int(os.getenv('EMAIL_RATE_LIMIT', 100))  # per minute
        self.sms_rate_limit = int(os.getenv('SMS_RATE_LIMIT', 10))       # per minute
        self.window_size = 60  # 60 seconds

    def _get_key(self, campaign_id, msg_type):
        """Generate Redis key for rate counter"""
        return f"rate:{msg_type}:{campaign_id}"

    def check_email_rate(self, campaign_id):
        """Check if email can be sent within rate limit"""
        key = self._get_key(campaign_id, 'email')
        current = self.redis.get(key)
        return current is None or int(current) < self.email_rate_limit

    def check_sms_rate(self, campaign_id):
        """Check if SMS can be sent within rate limit"""
        key = self._get_key(campaign_id, 'sms')
        current = self.redis.get(key)
        return current is None or int(current) < self.sms_rate_limit

    def increment_email_count(self, campaign_id):
        """Record email sent"""
        key = self._get_key(campaign_id, 'email')
        pipe = self.redis.pipeline()
        pipe.incr(key)
        pipe.expire(key, self.window_size)
        pipe.execute()

    def increment_sms_count(self, campaign_id):
        """Record SMS sent"""
        key = self._get_key(campaign_id, 'sms')
        pipe = self.redis.pipeline()
        pipe.incr(key)
        pipe.expire(key, self.window_size)
        pipe.execute()

    def get_current_rate(self, campaign_id, msg_type):
        """Return current send velocity"""
        key = self._get_key(campaign_id, msg_type)
        current = self.redis.get(key)
        return int(current) if current else 0

    def wait_if_needed(self, campaign_id, msg_type):
        """Block until rate allows send"""
        limit = self.email_rate_limit if msg_type == 'email' else self.sms_rate_limit

        while True:
            key = self._get_key(campaign_id, msg_type)
            current = self.redis.get(key)

            if current is None or int(current) < limit:
                return  # OK to send

            # Get TTL to know when counter resets
            ttl = self.redis.ttl(key)
            if ttl > 0:
                # Sleep for remaining time (max 5 seconds at a time)
                time.sleep(min(ttl, 5))
            else:
                return  # Key expired, OK to send

    def reset_counters(self, campaign_id):
        """Clear rate counters (on campaign complete)"""
        self.redis.delete(self._get_key(campaign_id, 'email'))
        self.redis.delete(self._get_key(campaign_id, 'sms'))
