# pylint: disable=unused-argument
"""
    Test for webhook service.
"""
import time
import socket
import multiprocessing
import hmac
import hashlib

import uvicorn
import pytest
import fastapi
from app.services.webhooks import send_http_webhook_event

SERVER_HOST = "127.0.0.1"
SERVER_PORT = 8001


@pytest.fixture(autouse=True, scope="session")
def webhook_server():
    """
    Runner for target webhook server with threading.
    """
    p = multiprocessing.Process(
        target=_webhook_target_server, args=(SERVER_HOST, SERVER_PORT)
    )
    p.start()
    yield
    p.terminate()


def _webhook_target_server(host: str, port: int) -> None:
    """
    FastAPI webhook target server.
    """
    app = fastapi.FastAPI()

    @app.post("/")
    async def _(request: fastapi.Request):
        payload = await request.body()
        payload_hash = hmac.new(payload, payload, hashlib.sha256).hexdigest()
        return fastapi.Response(headers={"x-payload-hash": payload_hash})

    uvicorn.run(app, host=host, port=port)


def test_send_and_accept_webhook(
    webhook_server,
):  # pylint: disable=redefined-outer-name:
    """
    Test send data and accept back for webhook.
    """
    result = 1
    while result:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex((SERVER_HOST, SERVER_PORT))
        time.sleep(0.1)

    assert send_http_webhook_event(
        url=f"http://{SERVER_HOST}:{SERVER_PORT}",
        event_type="pytest_event_name",
        data={"is_pytest": True, "some_stuff": "hi!"},
    )
