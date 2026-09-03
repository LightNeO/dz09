"""Shared pytest fixtures for DZ-09."""
import os

import pytest

from drivers.device_driver import DeviceDriver


@pytest.fixture(scope="session")
def device() -> DeviceDriver:
    """Connect to the unique DUT port selected by its USB VID."""
    vid_text = os.getenv("ESP32_VID")
    vid = int(vid_text, 0) if vid_text else None
    driver = DeviceDriver(DeviceDriver.find_port(vid=vid))
    driver.open()
    # The firmware requires AUTH_USER for most commands. Create the profile
    # once if needed and establish a session before exposing the fixture.
    login = os.getenv("DUT_LOGIN", "1")
    password = os.getenv("DUT_PASSWORD", "1")
    if not driver.login(login, password):
        driver.close()
        pytest.fail("Could not log in to DUT")
    yield driver
    driver.close()


@pytest.fixture(scope="function")
def clean_device(device: DeviceDriver) -> DeviceDriver:
    """Reset the DUT to a known state before each test."""
    device.load_config()
    device.reboot()

    if not device.wait_for_pattern("Device ready", timeout=10):
        pytest.fail("Firmware did not emit 'Device ready' after reboot")

    login = os.getenv("DUT_LOGIN", "1")
    password = os.getenv("DUT_PASSWORD", "1")

    if not device.login(login, password):
        pytest.fail("Could not log in after reboot")

    return device
