"""Gunicorn production configuration"""
import os
import multiprocessing

# Server socket
bind = f"0.0.0.0:{os.environ.get('PORT', '5000')}"
backlog = 2048

# Worker processes
workers = int(os.environ.get('GUNICORN_WORKERS', multiprocessing.cpu_count() * 2 + 1))
worker_class = 'sync'
worker_connections = 1000
max_requests = 1000
max_requests_jitter = 50
timeout = 30
keepalive = 2

# Process naming
proc_name = 'house_price_api'

# Logging
accesslog = '-'
errorlog = '-'
loglevel = os.environ.get('LOG_LEVEL', 'info')
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# Server mechanics
daemon = False
pidfile = None
umask = 0
user = None
group = None
tmp_upload_dir = None

# Security
limit_request_line = 4094
limit_request_fields = 100
limit_request_field_size = 8190

# Enable preload to save memory
preload_app = True

# Restart workers gracefully
graceful_timeout = 30

def on_starting(server):
    """Called just before the master process is initialized."""
    server.log.info("Starting Gunicorn server...")

def on_reload(server):
    """Called when a worker is reloaded."""
    server.log.info("Reloading Gunicorn server...")

def when_ready(server):
    """Called just after the server is started."""
    server.log.info("Gunicorn server is ready. Spawning workers...")

def on_exit(server):
    """Called just before exiting Gunicorn."""
    server.log.info("Shutting down Gunicorn server...")

def worker_int(worker):
    """Called when a worker receives the SIGINT or SIGQUIT signal."""
    worker.log.info("Worker received SIGINT or SIGQUIT")

def worker_abort(worker):
    """Called when a worker receives the SIGABRT signal."""
    worker.log.warning("Worker received SIGABRT - Aborting")
