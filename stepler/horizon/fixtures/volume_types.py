"""
------------------------------------------------------
Fixtures to manipulate with volume types and QoS Specs
------------------------------------------------------
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

from stepler.horizon.steps import VolumeTypesSteps
from stepler.third_party import utils

__all__ = [
    'qos_spec',
    'volume_type',
    'volume_types_steps'
]


@pytest.fixture
def volume_types_steps(horizon, login):
    """Get volume types steps.

    Arguments:
        - login: log in before tests.
        - horizon: application for steps.
    """
    return VolumeTypesSteps(horizon)


@pytest.yield_fixture
def volume_type(volume_types_steps):
    """Create volume type.

    Arguments:
        - volume_types_steps: in order to create volume type.
    """
    name = next(utils.generate_ids('volume-type'))

    volume_types_steps.create_volume_type(name)
    _volume_type = utils.AttrDict(name=name)

    yield _volume_type

    volume_types_steps.delete_volume_type(_volume_type.name)


@pytest.yield_fixture
def qos_spec(volume_types_steps):
    """Create QoS Spec.

    Arguments:
        - volume_types_steps: in order to create QoS Spec.
    """
    name = next(utils.generate_ids('qos-spec'))

    volume_types_steps.create_qos_spec(name)
    _qos_spec = utils.AttrDict(name=name)

    yield _qos_spec

    volume_types_steps.delete_qos_spec(_qos_spec.name)
