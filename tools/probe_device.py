"""Probe version, distance and status after creating/logging in a test user."""
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from drivers.device_driver import DeviceDriver

vid_text = os.getenv("ESP32_VID")
vid = int(vid_text, 0) if vid_text else None
driver = DeviceDriver(DeviceDriver.find_port(vid))
driver.open()
try:
    login = os.getenv("DUT_LOGIN", "qa_dz09")
    password = os.getenv("DUT_PASSWORD", "pass123")
    print("register/login:", driver.login(login, password))
    for command in ("version", "distance", "status"):
        print(f"\n>>> {command}")
        print("\n".join(driver.send_command(command, timeout=3)))
finally:
    driver.close()
