"""Shared pytest fixtures"""
import os

import pytest

from drivers.device_driver import DeviceDriver
from tests.constants import BOOT_READY_PATTERN, BOOT_TIMEOUT_SECONDS


@pytest.fixture(scope="session")
def device() -> DeviceDriver:
    """Connect to the unique DUT port selected by its USB VID."""
    vid_text = os.getenv("ESP32_VID")
    vid = int(vid_text, 0) if vid_text else None
    driver = DeviceDriver(DeviceDriver.find_port(vid=vid))
    driver.open()
    # The firmware requires AUTH_USER for most commands.
    login = os.getenv("DUT_LOGIN")
    password = os.getenv("DUT_PASSWORD")
    try:
        if not driver.login(login, password):
            pytest.fail("Could not log in to DUT")
        yield driver
    finally:
        try:
            if driver.ser and driver.ser.is_open:
                driver.reboot()
        except Exception:
            pass
        finally:
            driver.close()


@pytest.fixture(scope="function")
def clean_device(device: DeviceDriver) -> DeviceDriver:
    """Reset the DUT to a known state before each test."""
    device.load_config()
    device.reboot()

    if not device.wait_for_pattern(BOOT_READY_PATTERN, timeout=BOOT_TIMEOUT_SECONDS):
        pytest.fail(f"Firmware did not emit {BOOT_READY_PATTERN!r} after reboot")

    login = os.getenv("DUT_LOGIN")
    password = os.getenv("DUT_PASSWORD")

    if not device.login(login, password):
        pytest.fail("Could not log in after reboot")

    return device
