"""
    Prometheus metrics expose instrumentator installation.
"""
from typing import Callable

try:
    from prometheus_fastapi_instrumentator.instrumentation import (
        PrometheusFastApiInstrumentator,
    )
except ImportError:
    prometheus_instrumentator_installed = False
else:
    prometheus_instrumentator_installed = True

from fastapi import FastAPI
from app.config import get_settings, get_logger


def prometheus_metrics_on_startup(_app: FastAPI) -> None | Callable:
    """
    Exposes prometheus metrics via intstrumentator if
    """
    settings = get_settings()
    logger = get_logger()
    if not settings.prometheus_metrics_exposed:
        logger.info(
            "[fastapi_prometheus] Skipping exposing metrics as it is disabled with `prometheus_metrics_exposed`!"
        )
        return None

    if not prometheus_instrumentator_installed:
        get_logger().warn(
            "[fastapi_prometheus] You are enabled `prometheus_metrics_exposed`"
            " but `prometheus_fastapi_instrumentator` is not installed in the system!"
        )
        return None

    get_logger().info("[fastapi_prometheus] Initialising instrumentator...")
    return (
        lambda: PrometheusFastApiInstrumentator()
        .instrument(app=_app)
        .expose(
            app=_app,
            should_gzip=False,
            endpoint="/metrics",
            include_in_schema=False,
            tags=None,
        )
    )
