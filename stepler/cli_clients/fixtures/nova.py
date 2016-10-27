import pytest

from stepler.cli_clients import steps

__all__ = [
    'cli_nova_steps',
]


@pytest.fixture
def cli_nova_steps():
    return steps.CliNovaSteps()
