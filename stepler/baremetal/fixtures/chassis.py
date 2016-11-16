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
    cleanup_chassis(get_ironic_chassis_steps())


@pytest.fixture
def ironic_chassis_steps(unexpected_chassis_cleanup,
                         get_ironic_chassis_steps,
                         cleanup_chassis):
    """Callable function fixture to create ironic chassis with options.

    Can be called several times during a test.
    After the test it destroys all created chassis.

    Args:
        get_ironic_chassis_steps (object): instantiated ironic steps

    Returns:
        function: function to create chassis as batch with options
    """
    _chassis_steps = get_ironic_chassis_steps()

    chassis_before = _chassis_steps.get_ironic_chassis(check=False)
    # chassis_before = {chs.uuid for chs in chassis}

    yield _chassis_steps
    cleanup_chassis(get_ironic_chassis_steps,
                    uncleanable_chassis=chassis_before)


@pytest.fixture(scope='session')
def cleanup_chassis():
    def _cleanup_chassis(get_ironic_chassis_steps, limit=0, uncleanable_chassis=None):
        uncleanable_chassis = uncleanable_chassis or []

        # deleting_chassis = []

        chassis = get_ironic_chassis_steps().get_ironic_chassis(check=False)
        deleting_chassis = list(set(chassis) - set(uncleanable_chassis))
        # for chs in chassis:
        #     if chs not in uncleanable_chassis:
        #         deleting_chassis.append(chs)

            # if chs not in uncleanable_chassis:
            #     deleting_chassis.append(chs)

        if len(deleting_chassis) > limit:
            # deleting_chassis = list(set(deleting_chassis))
            for chs in deleting_chassis:
                get_ironic_chassis_steps().delete_ironic_chassis(chs)

    return _cleanup_chassis


@pytest.fixture(scope='session')
def primary_chassis(get_ironic_chassis_steps,
                    cleanup_chassis):
    """Session fixture to remember primary volumes before tests.

    Also optionally in finalization it deletes all unexpected volumes which
    are remained after tests.

    Args:
        get_volume_steps (function): Function to get volume steps.
        cleanup_volumes (function): Function to cleanup volumes.
    """
    chassis_before = set()
    for chs in get_ironic_chassis_steps().get_ironic_chassis(check=False):
        chassis_before.add(chs)

    yield
    cleanup_chassis(get_ironic_chassis_steps, uncleanable_chassis=chassis_before)