"""
------------
NFV fixtures
------------
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
from stepler.nfv import steps


__all__ = [
    'nfv_steps',
    'computes_without_hp',
    'computes_with_hp_2mb',
]


@pytest.fixture
def nfv_steps():
    """Function fixture to get NFV steps.

    Returns:
        stepler.nfv.steps.NvfSteps: instantiated NFV steps
    """
    return steps.NfvSteps()


@pytest.fixture
def computes_without_hp(os_faults_steps):
    """Function fixture to get computes without hugepages.

    Args:
        os_faults_steps (OsFaultsSteps): initialized os-faults steps

    Returns:
        list: FQDNs of computes without HP
    """
    fqdns = []
    for fqdn, hp_data in os_faults_steps.get_hugepages_data():
        if sum(hp_data) == 0:
            fqdns.append(fqdn)
    return fqdns


@pytest.fixture
def computes_with_hp_2mb(request, os_faults_steps):
    """Function fixture to get computes without hugepages.

    Can be parametrized with 'host_count' and 'hp_count_per_host'.
    Example:
        @pytest.mark.parametrize('computes_with_hp_2mb',
                                [{'host_count': 2, 'hp_count_per_host': 1024}],
                                indirect=['computes_with_hp_2mb'])

    Args:
        request (obj): py.test SubRequest
        os_faults_steps (OsFaultsSteps): initialized os-faults steps

    Returns:
        list: FQDNs of computes with HP 2MB
    """
    min_count = getattr(request, 'param', {'host_count': 1,
                                           'hp_count_per_host': 1024})
    fqdns = []
    for fqdn, hp_data in os_faults_steps.get_hugepages_data(
            sizes=[config.page_2mb]):
        if hp_data[config.page_2mb]['nr'] >= min_count['hp_count_per_host']:
            fqdns.append(fqdn)
    if len(fqdns) < min_count['host_count']:
        pytest.skip("Insufficient count of compute nodes with 2Mb huge pages")
    return fqdns
