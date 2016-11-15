"""
-------------------
Hypervisor fixtures
-------------------
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
    'hypervisor_steps',
    'big_hypervisors',
]


@pytest.fixture
def hypervisor_steps(nova_client):
    """Fixture to get hypervisor steps.

    Args:
        nova_client (object): instantiated nova client

    Returns:
        stepler.nova.steps.HypervisorSteps: instantiated hypervisor steps
    """
    return steps.HypervisorSteps(nova_client.hypervisors)


@pytest.fixture
def big_hypervisors(hypervisor_steps, flavor):
    """Function fixture to get hypervisors sorted by their capacity.

    Args:
        hypervisor_steps (obj): instantiated hypervisor steps
        flavor (obj): Nova flavor

    Returns:
        list: sorder hypervisors (from biggest to smallest)
    """
    hypervisors = hypervisor_steps.get_hypervisors()
    suitable_hypervisors = []
    for hypervisor in hypervisors:
        cap = hypervisor_steps.get_hypervisor_capacity(hypervisor, flavor)
        suitable_hypervisors.append((cap, hypervisor))
    hypervisors = [hyp for cap, hyp in reversed(sorted(suitable_hypervisors))]
    return hypervisors
