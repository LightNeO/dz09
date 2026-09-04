# DZ-09 — Embedded QA Automation

## Стенд

- Плата: ESP32-S3 DevKit
- Firmware image: `../fw_3/demo_fw_3_merged.bin` (змерджена самостійно)
- Boot application: `fw_1`, version `1`
- UART: 115200 8N1
- VID: задається через змінну середовища `ESP32_VID`

## Крок 0 — Boot verification

За boot-логом:

- reset reason: `POWERON`;
- ready marker: `Device ready`;
- `App started` у фактичному boot output відсутній.


.

## Test execution

Command:

```text
pytest -v
```

Result:

```text
13 passed, 1 xfailed in 834.54s (0:13:54)
```

Pytest collected 14 test cases. The expected failure is the known firmware persistence issue in `test_config_survives_reboot`: `alarm_threshold` is not restored after reboot and returns to the firmware default value.

## Distance stability results

Test: `test_distance_readings_are_stable`

- Readings: 100
- Mean: `19.30 cm`
- Standard deviation: `0.04 cm`
- Minimum: `19.00 cm`
- Maximum: `19.40 cm`
- Spread: `0.40 cm`

Assertions:

- Mean within `20 ± 2 cm`: PASS
- Standard deviation `< 1.5 cm`: PASS
- Spread `< 5 cm`: PASS

Execution result:

```text
1 passed in 427.88s (0:07:07)
```
