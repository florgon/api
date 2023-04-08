"""
    Webhooks services.

    Provides features to work with webhooks that sends data FROM this API.
    Used for features like notifying external services about some events / data that occured inside this API-service.
"""

import time
import json
import hmac
import hashlib

import requests

WEBHOOK_RESPONSE_HASH_HEADER = "x-payload-hash"
WEBHOOK_ACCEPTED_STATUS_CODES = (200, 201, 202)
WEBHOOK_DEFAULT_HEADERS = {
    "Content-Type": "application/json",
    "User-Agent": "Mozilla/5.0 (compatible; Florgon-Webhooks/1.0; +https://florgon.com)",
}


def send_http_webhook_event(url: str, event_type: str, data: dict) -> bool:
    """
    Sends HTTP request to webhook and returning is event was processed by webhook or not (due to unavailable service that accepts data / event).
    """

    # Build payload as bytes.
    payload_as_bytes = _payload_to_json_bytes(
        {
            "object": "event",
            "event": event_type,
            "data": data,
            "created_at": time.time(),
        }
    )

    response = _send_webhook_request(url=url, payload=payload_as_bytes)
    if not response:
        return False

    # Response should contain that header to verify that data was accepted.
    payload_hash_response = response.headers[WEBHOOK_RESPONSE_HASH_HEADER]
    # Should be valid response or return False as failed response.
    return _payload_verifiy_hmac(payload_as_bytes, returned_hash=payload_hash_response)


def _send_webhook_request(url: str, payload: dict) -> requests.Response:
    """
    Sends HTTP request for webhook and returns response or None if failed to any reason.
    """
    try:
        webhook_response = requests.post(
            url=url, data=payload, headers=WEBHOOK_DEFAULT_HEADERS
        )
    except requests.exceptions.RequestException:
        # There is any exception caused while sending request to webhook or whatever.
        # just mark as failed due to unavailability to check that response is fine.
        return None

    if webhook_response.status_code not in WEBHOOK_ACCEPTED_STATUS_CODES:
        # Webhook should answer valid status code (by default - 200 or any of 2xx).
        # mark as failed due to not meet requirements.
        return None

    return webhook_response


def _payload_verifiy_hmac(payload: bytes, returned_hash: str | None) -> bool:
    """
    Verifies that returned hash is same as payload HMAC.
    """
    if not returned_hash:
        # Not found payload hash in the response.
        # means target webhook server is not returned hash to verify accepted state.
        return False

    if not hmac.compare_digest(
        hmac.new(payload, payload, hashlib.sha256).hexdigest(), returned_hash
    ):
        print(
            f"expected: `{hmac.new(payload, payload, hashlib.sha256).hexdigest()}`, but got: `{returned_hash}`"
        )
        # Hash is invalid, means there is some unexpected error while comparing that hashes.
        return False

    return True


def _payload_to_json_bytes(payload_data: dict) -> bytes:
    """
    Converts payload as dict to bytes from dumped JSON.
    """
    return json.dumps(
        obj=payload_data,
        allow_nan=False,
    ).encode("utf-8")


if __name__ == "__main__":
    send_http_webhook_event("florgon.com", event_type="some", data={})
