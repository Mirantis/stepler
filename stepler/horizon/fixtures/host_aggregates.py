"""
----------------------------
Fixtures for host aggregates
----------------------------
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

from stepler.horizon.steps import HostAggregatesSteps
from stepler.third_party import utils

__all__ = [
    'create_host_aggregate',
    'create_host_aggregates',
    'host_aggregate',
    'host_aggregates_steps'
]


@pytest.fixture
def host_aggregates_steps(login, horizon):
    """Fixture to get host aggregates steps."""
    return HostAggregatesSteps(horizon)


@pytest.yield_fixture
def create_host_aggregates(host_aggregates_steps, horizon):
    """Fixture to create host aggregates with options.

    Can be called several times during test.
    """
    host_aggregates = []

    def _create_host_aggregates(*host_aggregate_names):
        _host_aggregates = []

        for host_aggregate_name in host_aggregate_names:
            host_aggregates_steps.create_host_aggregate(host_aggregate_name)

            host_aggregate = utils.AttrDict(name=host_aggregate_name)
            host_aggregates.append(host_aggregate)
            _host_aggregates.append(host_aggregate)

        return _host_aggregates

    yield _create_host_aggregates

    if host_aggregates:
        host_aggregates_steps.delete_host_aggregates(
            [host_aggregate.name for host_aggregate in host_aggregates])


@pytest.yield_fixture
def create_host_aggregate(host_aggregates_steps):
    """Fixture to create host aggregate with options.

    Can be called several times during test.
    """
    host_aggregates = []

    def _create_host_aggregate(host_aggregate_name):
        host_aggregates_steps.create_host_aggregate(host_aggregate_name)
        host_aggregate = utils.AttrDict(name=host_aggregate_name)
        host_aggregates.append(host_aggregate)
        return host_aggregate

    yield _create_host_aggregate

    for host_aggregate in host_aggregates:
        host_aggregates_steps.delete_host_aggregate(host_aggregate.name)


@pytest.fixture
def host_aggregate(create_host_aggregate):
    """Fixture to create host aggregate with default options before test."""
    host_aggregate_name = next(utils.generate_ids('host-aggregate'))
    return create_host_aggregate(host_aggregate_name)
