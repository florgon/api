# pylint: disable=cyclic-import
"""
    Florgon API server `Gunicorn` process manager configuration file.
    All configuration settings that may be required or changes,
    located here, only not required fields are omitted.
    You can read official `Gunicorn` documentation with
    a list of all available settings:
    https://docs.gunicorn.org/en/latest/settings.html

    Author: Kirill Zhosul (Florgon).
    Date: 07.31.22
"""

# Used for set workers count related to CPU cores.
# See `workers` field.
# Generally in range (2-4 x ${NUM_CORES}).
from multiprocessing import cpu_count

# TODO 07.31.22: Read more about logs.
# TODO 07.31.22: Proxy headers in access log format.
# TODO 07.31.22: Environment support?

# Entrance.
_bind_host = "0.0.0.0"
_bind_port = "80"
_log_to_stdout = True

# Logging.
# https://docs.gunicorn.org/en/latest/settings.html#logging
accesslog = "-" if _log_to_stdout else None
errorlog = "-" if _log_to_stdout else None
loglevel = (
    "info"  # (Default: Info) One of those: debug, info, warning, error, critical.
)
capture_output = (
    False if _log_to_stdout else False
)  # (Default: False) Redirect stdout/stderr to specified file in errorlog.
logger_class = "gunicorn.glogging.Logger"
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s"'  # Proxy headers is being skipped?

# Debugging.
# https://docs.gunicorn.org/en/latest/settings.html#debugging
reload = False  # Should not be used.
reload_engine = "auto"
check_config = False  # Gunicorn will exit with information about config.
print_config = False  # Gunicorn will exit with information about config.

# Process naming.
# https://docs.gunicorn.org/en/latest/settings.html#process-naming#
proc_name = None  # Should be inherited from below.
default_proc_name = "florgon-api-gunicorn"

# Socket.
# https://docs.gunicorn.org/en/latest/settings.html#server-socket
bind = f"{_bind_host}:{_bind_port}"
backlog = 2048  # Default, maximal, relates to high-load. (Limit for pending clients that should be served next).

# Worker.
# https://docs.gunicorn.org/en/latest/settings.html#worker-processes
workers = 2 * cpu_count() + 1  # (Default: 1). Generally in range (2-4 x ${NUM_CORES}).
worker_class = "uvicorn.workers.UvicornWorker"  # Not default, Uvicorn worker as we are using Uvicorn.
worker_connections = 1000  # Not affects, due to worker type.
threads = 1  # Not affects, as only works with `gthread` worker class.
max_requests = 32_000  # (Default: 0, no restart) Number of requests, after which worker will restart.
max_requests_jitter = (
    1_000  # Jitter for `max_requests` to not restart all workers at once.
)
timeout = 30  # Timeout after which worker request process marked as dead and restarts.
graceful_timeout = timeout  # Timeout to finish requests after exit.
keepalive = 2  # (Default: 2). Should be increased to 1-5 if being behing load balancer.

# Security.
# https://docs.gunicorn.org/en/latest/settings.html#security
# Notice, that this section should be handled by your proxy (like Nginx).
limit_request_line = 4094  # (Default). Limit for URL size.
limit_request_fields = 30  # (Default: 100). Limit for headers count.
limit_request_field_size = 2047  # (Default: 8190). Limit for header size.

# Server mechanics.
# https://docs.gunicorn.org/en/latest/settings.html#server-mechanics
preload_app = False  # (Default: False). Loads application code before worker fork. Saves a bit RAM and launch time. WARNING: Disable this as this will cause errors with forking database connections (database errors).
reuse_port = False
daemon = False  # (Default: False). Should process manager detach from terminal and used as background?
user = 1005  # OS.
group = 205  # OS.
umask = 0  # OS
secure_scheme_headers = {
    "X-FORWARDED-PROTOCOL": "ssl",
    "X-FORWARDED-PROTO": "https",
    "X-FORWARDED-SSL": "on",
}
forwarded_allow_ips = "*"  # (Default: 127.0.0.1). Complex field. https://docs.gunicorn.org/en/latest/settings.html#forwarded-allow-ips
proxy_allow_ips = "*"  # (Default: 127.0.0.1). Complex field. https://docs.gunicorn.org/en/latest/settings.html#proxy-allow-ips


# SSL.
# https://docs.gunicorn.org/en/latest/settings.html#ssl
# Notice, that this section should be handled by your proxy (like Nginx).
# Please read more Gunicorn documentation if You want to use SSL inside Gunicorn.
keyfile = None  # (Default: None)
certfile = None  # (Default: None)
ca_certs = None  # (Default: None)

# Hooks.
# https://docs.gunicorn.org/en/latest/settings.html#server-hooks
def pre_request(worker, req):
    """Logger for pre-request."""
    worker.log.debug("%s %s" % (req.method, req.path))
