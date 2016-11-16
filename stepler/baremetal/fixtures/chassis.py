"""
-----------------------
Ironic chassis fixtures
-----------------------
"""

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import pytest

from stepler.baremetal import steps
from stepler import config

__all__ = [
    'ironic_chassis_steps',
    'get_ironic_chassis_steps',
    'cleanup_chassis',
    'primary_chassis',
    'unexpected_chassis_cleanup',
]


@pytest.fixture(scope='session')
def get_ironic_chassis_steps(get_ironic_client):
    """Callable session fixture to get ironic steps.

    Args:
        get_ironic_client (function): function to get ironic client

    Returns:
        function: function to instantiated ironic steps
    """
    def _get_ironic_chassis_steps(**credentials):
        return steps.IronicChassisSteps(
            get_ironic_client(**credentials).chassis)

    return _get_ironic_chassis_steps


@pytest.fixture
def unexpected_chassis_cleanup(primary_chassis,
                               get_ironic_chassis_steps,
                               cleanup_chassis):
    """Function fixture to clear unexpected volumes.

    It provides cleanup before and after test.
    """
    if config.CLEANUP_UNEXPECTED_BEFORE_TEST:
        cleanup_chassis(get_ironic_chassis_steps())

    yield

    if config.CLEANUP_UNEXPECTED_AFTER_TEST:
        cleanup_chassis(get_ironic_chassis_steps())


@pytest.fixture
def ironic_chassis_steps(unexpected_chassis_cleanup,
                         get_ironic_chassis_steps,
                         cleanup_chassis):
    """Callable function fixture to get ironic steps.

    Can be called several times during a test.
    After the test it destroys all created chassis.

    Args:
        get_ironic_chassis_steps (function): function to get ironic steps
        cleanup_chassis (function): function to cleanup chassis after test

    Yields:
        IronicChassisSteps: instantiated ironic chassis steps
    """
    _chassis_steps = get_ironic_chassis_steps()

    chassis_before = _chassis_steps.get_ironic_chassis(check=False)
    chassis_uuids_before = {chassis.uuid for chassis in chassis_before}

    yield _chassis_steps
    cleanup_chassis(_chassis_steps,
                    uncleanable_chassis_uuids=chassis_uuids_before)


@pytest.fixture(scope='session')
def cleanup_chassis(uncleanable):
    """Callable session fixture to cleanup chassis.

    Args:
        uncleanable (AttrDict): Data structure with skipped resources
    """
    def _cleanup_chassis(_chassis_steps,
                         limit=0,
                         uncleanable_chassis_uuids=None):
        uncleanable_chassis_uuids = (uncleanable_chassis_uuids or
                                     uncleanable.chassis_ids)
        deleting_chassis = []

        for chassis in _chassis_steps.get_ironic_chassis(check=False):
            if chassis.uuid not in uncleanable_chassis_uuids:
                deleting_chassis.append(chassis)

        if len(deleting_chassis) > limit:
            _chassis_steps.delete_ironic_chassis(deleting_chassis)

    return _cleanup_chassis


@pytest.fixture(scope='session')
def primary_chassis(get_ironic_chassis_steps,
                    cleanup_chassis,
                    uncleanable):
    """Session fixture to remember primary chassis before tests.

    Also optionally in finalization it deletes all unexpected chassis which
    are remained after tests.

    Args:
        get_ironic_chassis_steps (function): Function to get ironic steps.
        cleanup_chassis (function): Function to cleanup volumes.
        uncleanable (AttrDict): Data structure with skipped resources.
    """
    chassis_before = set()
    for chassis in get_ironic_chassis_steps().get_ironic_chassis(check=False):
        chassis_before.add(chassis)
        uncleanable.chassis_ids.add(chassis.uuid)

    yield
    if config.CLEANUP_UNEXPECTED_AFTER_ALL:
        cleanup_chassis(get_ironic_chassis_steps(),
                        uncleanable_chassis_uuids=chassis_before)
