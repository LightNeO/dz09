"""Basic smoke checks for the connected ESP32-S3 DUT."""

import re

import pytest

from drivers.device_driver import DeviceDriver
from tests.constants import (
    DISTANCE_LOG_MARKER,
    DISTANCE_UNIT,
    LED_ON_COMMAND,
    MIN_VALID_DISTANCE_CM,
    STATUS_COMPLETION_MARKER,
    STATUS_MARKER,
)

pytestmark = pytest.mark.smoke


def test_status_command_works(clean_device: DeviceDriver) -> None:
    response = clean_device.get_status()
    response_text = "\n".join(response)
    normalized_response = response_text.casefold()

    assert response, "The status command returned no response"
    assert (
        STATUS_MARKER.casefold() in normalized_response
    ), "Status marker was not found"
    assert (
        STATUS_COMPLETION_MARKER.casefold() in normalized_response
    ), "Status did not complete"


def test_distance_command_returns_measurement(
    clean_device: DeviceDriver,
) -> None:
    response = clean_device.get_distance()
    response_text = "\n".join(response)
    normalized_response = response_text.casefold()
    match = re.search(
        rf"{re.escape(DISTANCE_LOG_MARKER.casefold())}.*?(\d+(?:\.\d+)?)\s*{DISTANCE_UNIT}",
        normalized_response,
    )

    assert (
        match is not None
    ), f"Numeric distance was not found: {response_text!r}"
    assert float(match.group(1)) >= MIN_VALID_DISTANCE_CM


def test_led_command_works(clean_device: DeviceDriver) -> None:
    response = clean_device.led_on()
    response_text = "\n".join(response)
    normalized_response = response_text.casefold()

    assert (
        LED_ON_COMMAND.casefold() in normalized_response
    ), f"The device did not echo the LED command: {response_text!r}"
