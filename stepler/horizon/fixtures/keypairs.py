"""
---------------------
Fixtures for keypairs
---------------------
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

from stepler.horizon.steps import KeypairsSteps
from stepler.horizon.utils import generate_ids, AttrDict  # noqa

__all__ = [
    'import_keypair',
    'keypair',
    'keypairs_steps'
]


@pytest.fixture
def keypairs_steps(login, horizon):
    """Get keypairs steps."""
    return KeypairsSteps(horizon)


@pytest.yield_fixture
def keypair(keypairs_steps):
    """Create keypair."""
    name = next(generate_ids('keypair'))

    keypairs_steps.create_keypair(name)
    _keypair = AttrDict(name=name)

    yield _keypair

    keypairs_steps.delete_keypair(_keypair.name)


@pytest.yield_fixture
def import_keypair(keypairs_steps):
    """Import keypair."""
    keypairs = []

    def _import_keypair(public_key):
        name = next(generate_ids('keypair'))

        keypairs_steps.import_keypair(name, public_key)
        keypair = AttrDict(name=name)

        keypairs.append(keypair)
        return keypair

    yield _import_keypair

    if keypairs:
        keypairs_steps.delete_keypairs([k.name for k in keypairs])
