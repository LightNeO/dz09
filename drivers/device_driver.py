"""UART driver for the ESP32-S3 device under test"""

from __future__ import annotations

import re
import time

import serial
from serial.tools import list_ports
from drivers.protocol_constants import (
    AUTH_TIMEOUT_SECONDS,
    COMMAND_TIMEOUT_SECONDS,
    PROFILE_CREATED_MARKER,
    PROFILE_EXISTS_MARKER,
    SESSION_STARTED_MARKER,
    UART_BAUDRATE,
    UART_TIMEOUT_SECONDS,
)

ANSI_ESCAPE_RE = re.compile(r"\x1b\[[0-9;]*[mK]")


class DeviceDriver:
    """Encapsulates UART transport and firmware command protocol."""

    def __init__(
        self,
        port: str,
        timeout: float = UART_TIMEOUT_SECONDS,
        baudrate: int = UART_BAUDRATE,
    ):
        self.port_name = port
        self.timeout = timeout
        self.baudrate = baudrate
        self.ser: serial.Serial | None = None

    @staticmethod
    def find_port(vid: int | None = None) -> str:
        ports = list(list_ports.comports())
        candidates = [p for p in ports if vid is None or p.vid == vid]
        if len(candidates) != 1:
            raise RuntimeError(
                f"Expected exactly one ESP32-S3 port for VID={vid!r}; found: {candidates}"
            )
        return candidates[0].device

    def open(self) -> None:
        if self.ser and self.ser.is_open:
            return
        self.ser = serial.Serial(
            self.port_name,
            self.baudrate,
            bytesize=8,
            parity=serial.PARITY_NONE,
            stopbits=1,
            timeout=self.timeout,
        )
        self.ser.reset_input_buffer()

    def close(self) -> None:
        if self.ser and self.ser.is_open:
            self.ser.close()

    def _require_open(self) -> serial.Serial:
        if not self.ser or not self.ser.is_open:
            raise RuntimeError("Serial port is not open")
        return self.ser

    @staticmethod
    def clean_line(raw: bytes) -> str:
        text = raw.decode("utf-8", errors="replace")
        return ANSI_ESCAPE_RE.sub("", text).rstrip("\r\n")

    def read_lines(
        self, timeout: float | None = None, end_pattern: str | None = None
    ) -> list[str]:
        ser = self._require_open()
        deadline = time.monotonic() + (
            self.timeout if timeout is None else timeout
        )
        result: list[str] = []
        while time.monotonic() < deadline:
            raw = ser.readline()
            if not raw:
                continue
            line = self.clean_line(raw)
            if line:
                result.append(line)
                if end_pattern and end_pattern.casefold() in line.casefold():
                    break
        return result

    def send_command(
        self,
        command: str,
        timeout: float | None = None,
        end_pattern: str | None = None,
    ) -> list[str]:
        ser = self._require_open()
        ser.reset_input_buffer()
        ser.write((command.rstrip("\r\n") + "\r\n").encode())
        ser.flush()
        return self.read_lines(timeout, end_pattern=end_pattern)

    def wait_for_pattern(self, pattern: str, timeout: float = 10.0) -> bool:
        return bool(self.read_lines(timeout=timeout, end_pattern=pattern))

    def get_status(self) -> list[str]:
        return self.send_command("status", timeout=COMMAND_TIMEOUT_SECONDS)

    def get_distance(self) -> list[str]:
        return self.send_command("distance", timeout=COMMAND_TIMEOUT_SECONDS)

    def led_on(self) -> list[str]:
        return self.send_command("led on", timeout=COMMAND_TIMEOUT_SECONDS)

    def led_off(self) -> list[str]:
        return self.send_command("led off", timeout=COMMAND_TIMEOUT_SECONDS)

    def save_config(self) -> None:
        self.send_command("config save")

    def load_config(self) -> None:
        self.send_command("config load")

    def reboot(self) -> None:
        ser = self._require_open()
        ser.reset_input_buffer()
        ser.write(b"reboot\r\n")
        ser.flush()

    def login(self, login: str, password: str) -> bool:
        registration = self.send_command(
            f"register {login} {password}", timeout=AUTH_TIMEOUT_SECONDS
        )
        registration_text = "\n".join(registration).casefold()
        if not (
            PROFILE_CREATED_MARKER.casefold() in registration_text
            or PROFILE_EXISTS_MARKER.casefold() in registration_text
        ):
            return False
        response = self.send_command(
            f"login {login} {password}", timeout=AUTH_TIMEOUT_SECONDS
        )
        return (
            SESSION_STARTED_MARKER.casefold() in "\n".join(response).casefold()
        )
