# Gunicorn configuration settings.

bind = ":8080"
workers = 4
worker_connections = 1000  # Max connections per worker
max_requests = 2048
max_requests_jitter = 256
preload_app = True
keepalive = 5  # Keepalive timeout
timeout = 180  # Worker timeout
graceful_timeout = 30  # Graceful shutdown timeout
# Disable access logging.
accesslog = None
control_socket = "/tmp/gunicorn.ctl"
