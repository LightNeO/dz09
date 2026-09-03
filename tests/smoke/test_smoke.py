"""Basic smoke check for the connected ESP32-S3 DUT."""
from drivers.device_driver import DeviceDriver


def test_device_accepts_help_command(clean_device: DeviceDriver) -> None:
    """Verify that the device responds to a basic CLI command."""
    response = clean_device.send_command("help", timeout=3)
    response_text = "\n".join(response)

    assert response, "The device returned no response to the help command"
    assert "Unknown" not in response_text, (
        f"The device rejected the help command: {response_text!r}"
    )