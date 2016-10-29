"""
----------------
Keypair fixtures
----------------
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

from stepler.nova.steps import KeypairSteps
from stepler.third_party.utils import generate_ids

__all__ = [
    'create_keypair',
    'keypair',
    'keypair_steps'
]


@pytest.fixture
def keypair_steps(nova_client):
    """Function fixture to get keypair steps.

    Can be called several times during test.
    After the test it destroys all created security groups

    Args:
        nova_client (object): instantiated nova client

    Returns:
        stepler.nova.steps.KeypairSteps: instantiated keypair steps

    """
    return KeypairSteps(nova_client.keypairs)


@pytest.yield_fixture
def create_keypair(keypair_steps):
    """Callable function fixture to create keypair with options.

    Can be called several times during test.
    After the test it destroys all created security groups

    Args:
        keypair_steps (object): instantiated keypair steps

    Returns:
        function: function to create keypair
    """
    keypairs = []

    def _create_keypair(keypair_name):
        keypair = keypair_steps.create_keypair(keypair_name)
        keypairs.append(keypair)
        return keypair

    yield _create_keypair

    for keypair in keypairs:
        keypair_steps.delete_keypair(keypair)


@pytest.fixture
def keypair(create_keypair):
    """Function fixture to create keypair with options.

    Can be called several times during test.
    After the test it destroys all created security groups

    Args:
        create_keypair (object): instantiated keypair steps

    Returns:
        object: keypair
    """
    keypair_name = next(generate_ids('keypair'))
    return create_keypair(keypair_name)
