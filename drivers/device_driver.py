"""UART driver for the ESP32-S3 demo firmware used in DZ-09."""

from __future__ import annotations

import json
import re
import time
from typing import Any

import serial
from serial.tools import list_ports

ANSI_ESCAPE_RE = re.compile(r"\x1b\[[0-9;]*[mK]")


class DeviceDriver:
    """Encapsulates UART transport and firmware command protocol."""

    def __init__(
        self, port: str, timeout: float = 2.0, baudrate: int = 115200
    ):
        self.port_name = port
        self.timeout = timeout
        self.baudrate = baudrate
        self.ser: serial.Serial | None = None

    @staticmethod
    def find_port(vid: int | None = None) -> str:
        """Return the unique DUT port, optionally filtered by USB VID."""
        ports = list(list_ports.comports())
        candidates = [p for p in ports if vid is None or p.vid == vid]
        if len(candidates) != 1:
            raise RuntimeError(
                f"Expected exactly one ESP32-S3 port for VID={vid!r}; found: {candidates}"
            )
        return candidates[0].device

    def open(self) -> None:
        """Open UART with the required 115200 8N1 settings."""
        if self.ser and self.ser.is_open:
            return
        self.ser = serial.Serial(
            port=self.port_name,
            baudrate=self.baudrate,
            bytesize=serial.EIGHTBITS,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            timeout=self.timeout,
        )
        self.ser.reset_input_buffer()

    def close(self) -> None:
        """Close the port safely."""
        if self.ser and self.ser.is_open:
            self.ser.close()

    def _require_open(self) -> serial.Serial:
        if not self.ser or not self.ser.is_open:
            raise RuntimeError("Serial port is not open")
        return self.ser

    @staticmethod
    def clean_line(raw: bytes) -> str:
        """Decode one UART line, remove ANSI control codes and line endings."""
        text = raw.decode("utf-8", errors="replace")
        text = ANSI_ESCAPE_RE.sub("", text)
        return text.rstrip("\r\n")

    def read_lines(
        self, timeout: float | None = None, end_pattern: str | None = None
    ) -> list[str]:
        """Read non-empty lines until timeout or an optional marker."""
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
                if end_pattern and end_pattern in line:
                    break
        return result

    def send_command(
        self, command: str, timeout: float | None = None
    ) -> list[str]:
        """Send a command and collect response lines until timeout or marker."""
        ser = self._require_open()
        ser.reset_input_buffer()
        # Normalize every command to exactly one CRLF.
        # ``help``, ``help\n`` and ``help\r\n`` become ``help\r\n``.
        ser.write((command.rstrip("\r\n") + "\r\n").encode())
        ser.flush()
        return self.read_lines(timeout)

    def wait_for_pattern(self, pattern: str, timeout: float = 10.0) -> bool:
        """Wait until a text pattern appears or timeout expires."""
        lines = self.read_lines(
            timeout=timeout,
            end_pattern=pattern,
        )
        return any(pattern in line for line in lines)

    def get_version(self) -> str:
        lines = self.send_command("version")
        return next(
            line.strip()
            for line in lines
            if re.fullmatch(r"v\d+\.\d+\.\d+", line.strip())
        )

    def get_status(self) -> dict[str, Any]:
        """Return status, not JSON, tolerating a CLI/prompt-wrapped response."""
        return self.send_command("status", timeout=3)

    def get_distance(self) -> dict[str, Any]:
        """Return distance, not JSON, tolerating a CLI/prompt-wrapped response."""
        return self.send_command("distance", timeout=3)

    def set_alarm_threshold(self, value: int) -> None:
        self.send_command(f"config set alarm_threshold {value}")

    def get_alarm_threshold(self) -> int:
        lines = self.send_command("config get alarm_threshold")
        for line in reversed(lines):
            match = re.search(r"(?:alarm_threshold\s*[:=]?\s*)(\d+)", line)
            if match:
                return int(match.group(1))
        raise ValueError(f"Alarm threshold not found: {lines!r}")

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
        """Create the profile if necessary, then start an AUTH_USER session."""
        registration = self.send_command(f"register {login} {password}", timeout=5)
        registration_text = "\n".join(registration)
        registration_ok = (
            "Profile Created" in registration_text
            or "Profile already exists" in registration_text
        )

        if not registration_ok:
            return False
        response = self.send_command(f"login {login} {password}", timeout=5)
        return "Session Started" in "\n".join(response)
