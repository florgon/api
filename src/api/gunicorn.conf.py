# pylint: disable=cyclic-import
# sourcery skip: remove-redundant-condition
"""
    Florgon API server `Gunicorn` process manager configuration file.
    All configuration settings that may be required or changes,
    located here, only not required fields are omitted.
    You can read official `Gunicorn` documentation with
    a list of all available settings:
    https://docs.gunicorn.org/en/latest/settings.html
"""

from multiprocessing import cpu_count

from pydantic import BaseSettings


class GunicornSettings(BaseSettings):
    """
    Environement settings reader.

    Information about the configuration is not provided here,
    please see the documentation for more configuration information.
    """

    proc_bind_host: str = "0.0.0.0"
    proc_bind_port: int = 80
    proc_log_to_stdout: bool = True
    proc_access_log: str | None = None
    proc_error_log: str | None = None
    proc_log_level: str = "info"
    proc_timeout: int = 30
    proc_debug_config: bool = False
    proc_name: str = "florgon-api-gunicorn"
    proc_overwrite_workers: int = 0


# ?TODO?: Read more about logs.
# TODO: Proxy headers in access log format.

settings = GunicornSettings()

# Logging.
# https://docs.gunicorn.org/en/latest/settings.html#logging
accesslog = "-" if settings.proc_log_to_stdout else settings.proc_access_log
errorlog = "-" if settings.proc_log_to_stdout else settings.proc_error_log
loglevel = (
    settings.proc_log_level
)  # (Default: Info) One of those: debug, info, warning, error, critical.
capture_output = (
    False
    if settings.proc_log_to_stdout
    else (settings.proc_access_log and settings.proc_error_log)
)  # (Default: False) Redirect stdout/stderr to specified file in errorlog.
logger_class = "gunicorn.glogging.Logger"
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s"'  # TODO: Proxy headers is being skipped?

# Debugging.
# https://docs.gunicorn.org/en/latest/settings.html#debugging
reload = False  # Should not be used.
reload_engine = "auto"
check_config = (
    settings.proc_debug_config
)  # Gunicorn will exit with information about config.
print_config = (
    settings.proc_debug_config
)  # Gunicorn will exit with information about config.

# Process naming.
# https://docs.gunicorn.org/en/latest/settings.html#process-naming#
proc_name = None  # Should be inherited from below.
default_proc_name = settings.proc_name

# Socket.
# https://docs.gunicorn.org/en/latest/settings.html#server-socket
bind = f"{settings.proc_bind_host}:{settings.proc_bind_port}"
backlog = 2048  # Default, maximal, relates to high-load. (Limit for pending clients that should be served next).

# Worker.
# https://docs.gunicorn.org/en/latest/settings.html#worker-processes
workers = (
    (2 * cpu_count() + 1)
    if settings.proc_overwrite_workers == 0
    else settings.proc_overwrite_workers
)  # (Default: 1). Generally in range (2-4 x ${NUM_CORES}).
worker_class = "uvicorn.workers.UvicornWorker"  # Not default, Uvicorn worker as we are using Uvicorn.
worker_connections = 1000  # Not affects, due to worker type.
threads = 1  # Not affects, as only works with `gthread` worker class.
max_requests = 32_000  # (Default: 0, no restart) Number of requests, after which worker will restart.
max_requests_jitter = (
    1_000  # Jitter for `max_requests` to not restart all workers at once.
)
timeout = (
    settings.proc_timeout
)  # Timeout after which worker request process marked as dead and restarts.
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
    # sourcery skip: replace-interpolation-with-fstring
    """Logger for pre-request."""
    worker.log.debug("%s %s" % (req.method, req.path))
