import pytest
from cappa.testing import CommandRunner

from printed.cli.base import Printed


def create_cli_fixture(*base_args: str):
    @pytest.fixture
    def fixture() -> CommandRunner:
        return CommandRunner(
            Printed,
            base_args=list(base_args),
        )

    return fixture
