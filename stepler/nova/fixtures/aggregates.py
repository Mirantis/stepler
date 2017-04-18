"""
------------------
Aggregate fixtures
------------------
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

from stepler.nova import steps

__all__ = [
    'aggregate_steps',
    'create_aggregate',
    'pinned_aggregate',
]


@pytest.fixture
def aggregate_steps(nova_client):
    """Callable function fixture to get nova aggregate steps.

    Args:
        nova_client (function): function to get nova client

    Returns:
        function: function to instantiated aggregate steps
    """
    return steps.AggregateSteps(nova_client.aggregates)


@pytest.yield_fixture
def create_aggregate(aggregate_steps):
    """Callable function fixture to create nova aggregate with options.

    Can be called several times during a test.
    After the test it destroys all created nodes.

    Args:
        flavor_steps (object): instantiated flavor steps

    Returns:
        function: function to create flavors as batch with options
    """
    aggregates = []

    def _create_aggregate(aggregate_name=None, availability_zone='nova'):
        aggregate = aggregate_steps.create_aggregate(
            aggregate_name, availability_zone)
        aggregates.append(aggregate)
        return aggregate

    yield _create_aggregate

    for aggregate in aggregates:
        aggregate.get()
        for host_name in aggregate.hosts:
            aggregate_steps.remove_host(aggregate, host_name)
        aggregate_steps.delete_aggregate(aggregate)


@pytest.fixture
def pinned_aggregate(create_aggregate, aggregate_steps, host_steps,
                     os_faults_steps):
    """Function fixture to create an aggregate with pinned=True and hosts

    Args:
        create_aggregate (function): function to create nova aggregate
        aggregate_steps (object): instantiated aggregate steps
        host_steps (object): instantiated host steps
        os_faults_steps (object): instantiated os_faults steps

    Returns:
        object: nova aggregate
    """
    aggregate = create_aggregate()

    metadata = {'pinned': 'true'}
    aggregate_steps.set_metadata(aggregate, metadata)

    computes = os_faults_steps.get_cpu_pinning_computes()
    for compute in computes:
        host = host_steps.get_host(fqdn=compute.fqdn)
        aggregate_steps.add_host(aggregate, host.host_name)

    return aggregate
