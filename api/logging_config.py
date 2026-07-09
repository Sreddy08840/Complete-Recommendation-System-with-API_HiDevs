
import logging
import sys


class StructuredFormatter(logging.Formatter):
    """
    Custom formatter to include structured fields in log messages.
    """
    def format(self, record: logging.LogRecord) -> str:
        # Build base message
        base_message = super().format(record)
        
        # Add structured fields if they exist
        structured_fields = []
        if hasattr(record, "request_id"):
            structured_fields.append(f"request_id={record.request_id}")
        if hasattr(record, "method"):
            structured_fields.append(f"method={record.method}")
        if hasattr(record, "url"):
            structured_fields.append(f"url={record.url}")
        if hasattr(record, "status_code"):
            structured_fields.append(f"status_code={record.status_code}")
        if hasattr(record, "response_time_ms"):
            structured_fields.append(f"response_time_ms={record.response_time_ms}")
        
        if structured_fields:
            return f"{base_message} | {' '.join(structured_fields)}"
        return base_message


def setup_logging(level: int = logging.INFO) -> None:
    """
    Configure production-ready logging for the application.
    
    Args:
        level: Logging level (default: logging.INFO)
    """
    # Configure root logger
    logger = logging.getLogger()
    logger.setLevel(level)
    
    # Remove existing handlers to avoid duplicates
    logger.handlers.clear()
    
    # Create console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    
    # Define log format with custom formatter
    formatter = StructuredFormatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    console_handler.setFormatter(formatter)
    
    # Add handler to root logger
    logger.addHandler(console_handler)
    
    # Set level for specific loggers
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("uvicorn.error").setLevel(logging.WARNING)

