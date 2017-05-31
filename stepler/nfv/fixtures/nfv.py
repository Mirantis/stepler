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
from stepler.third_party import utils

__all__ = [
    'nfv_steps',
    'computes_without_hp',
    'computes_with_hp_2mb',
    'computes_with_hp_1gb',
    'computes_with_hp_mixed',
    'computes_with_cpu_pinning_and_hp',
    'create_servers_to_allocate_hp',
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
    if not fqdns:
        pytest.skip("No computes without HP found")
    return fqdns


@pytest.fixture
def computes_with_hp_2mb(request, os_faults_steps):
    """Function fixture to get computes with hugepages 2Mb.

    Can be parametrized with 'host_count' and 'hp_count_per_host'.
    Example:
        @pytest.mark.parametrize('computes_with_hp_2mb',
                                [{'host_count': 2, 'hp_count_per_host': 1024}],
                                indirect=['computes_with_hp_2mb'])

    Args:
        request (obj): py.test SubRequest
        os_faults_steps (OsFaultsSteps): initialized os-faults steps

    Returns:
        list: FQDNs of computes with HP 2Mb
    """
    min_count = getattr(request, 'param', {'host_count': 1,
                                           'hp_count_per_host': 512})
    fqdns = []
    for fqdn, hp_data in os_faults_steps.get_hugepages_data(
            sizes=[config.page_2mb]):
        if hp_data[config.page_2mb]['nr'] >= min_count['hp_count_per_host']:
            fqdns.append(fqdn)
    if len(fqdns) < min_count['host_count']:
        pytest.skip("Insufficient count of compute nodes with 2Mb huge pages")
    return fqdns


@pytest.fixture
def computes_with_hp_1gb(request, os_faults_steps):
    """Function fixture to get computes with hugepages 1Gb.

    Can be parametrized with 'host_count' and 'hp_count_per_host'.
    Example:
        @pytest.mark.parametrize('computes_with_hp_1gb',
                                [{'host_count': 2, 'hp_count_per_host': 4}],
                                indirect=['computes_with_hp_1gb'])

    Args:
        request (obj): py.test SubRequest
        os_faults_steps (OsFaultsSteps): initialized os-faults steps

    Returns:
        list: FQDNs of computes with HP 1Gb
    """
    min_count = getattr(request, 'param', {'host_count': 1,
                                           'hp_count_per_host': 4})
    fqdns = []
    for fqdn, hp_data in os_faults_steps.get_hugepages_data(
            sizes=[config.page_1gb]):
        if hp_data[config.page_1gb]['nr'] >= min_count['hp_count_per_host']:
            fqdns.append(fqdn)
    if len(fqdns) < min_count['host_count']:
        pytest.skip("Insufficient count of compute nodes with 1Gb huge pages")
    return fqdns


@pytest.fixture
def computes_with_hp_mixed(request, os_faults_steps):
    """Function fixture to get computes with hugepages 2Mb and 1Gb both.

    Can be parametrized with 'host_count', 'hp_count_2mb' and 'hp_count_1gb'
    Example:
        @pytest.mark.parametrize(
            'computes_with_hp_mixed',
            [{'host_count': 2, 'hp_count_2mb': 1024, 'hp_count_1gb': 4}],
            indirect=['computes_with_hp_mixed'])

    Args:
        request (obj): py.test SubRequest
        os_faults_steps (OsFaultsSteps): initialized os-faults steps

    Returns:
        list: FQDNs of computes with HP 2Mb and 1Gb
    """
    min_count = getattr(request, 'param', {'host_count': 1,
                                           'hp_count_2mb': 512,
                                           'hp_count_1gb': 4})
    fqdns = []
    for fqdn, hp_data in os_faults_steps.get_hugepages_data(
            sizes=[config.page_2mb, config.page_1gb]):
        if ((hp_data[config.page_2mb]['nr'] >= min_count['hp_count_2mb']) and
                (hp_data[config.page_1gb]['nr'] >= min_count['hp_count_1gb'])):
            fqdns.append(fqdn)
    if len(fqdns) < min_count['host_count']:
        pytest.skip("Insufficient count of computes with 2Mb/1Gb huge pages")
    return fqdns


@pytest.fixture
def computes_with_cpu_pinning_and_hp(request, os_faults_steps):
    """Function fixture to get computes with CPU pinning and hugepages 2Mb/1Gb.

    Can be parametrized with 'host_count', 'hp_count_2mb' and 'hp_count_1gb'.
    Example:
        @pytest.mark.parametrize(
            'computes_with_cpu_pinning_and_hp',
            [{'host_count': 2, 'hp_count_2mb': 1024, 'hp_count_1gb': 4}],
            indirect=['computes_with_cpu_pinning_and_hp'])

    Args:
        request (obj): py.test SubRequest
        os_faults_steps (OsFaultsSteps): initialized os-faults steps

    Returns:
        list: FQDNs of computes with CPU pinning and HP 2Mb/1Gb
    """
    min_count = getattr(request, 'param', {'host_count': 1,
                                           'hp_count_2mb': 512,
                                           'hp_count_1gb': 4})

    nodes = os_faults_steps.get_cpu_pinning_computes()
    fqdns_pinned = [node.fqdn for node in nodes]
    if len(fqdns_pinned) < min_count['host_count']:
        pytest.skip("Insufficient count of computes with CPU pinning")

    fqdns = []
    for fqdn, hp_data in os_faults_steps.get_hugepages_data(
            fqdns=fqdns_pinned):
        if ((hp_data[config.page_2mb]['nr'] >= min_count['hp_count_2mb']) and
                (hp_data[config.page_1gb]['nr'] >= min_count['hp_count_1gb'])):
            fqdns.append(fqdn)
    if len(fqdns) < min_count['host_count']:
        pytest.skip("Insufficient count of computes with CPU pinning and HP")
    return fqdns


@pytest.fixture
def create_servers_to_allocate_hp(cirros_image,
                                  security_group,
                                  net_subnet_router,
                                  flavor_steps,
                                  create_flavor,
                                  server_steps,
                                  host_steps,
                                  os_faults_steps):
    """Callable function fixture to allocate hugepages on compute.

    This fixture creates servers with specific flavors to allocate 2Mb or 1Gb
    hugepages on all numa nodes of one compute. After that, free memory can be
    empty or not (set as parameter).

    Args:
        cirros_image (object): cirros image
        security_group (obj): nova security group
        net_subnet_router (tuple): neutron network, subnet, router
        flavor_steps (FlavorSteps): instantiated flavor steps
        create_flavor (function): function to create flavor
        server_steps (ServerSteps): instantiated server steps
        host_steps (HostSteps): instantiated host steps
        os_faults_steps (OsFaultsSteps): initialized os-faults steps

    Returns:
        function: function to create servers
    """
    def _create_servers_to_allocate_hp(fqdn, size, ram_left_free=0):
        node = os_faults_steps.get_nodes(fqdns=[fqdn])
        host_cpus = os_faults_steps.get_cpu_distribition_per_numa_node(node)
        hp_data = os_faults_steps.get_hugepage_distribition_per_numa_node(
            node, numa_count=len(host_cpus), sizes=[size])

        flv_sizes = [hp_data[numa][size]['free'] * size / 1024
                     for numa, hp in hp_data.items() if hp[size]['free'] != 0]
        flv_sizes.sort(reverse=True)

        host_name = host_steps.get_host(fqdn=fqdn).host_name

        for flv_size in flv_sizes:
            if flv_size <= ram_left_free:
                continue
            flavor_name = next(utils.generate_ids('flavor'))
            flavor = create_flavor(flavor_name, ram=flv_size - ram_left_free,
                                   vcpus=1, disk=1)
            metadata = {'hw:mem_page_size': str(size)}
            flavor_steps.set_metadata(flavor, metadata)

            server_steps.create_servers(
                image=cirros_image,
                flavor=flavor,
                networks=[net_subnet_router[0]],
                security_groups=[security_group],
                username=config.CIRROS_USERNAME,
                password=config.CIRROS_PASSWORD,
                availability_zone='nova:{}'.format(host_name))

    return _create_servers_to_allocate_hp
