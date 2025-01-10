import time


class ExponentialBackOff:

    def __init__(self) -> None:
        self.backoff_time_bucket_index = 0
        # incremental backoff times on exceptions (1m, 2m, 4m, 8m, 16m, 32m)
        self.backoff_time_buckets = [60, 120, 240, 480, 960, 1920]
        self.next_timer = time.time()

    def reset_timer(self) -> None:
        self.backoff_time_bucket_index = 0

    def next_try_timer(self) -> float:
        """
        Returns the next backoff time
        """
        return self.next_timer

    def set_next_timer(self) -> None:
        """
        Sets next backoff timer
        """
        current_backoff_time = self.backoff_time_buckets[
            self.backoff_time_bucket_index]

        self.backoff_time_bucket_index = min(
            self.backoff_time_bucket_index + 1,
            len(self.backoff_time_buckets) - 1,
        )

        self.next_timer = time.time() + current_backoff_time
