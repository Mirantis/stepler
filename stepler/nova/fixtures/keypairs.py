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

from stepler import config
from stepler.nova import steps
from stepler.third_party import context

__all__ = [
    'keypair',
    'keypair_steps',
    'keypairs_cleanup',
]


@pytest.fixture
def keypair_steps(nova_client, keypairs_cleanup):
    """Function fixture to get keypair steps.

    Can be called several times during test.
    After the test it destroys all created security groups

    Args:
        nova_client (object): instantiated nova client
        keypairs_cleanup (function): function to cleanup keypairs

    Returns:
        KeypairSteps: instantiated keypair steps
    """
    _keypair_steps = steps.KeypairSteps(nova_client.keypairs)
    with keypairs_cleanup(_keypair_steps):
        yield _keypair_steps


@pytest.fixture
def keypairs_cleanup(uncleanable):
    """Callable function fixture to cleanup keypairs after test.

    Args:
        uncleanable (AttrDict): data structure with skipped resources

    Returns:
        function: function to cleanup keypairs
    """
    @context.context
    def _keypairs_cleanup(keypair_steps):

        def _get_keypairs():
            # check=False because in best case no keypairs will be
            return keypair_steps.get_keypairs(
                name_prefix=config.STEPLER_PREFIX, check=False)

        keypair_ids_before = [keypair.id for keypair in _get_keypairs()]

        yield

        deleting_keypairs = []
        for keypair in _get_keypairs():

            if keypair.id not in uncleanable.keypair_ids:
                if keypair.id not in keypair_ids_before:
                    deleting_keypairs.append(keypair)

        keypair_steps.delete_keypairs(deleting_keypairs)

    return _keypairs_cleanup


@pytest.fixture
def keypair(keypair_steps):
    """Function fixture to create keypair with default options.

    Args:
        keypair_steps (object): instantiated keypair steps

    Returns:
        object: keypair
    """
    return keypair_steps.create_keypairs()[0]
