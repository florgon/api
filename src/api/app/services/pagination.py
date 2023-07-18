"""
    Service for working with pagination.
"""


def with_pagination(
    response: dict,
    current_total: int,
    total: int,
    page: int,
    max_page: int,
    per_page: int,
) -> dict:
    """
    Adds pagination data to the response.
    """
    return {
        "current_total": current_total,
        "pagination": {
            "total": total,
            "page": page,
            "per_page": per_page,
            "max_page": max_page,
        },
    } | response
