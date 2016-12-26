"""
----------------------
Fixtures for instances
----------------------
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

from stepler import config
from stepler.horizon.steps import InstancesSteps
from stepler.third_party import utils

__all__ = [
    'create_instance',
    'instance',
    'instances_steps'
]


@pytest.yield_fixture
def create_instance(instances_steps):
    """Create instances."""
    instances = []

    def _create_instance(instance_name,
                         network_name=config.INTERNAL_NETWORK_NAME,
                         count=1):
        _instances = []
        instance_names = instances_steps.create_instance(
            instance_name, network_name=network_name, count=count)

        for name in instance_names:
            instance = utils.AttrDict(name=name)
            instances.append(instance)
            _instances.append(instance)

        return _instances

    yield _create_instance

    if instances:
        instances_steps.delete_instances([i.name for i in instances])


@pytest.fixture
def instances_steps(setup_network, login, horizon):
    """Get instances steps."""
    return InstancesSteps(horizon)


@pytest.yield_fixture
def instance(instances_steps):
    """Create instance."""
    instance_name = next(utils.generate_ids('instance'))

    instances_steps.create_instance(
        instance_name, network_name=config.INTERNAL_NETWORK_NAME)
    instance = utils.AttrDict(name=instance_name)

    yield instance

    instances_steps.delete_instance(instance.name)
