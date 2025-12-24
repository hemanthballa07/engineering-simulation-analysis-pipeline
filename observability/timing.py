import time
from observability.logging import get_logger, log_event

logger = get_logger("timer")

class Timer:
    def __init__(self, event_name: str, description: str = ""):
        self.event_name = event_name
        self.description = description
        self.start_time = None

    def __enter__(self):
        self.start_time = time.time()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        duration_ms = (time.time() - self.start_time) * 1000
        status = "failed" if exc_type else "success"
        
        log_event(
            logger, 
            self.event_name, 
            f"{self.description} completed in {duration_ms:.2f}ms" if status == "success" else f"{self.description} failed after {duration_ms:.2f}ms",
            duration_ms=duration_ms,
            status=status
        )
