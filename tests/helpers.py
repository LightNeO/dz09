"""Shared helpers for pytest tests."""


def response_to_string(response: list[str]) -> str:
    """Join UART response lines into a single searchable string."""
    return "\n".join(response)


def normalized_response_to_string(response: list[str]) -> str:
    """Join UART response lines and normalize case for marker assertions."""
    return response_to_string(response).casefold()
