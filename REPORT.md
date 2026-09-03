# DZ-09 — Embedded QA Automation

## Стенд

- Плата: ESP32-S3 DevKit
- Firmware image: `../fw_3/demo_fw_3_merged.bin`
- Boot application: `fw_1`, version `1`
- UART: 115200 8N1
- VID: задається через змінну середовища `ESP32_VID`

## Крок 0 — Boot verification

За boot-логом:

- reset reason: `POWERON`;
- ready marker: `Device ready`;
- `App started` у фактичному boot output відсутній.

Заміна маркера на `Device ready` використовується за погодженням із викладачем.

## Firmware adaptation

Надана прошивка повертає текстові diagnostic logs, а не JSON-структури з початкового формулювання. Тому smoke-тести перевіряють фактичний контракт CLI:

- `status` повертає status log і marker `Done`;
- `distance` повертає числове значення у сантиметрах;
- `led on` приймається пристроєм і повертається в response.

Команда `version` у фактичній прошивці не підтримується, тому замість неї використовується smoke-перевірка `led on`.

## Test execution

```text
pytest -v
```

Smoke tests:

```text
3 tests collected
```

Фактичний результат повного запуску буде додано після стабільного прогону на вільному COM-порті.
