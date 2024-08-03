from datetime import datetime

import pytest
from time_machine import TimeMachineFixture

from printed.console import Console


@pytest.fixture(autouse=True)
def time(time_machine: TimeMachineFixture):
    time_machine.move_to(datetime(2020, 1, 1), tick=False)
    yield


@pytest.fixture
def console():
    return Console()
