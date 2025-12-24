import contextvars
from typing import Optional
import uuid

_correlation_id_var = contextvars.ContextVar("correlation_id", default=None)
_run_id_var = contextvars.ContextVar("run_id", default=None)

def generate_correlation_id() -> str:
    return str(uuid.uuid4())

def get_correlation_id() -> Optional[str]:
    return _correlation_id_var.get()

def get_run_id() -> Optional[str]:
    return _run_id_var.get()

class RequestContext:
    def __init__(self, correlation_id: Optional[str] = None, run_id: Optional[str] = None):
        self.correlation_id = correlation_id or generate_correlation_id()
        self.run_id = run_id
        self.token_corr = None
        self.token_run = None

    def __enter__(self):
        self.token_corr = _correlation_id_var.set(self.correlation_id)
        if self.run_id:
            self.token_run = _run_id_var.set(self.run_id)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.token_corr:
            _correlation_id_var.reset(self.token_corr)
        if self.token_run:
            _run_id_var.reset(self.token_run)
