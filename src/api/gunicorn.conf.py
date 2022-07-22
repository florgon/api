"""
    Gunicorn process manager configuration.
"""

# TODO: `.env` support?

proc_name = "florgon-api"

bind = "0.0.0.0:80"

timeout = 300

check_config = False
print_config = False

forwarded_allow_ips = "['127.0.0.1']"

threads = 1
workers = 4
worker_class = "uvicorn.workers.UvicornWorker"