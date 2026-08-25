from collections import defaultdict
from time import monotonic
from threading import Lock


class RateLimiter:
    """Simple in-memory fixed-window rate limiter."""

    def __init__(
        self,
        max_requests: int = 20,
        window_seconds: int = 60,
    ) -> None:
        self.max_requests = max_requests
        self.window_seconds = window_seconds

        self._requests: dict[str, list[float]] = defaultdict(list)
        self._lock = Lock()

    def allow(self, client_id: str) -> bool:
        now = monotonic()
        window_start = now - self.window_seconds

        with self._lock:
            timestamps = self._requests[client_id]

            # Remove expired requests.
            self._requests[client_id] = [
                timestamp
                for timestamp in timestamps
                if timestamp > window_start
            ]

            timestamps = self._requests[client_id]

            if len(timestamps) >= self.max_requests:
                return False

            timestamps.append(now)

            return True