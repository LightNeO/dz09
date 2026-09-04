"""Test constants"""

import re

"""Smoke test constants"""
BOOT_READY_PATTERN = "Device ready"
BOOT_TIMEOUT_SECONDS = 10
STATUS_MARKER = "[Status]"
STATUS_COMPLETION_MARKER = "Done"
DISTANCE_LOG_MARKER = "[Distance]"
DISTANCE_UNIT = "cm"
MIN_VALID_DISTANCE_CM = 0.0
LED_ON_COMMAND_ECHO = "LED ON"

"""Functional test constants"""
COMMAND_TIMEOUT_SECONDS = 5
DISTANCE_VALUE_PATTERN = re.compile(r"(\d+(?:\.\d+)?)\s*cm", re.IGNORECASE)
ALARM_ENABLED_MARKER = "alarm enabled"
DISTANCE_MODE_MARKER = "mode: distance"
SENSOR_READY_MARKER = "sensor ready"
ALARM_TRIGGERED_MARKER = "triggered"
ALARM_ARMED_MARKER = "armed"
