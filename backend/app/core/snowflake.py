"""
Snowflake ID Generator
"""
import time
import threading


class SnowflakeIDGenerator:
    """
    Twitter Snowflake ID generator.
    64-bit ID: 1 bit sign | 41 bit timestamp | 5 bit datacenter | 5 bit worker | 12 bit sequence
    """

    EPOCH = 1704067200000  # 2024-01-01 00:00:00 UTC in milliseconds

    def __init__(self, datacenter_id: int = 1, worker_id: int = 1):
        if datacenter_id < 0 or datacenter_id > 31:
            raise ValueError("Datacenter ID must be between 0 and 31")
        if worker_id < 0 or worker_id > 31:
            raise ValueError("Worker ID must be between 0 and 31")

        self.datacenter_id = datacenter_id
        self.worker_id = worker_id
        self.sequence = 0
        self.last_timestamp = -1
        self._lock = threading.Lock()

    def _current_millis(self) -> int:
        return int(time.time() * 1000)

    def generate(self) -> int:
        with self._lock:
            timestamp = self._current_millis()

            if timestamp == self.last_timestamp:
                self.sequence = (self.sequence + 1) & 0xFFF  # 12 bits
                if self.sequence == 0:
                    while timestamp <= self.last_timestamp:
                        timestamp = self._current_millis()
            else:
                self.sequence = 0

            self.last_timestamp = timestamp

            return (
                ((timestamp - self.EPOCH) << 22)
                | (self.datacenter_id << 17)
                | (self.worker_id << 12)
                | self.sequence
            )


# Global instance
_generator = None


def get_snowflake_id() -> int:
    global _generator
    if _generator is None:
        from app.config import settings
        _generator = SnowflakeIDGenerator(
            datacenter_id=settings.SNOWFLAKE_DATACENTER_ID,
            worker_id=settings.SNOWFLAKE_WORKER_ID,
        )
    return _generator.generate()
