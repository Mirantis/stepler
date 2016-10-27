import pytest

from stepler.cli_clients import steps

__all__ = [
    'cli_openstack_steps',
]


@pytest.fixture
def cli_openstack_steps():
    return steps.CliOpenstackSteps()
