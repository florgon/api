"""
    Returns real client host from the request.
    As server mostly runs over proxy server, docker,
    and real IP may be hidden.
"""
from fastapi.requests import Request


def get_client_host_from_request(request: Request) -> str:
    """Returns client host (IP) from passed request, if it is forwarded, queries correct host."""
    if header_x_forwarded_for := request.headers.get("X-Forwarded-For"):
        return header_x_forwarded_for.split(",")[0]
    if header_cf_connecting_ip := request.headers.get("HTTP_CF_CONNECTING_IP"):
        return header_cf_connecting_ip

    return "" if request.client is None else request.client.host


def get_country_from_request(request: Request) -> str | None:
    """Returns get country from passed request, if it passed by services."""
    if header_geo_country := request.headers.get("CF-IPCountry"):
        return header_geo_country
    return None


def get_user_agent_from_request(request: Request) -> str:
    """
    Returns user agent from passed request.
    """
    return request.headers.get("User-Agent", "")
