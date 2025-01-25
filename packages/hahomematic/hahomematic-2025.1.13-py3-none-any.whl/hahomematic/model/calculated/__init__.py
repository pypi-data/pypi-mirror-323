"""Module for HaHomematic calculated data points."""

from __future__ import annotations

import logging
from typing import Final

from hahomematic.decorators import inspector
from hahomematic.model import device as hmd
from hahomematic.model.calculated.data_point import CalculatedDataPoint
from hahomematic.model.calculated.sensor import OperatingVoltageLevel

__all__ = [
    "CalculatedDataPoint",
    "OperatingVoltageLevel",
    "create_calculated_data_points",
]

_LOGGER: Final = logging.getLogger(__name__)


@inspector()
def create_calculated_data_points(channel: hmd.Channel) -> None:
    """Decides which data point category should be used, and creates the required data points."""
    if OperatingVoltageLevel.is_relevant_for_model(channel=channel):
        channel.add_data_point(data_point=OperatingVoltageLevel(channel=channel))
