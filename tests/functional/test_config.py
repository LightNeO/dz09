"""Functional config tests for the real distance/alarm CLI."""

import os

import pytest

from drivers.device_driver import DeviceDriver
from tests.constants import (
    BOOT_READY_PATTERN,
    BOOT_TIMEOUT_SECONDS,
    EXPECTED_ALARM_THRESHOLD,
    EXPECTED_ALARM_THRESHOLD_RESPONSE,
)
from tests.helpers import normalized_response_to_string

pytestmark = pytest.mark.functional


@pytest.mark.xfail(
    reason="Known issue: the alarm threshold is not preserved after reboot, it resets to 80"
)
def test_config_survives_reboot(clean_device: DeviceDriver) -> None:
    """Verify that the alarm threshold survives a reboot."""
    clean_device.set_alarm_threshold(EXPECTED_ALARM_THRESHOLD)
    clean_device.save_config()
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
