"""Functional, parameterized tests for the real distance/alarm CLI."""

import pytest

from drivers.device_driver import DeviceDriver
from tests.constants import (
    ALARM_ARMED_MARKER,
    ALARM_ENABLED_MARKER,
    ALARM_TRIGGERED_MARKER,
    DISTANCE_MODE_MARKER,
    SENSOR_READY_MARKER,
)

pytestmark = pytest.mark.functional


def _response_text(response: list[str]) -> str:
    return "\n".join(response)


@pytest.mark.parametrize(
    ("distance", "expected_marker"),
    (
        (50, ALARM_TRIGGERED_MARKER),
        (30, ALARM_TRIGGERED_MARKER),
        (20, ALARM_TRIGGERED_MARKER),
        (10, ALARM_ARMED_MARKER),
        (5, ALARM_ARMED_MARKER),
    ),
)
def test_distance_alarm_triggers_alarm_correctly(
    clean_device: DeviceDriver, distance: int, expected_marker: str
) -> None:
    """Verify distance alarm activation for a real object located at 20 cm.
    Assuming that we always have a real object at 20 cm in front of the sensor
    """
    mode_response = clean_device.sensor_mode_distance()
    mode_text = _response_text(mode_response).casefold()

    distance_response = clean_device.distance_alarm(distance)
    distance_text = _response_text(distance_response).casefold()

    arm_response = clean_device.alarm_arm()
    arm_text = _response_text(arm_response).casefold()

    sensor_response = clean_device.sensor_start()
    sensor_text = _response_text(sensor_response).casefold()

    status_response = clean_device.alarm_status()
    status_text = _response_text(status_response).casefold()

    assert (
        ALARM_ENABLED_MARKER in distance_text
    ), f"Alarm was not enabled for distance {distance}: {distance_response!r}"
    assert (
        DISTANCE_MODE_MARKER in mode_text
    ), f"Sensor mode was not set to distance: {mode_response!r}"
    assert (
        ALARM_ARMED_MARKER.casefold() in arm_text
    ), f"Alarm was not armed: {arm_response!r}"
    assert (
        SENSOR_READY_MARKER in sensor_text
    ), f"Sensor was not started: {sensor_response!r}"
    assert (
        expected_marker.casefold() in status_text
    ), f"Alarm was not triggered for a real object at 20 cm: {status_response!r}"


@pytest.mark.parametrize(
    ("zone", "expected_marker"),
    (
        ("far", ALARM_ARMED_MARKER),
        ("near", ALARM_TRIGGERED_MARKER),
        ("custom 15 25", ALARM_TRIGGERED_MARKER),
        ("custom 25 35", ALARM_ARMED_MARKER),
    ),
)
def test_distance_zone_triggers_alarm_correctly(
    clean_device: DeviceDriver, zone: str, expected_marker: str
) -> None:
    """Verify distance zone alarm activation for a real object located at 20 cm.
    Assuming that we always have a real object at 20 cm in front of the sensor
    """
    mode_response = clean_device.sensor_mode_distance()
    mode_text = _response_text(mode_response).casefold()

    distance_zone_response = clean_device.distance_zone(zone)
    distance_zone_text = _response_text(distance_zone_response).casefold()

    arm_response = clean_device.alarm_arm()
    arm_text = _response_text(arm_response).casefold()

    sensor_response = clean_device.sensor_start()
    sensor_text = _response_text(sensor_response).casefold()

    status_response = clean_device.alarm_status()
    status_text = _response_text(status_response).casefold()

    assert (
        DISTANCE_MODE_MARKER in mode_text
    ), f"Sensor mode was not set to distance: {mode_response!r}"
    assert (
        f"{zone}" in distance_zone_text
    ), f"Distance zone was not set to {zone}: {distance_zone_response!r}"
    assert (
        ALARM_ARMED_MARKER.casefold() in arm_text
    ), f"Alarm was not armed: {arm_response!r}"
    assert (
        SENSOR_READY_MARKER in sensor_text
    ), f"Sensor was not started: {sensor_response!r}"
    assert (
        expected_marker.casefold() in status_text
    ), f"Alarm was not triggered for a real object at 20 cm: {status_response!r}"
