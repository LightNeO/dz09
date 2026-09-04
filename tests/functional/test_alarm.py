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
from tests.helpers import normalized_response_to_string

pytestmark = pytest.mark.functional


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
    """Verify distance alarm activation for a real object located at 20 cm."""
    mode_response = clean_device.sensor_mode_distance()
    mode_text = normalized_response_to_string(mode_response)

    distance_response = clean_device.distance_alarm(distance)
    distance_text = normalized_response_to_string(distance_response)

    arm_response = clean_device.alarm_arm()
    arm_text = normalized_response_to_string(arm_response)

    sensor_response = clean_device.sensor_start()
    sensor_text = normalized_response_to_string(sensor_response)

    status_response = clean_device.alarm_status()
    status_text = normalized_response_to_string(status_response)

    assert ALARM_ENABLED_MARKER in distance_text, (
        f"Alarm was not enabled for distance {distance}: {distance_response!r}"
    )
    assert DISTANCE_MODE_MARKER in mode_text, (
        f"Sensor mode was not set to distance: {mode_response!r}"
    )
    assert ALARM_ARMED_MARKER.casefold() in arm_text, (
        f"Alarm was not armed: {arm_response!r}"
    )
    assert SENSOR_READY_MARKER in sensor_text, (
        f"Sensor was not started: {sensor_response!r}"
    )
    assert expected_marker.casefold() in status_text, (
        f"Alarm state was unexpected for 20 cm object: {status_response!r}"
    )


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
    """Verify distance zone alarm activation for a real object located at 20 cm."""
    mode_response = clean_device.sensor_mode_distance()
    mode_text = normalized_response_to_string(mode_response)

    distance_zone_response = clean_device.distance_zone(zone)
    distance_zone_text = normalized_response_to_string(distance_zone_response)

    arm_response = clean_device.alarm_arm()
    arm_text = normalized_response_to_string(arm_response)

    sensor_response = clean_device.sensor_start()
    sensor_text = normalized_response_to_string(sensor_response)

    status_response = clean_device.alarm_status()
    status_text = normalized_response_to_string(status_response)

    assert DISTANCE_MODE_MARKER in mode_text, (
        f"Sensor mode was not set to distance: {mode_response!r}"
    )
    assert zone.casefold() in distance_zone_text, (
        f"Distance zone was not set to {zone}: {distance_zone_response!r}"
    )
    assert ALARM_ARMED_MARKER.casefold() in arm_text, (
        f"Alarm was not armed: {arm_response!r}"
    )
    assert SENSOR_READY_MARKER in sensor_text, (
        f"Sensor was not started: {sensor_response!r}"
    )
    assert expected_marker.casefold() in status_text, (
        f"Alarm state was unexpected for zone {zone}: {status_response!r}"
    )
