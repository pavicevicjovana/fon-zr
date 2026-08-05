import os
import sys
import json
import logging
import contextvars
from datetime import datetime, timezone
from logging.handlers import SocketHandler

correlation_id_ctx = contextvars.ContextVar("correlation_id", default="")


class JsonFormatter(logging.Formatter):


    def __init__(self, service_name: str):
        super().__init__()
        self.service_name = service_name


    def format(self, record: logging.LogRecord) -> str:
        zapis = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "service": self.service_name,
            "correlation_id": correlation_id_ctx.get(),
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
 
 
def setup_logging(service_name: str = None):
    
    service_name = service_name or os.getenv("SERVICE_NAME", "unknown-service")
    formatter = JsonFormatter(service_name)
 
    root = logging.getLogger()
    root.handlers.clear()
    root.setLevel(logging.INFO)
 
    stdout_handler = logging.StreamHandler(sys.stdout)
    stdout_handler.setFormatter(formatter)
    root.addHandler(stdout_handler)
 
    logstash_host = os.getenv("LOGSTASH_HOST")
    logstash_port = int(os.getenv("LOGSTASH_PORT", "5000"))
    if logstash_host:
        root.addHandler(LogstashTcpHandler(logstash_host, logstash_port, formatter))
 
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