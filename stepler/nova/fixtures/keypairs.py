"""
Keypair fixtures.

@author: schipiga@mirantis.com
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
from stepler.utils import generate_ids

__all__ = [
    'create_keypair',
    'keypair',
    'keypair_steps'
]


@pytest.fixture
def keypair_steps(nova_client):
    """Fixture to get keypair steps."""
    return KeypairSteps(nova_client.keypairs)


@pytest.yield_fixture
def create_keypair(keypair_steps):
    """Fixture to create keypair with options.

    Can be called several times during test.
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
    """Fixture to create keypair with default options before test."""
    keypair_name = next(generate_ids('keypair'))
    return create_keypair(keypair_name)
