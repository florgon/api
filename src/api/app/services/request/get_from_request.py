"""
    Returns real client host from the request.
    As server mostly runs over proxy server, docker,
    and real IP may be hidden.
"""
from fastapi.requests import Request


def get_client_host_from_request(request: Request) -> str:
    """Returns client host (IP) from passed request, if it is forwarded, queries correct host."""
    header_x_forwarded_for = request.headers.get("X-Forwarded-For")
    if header_x_forwarded_for:
        return header_x_forwarded_for.split(",")[0]
    return request.client.host


def get_country_from_request(request: Request) -> str | None:
    """Returns get country from passed request, if it passed by services."""
    header_geo_country = request.headers.get("CF-IPCountry")
    if header_geo_country:
        return header_geo_country
    return None
