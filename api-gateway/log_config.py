import os
import sys
import json
import logging
import queue
import contextvars
from datetime import datetime, timezone
from logging.handlers import QueueHandler, QueueListener

correlation_id_ctx = contextvars.ContextVar("correlation_id", default="")

class CorrelationIdFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        record.correlation_id = correlation_id_ctx.get()
        return True
    
class JsonFormatter(logging.Formatter):

    def __init__(self, service_name: str):
        super().__init__()
        self.service_name = service_name

    def format(self, record: logging.LogRecord) -> str:
        zapis = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "service": self.service_name,
            "correlation_id": getattr(record, "correlation_id", ""),
            "message": record.getMessage(),
            "logger": record.name,
        }
        if record.exc_info:
            zapis["exception"] = self.formatException(record.exc_info)
        return json.dumps(zapis, ensure_ascii=False)


class LogstashTcpHandler(logging.Handler):

    def __init__(self, host: str, port: int, formatter: JsonFormatter):
        super().__init__()
        self.host = host
        self.port = port
        self.setFormatter(formatter)
        self._sock = None

    def _connect(self):
        import socket
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._sock.settimeout(2)
        self._sock.connect((self.host, self.port))

    def emit(self, record):
        try:
            if self._sock is None:
                self._connect()
            poruka = self.format(record) + "\n"
            self._sock.sendall(poruka.encode("utf-8"))
        except Exception:
            self._sock = None


# Cuvamo referencu na listener da ga GC ne pokupi
_listener = None


def setup_logging(service_name: str = None):
    global _listener

    service_name = service_name or os.getenv("SERVICE_NAME", "unknown-service")
    formatter = JsonFormatter(service_name)

    root = logging.getLogger()
    root.handlers.clear()
    root.setLevel(logging.INFO)

    # Stvarni handleri (stdout + opcioni Logstash) - njih pokrece pozadinski thread
    target_handlers = []

    stdout_handler = logging.StreamHandler(sys.stdout)
    stdout_handler.setFormatter(formatter)
    target_handlers.append(stdout_handler)

    logstash_host = os.getenv("LOGSTASH_HOST")
    logstash_port = int(os.getenv("LOGSTASH_PORT", "5000"))
    if logstash_host:
        target_handlers.append(LogstashTcpHandler(logstash_host, logstash_port, formatter))

    # Red + QueueHandler: log zapisi idu u red trenutno (bez mreze), 
    # a QueueListener ih u pozadinskom thread-u salje pravim handlerima.
    log_queue = queue.Queue(-1)

    queue_handler = QueueHandler(log_queue)
    queue_handler.addFilter(CorrelationIdFilter())

    root.addHandler(queue_handler)

    if _listener is not None:
        _listener.stop()
    _listener = QueueListener(log_queue, *target_handlers, respect_handler_level=True)
    _listener.start()

    return logging.getLogger(service_name)


def get_correlation_id() -> str:
    return correlation_id_ctx.get()


def set_correlation_id(corr_id: str):
    correlation_id_ctx.set(corr_id or "")


async def correlation_id_middleware(request, call_next):
    corr_id = request.headers.get("X-Correlation-ID", "")
    set_correlation_id(corr_id)
    response = await call_next(request)
    if corr_id:
        response.headers["X-Correlation-ID"] = corr_id
    return response


def correlation_id_from_event(event: dict) -> str:
    if isinstance(event, dict):
        return event.get("correlation_id", "")
    return ""