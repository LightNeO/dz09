"""Functional config tests for the real distance/alarm CLI."""

import os

import pytest

from drivers.device_driver import DeviceDriver
from tests.constants import (
    BOOT_READY_PATTERN,
    BOOT_TIMEOUT_SECONDS,
    EXPECTED_ALARM_THRESHOLD,
    EXPECTED_ALARM_THRESHOLD_RESPONSE,
    EXPECTED_SAVE_CONFIG_RESPONSE,
)
from tests.helpers import normalized_response_to_string

pytestmark = pytest.mark.functional


@pytest.mark.xfail(
    reason=(
        "Known firmware issue: alarm_threshold is not restored "
        "after reboot and returns to the default value."
    ),
    strict=False,
)
def test_config_survives_reboot(clean_device: DeviceDriver) -> None:
    """Verify that the alarm threshold survives a reboot."""
    alarm_threshold_response = clean_device.set_alarm_threshold(
        EXPECTED_ALARM_THRESHOLD
    )
    alarm_threshold_text = normalized_response_to_string(
        alarm_threshold_response
    )

    assert EXPECTED_ALARM_THRESHOLD_RESPONSE in alarm_threshold_text, (
        "Alarm threshold was not set correctly: "
        f"expected {EXPECTED_ALARM_THRESHOLD}, response={alarm_threshold_response!r}"
    )

    save_config_response = clean_device.save_config()
    save_config_text = normalized_response_to_string(save_config_response)
    assert EXPECTED_SAVE_CONFIG_RESPONSE in save_config_text, (
        "Config was not saved correctly: "
        f"expected {EXPECTED_SAVE_CONFIG_RESPONSE}, response={save_config_response!r}"
    )

    clean_device.reboot()

    assert clean_device.wait_for_pattern(
        BOOT_READY_PATTERN,
        timeout=BOOT_TIMEOUT_SECONDS,
    ), "Firmware did not become ready after reboot"

    login = os.getenv("DUT_LOGIN")
    password = os.getenv("DUT_PASSWORD")
    assert clean_device.login(login, password), "Could not log in after reboot"

    response = clean_device.get_alarm_threshold_response()
    response_text = normalized_response_to_string(response)

    assert EXPECTED_ALARM_THRESHOLD_RESPONSE in response_text, (
        "Alarm threshold was not preserved after reboot: "
        f"expected {EXPECTED_ALARM_THRESHOLD}, response={response!r}"
    )
