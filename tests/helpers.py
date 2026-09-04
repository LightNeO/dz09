"""Shared helpers for pytest tests."""

from tests.constants import DISTANCE_VALUE_PATTERN


def response_to_string(response: list[str]) -> str:
    """Join UART response lines into a single searchable string."""
    return "\n".join(response)


def normalized_response_to_string(response: list[str]) -> str:
    """Join UART response lines and normalize case for marker assertions."""
    return response_to_string(response).casefold()


def extract_distance(response: list[str]) -> float:
    """Extract the first distance value in centimeters from a UART response."""
    match = DISTANCE_VALUE_PATTERN.search(response_to_string(response))
    if match is None:
        raise ValueError(
            f"Distance value was not found in response: {response!r}"
        )
    return float(match.group(1))
