import logging
import json
import sys
from datetime import datetime
from observability.context import get_correlation_id, get_run_id

class JSONFormatter(logging.Formatter):
    def format(self, record):
        log_record = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "service": "simulation-pipeline",
            "message": record.getMessage(),
            "logger": record.name,
            "correlation_id": get_correlation_id(),
            "run_id": get_run_id() 
        }
        
        # Add event fields if present in extra
        if hasattr(record, "event"):
            log_record["event"] = record.event
            
        if hasattr(record, "duration_ms"):
            log_record["duration_ms"] = record.duration_ms
            
        if record.exc_info:
            log_record["error"] = self.formatException(record.exc_info)
            
        return json.dumps(log_record)

def get_logger(name: str):
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    
    # Avoid adding multiple handlers if already configured
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        formatter = JSONFormatter()
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        
    return logger

def log_event(logger, event_name: str, message: str, **kwargs):
    """Helper to log an event with extra fields"""
    extra = {"event": event_name}
    extra.update(kwargs)
    logger.info(message, extra=extra)
