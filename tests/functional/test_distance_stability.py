"""Distance sensor stability test."""

from statistics import mean, pstdev

import pytest

from drivers.device_driver import DeviceDriver
from tests.constants import (
    DISTANCE_READING_COUNT,
    DISTANCE_STABILITY_EXPECTED_CM,
    DISTANCE_STABILITY_MEAN_TOLERANCE_CM,
    DISTANCE_STABILITY_MAX_SPREAD_CM,
    DISTANCE_STABILITY_MAX_STD_CM,
)
from tests.helpers import extract_distance

pytestmark = pytest.mark.functional


def test_distance_readings_are_stable(clean_device: DeviceDriver) -> None:
    """Verify stability of repeated readings for the fixed 20 cm object."""
    readings = [
        extract_distance(clean_device.get_distance())
        for _ in range(DISTANCE_READING_COUNT)
    ]

    actual_mean = mean(readings)
    actual_std = pstdev(readings)
    actual_min = min(readings)
    actual_max = max(readings)
    actual_spread = actual_max - actual_min

    print(
        "Distance stability: "
        f"mean={actual_mean:.2f}, std={actual_std:.2f}, "
        f"min={actual_min:.2f}, max={actual_max:.2f}"
    )

    assert (
        DISTANCE_STABILITY_EXPECTED_CM - DISTANCE_STABILITY_MEAN_TOLERANCE_CM
        <= actual_mean
        <= (
            DISTANCE_STABILITY_EXPECTED_CM
            + DISTANCE_STABILITY_MEAN_TOLERANCE_CM
        )
    ), f"Mean distance is unstable: {actual_mean:.2f} cm"
    assert (
        actual_std < DISTANCE_STABILITY_MAX_STD_CM
    ), f"Standard deviation is too high: {actual_std:.2f} cm"
    assert (
        actual_spread < DISTANCE_STABILITY_MAX_SPREAD_CM
    ), f"Distance spread is too high: {actual_spread:.2f} cm"
