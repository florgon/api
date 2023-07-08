"""
    Prometheus metrics expose instrumentator installation.
"""

from typing import Callable

try:
    from prometheus_fastapi_instrumentator.instrumentation import (
        PrometheusFastApiInstrumentator,
    )
except ImportError:
    module_installed = False
else:
    module_installed = True

from fastapi import FastAPI
from app.config import get_settings, get_logger


def prometheus_metrics_on_startup(_app: FastAPI) -> Callable:
    """
    Exposes prometheus metrics via intstrumentator.
    TODO: Allow prometheus to be more configured via settings.
    """

    setup_hook = lambda *_: None
    logger = get_logger()
    if not get_settings().prometheus_metrics_exposed:
        logger.info(
            "[prometheus] Skipping exposing metrics as disabled with `prometheus_metrics_exposed`!"
        )
    elif not module_installed:
        logger.warning(
            "[prometheus] You are enabled `prometheus_metrics_exposed`"
            " but `prometheus_fastapi_instrumentator` is not installed in the system!"
        )
    else:
        logger.info("[prometheus] Initialising instrumentator...")
        setup_hook = (
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
    return setup_hook
