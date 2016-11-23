"""
----------------------------------
Neutron OVS restart tests fixtures
----------------------------------
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

import attrdict
import pytest

from stepler import config
from stepler.third_party import utils

__all__ = [
    'neutron_2_servers_different_networks',
    'neutron_2_servers_same_network',
]


@pytest.fixture(params=['different_hosts'])
def neutron_2_servers_different_networks(
        request,
        cirros_image,
        flavor,
        security_group,
        net_subnet_router,
        server,
        create_network,
        create_subnet,
        add_router_interfaces,
        hypervisor_steps,
        server_steps):
    """Function fixture to prepare environment with 2 servers.

    This fixture creates router, 2 networks and 2 subnets, connects networks
    to router, boot nova server on each network on different computes.

    All created resources are to be deleted after test.

    Can be parametrized with 'same_host'.

    Example:
        @pytest.mark.parametrize('neutron_2_servers_different_networks',
                                 ['same_host'],
                                 indirect=True)
        def test_foo(neutron_2_servers_different_networks):
            # Instances will be created on the same compute

    Args:
        request (obj): py.test SubRequest
        cirros_image (obj): cirros image
        flavor (obj): nova flavor
        security_group (obj): nova security group
        net_subnet_router (tuple): network, subnet, router
        server (obj): nova server
        create_network (function): function to create network
        create_subnet (function): function to create subnet
        add_router_interfaces (function): function to add subnet interface to
            router
        hypervisor_steps (obj): instantiated nova hypervisor steps
        server_steps (obj): instantiated nova server steps

    Returns:
        attrdict.AttrDict: created resources
    """

    network, subnet, router = net_subnet_router
    network_2 = create_network(next(utils.generate_ids()))

    subnet_2 = create_subnet(
        subnet_name=next(utils.generate_ids()),
        network=network_2,
        cidr='192.168.2.0/24')
    add_router_interfaces(router, [subnet_2])

    if request.param == 'same_host':
        server_2_hypervisor = getattr(server, 'OS-EXT-SRV-ATTR:host')
    elif request.param == 'different_hosts':
        server_2_hypervisor = hypervisor_steps.get_another_hypervisor(server)
        server_2_hypervisor = server_2_hypervisor.hypervisor_hostname

    server_2 = server_steps.create_servers(
        image=cirros_image,
        flavor=flavor,
        networks=[network_2],
        availability_zone='nova:{}'.format(server_2_hypervisor),
        security_groups=[security_group],
        username=config.CIRROS_USERNAME,
        password=config.CIRROS_PASSWORD)[0]

    return attrdict.AttrDict(
        servers=(server, server_2),
        networks=(network, network_2),
        router=router)


@pytest.fixture
def neutron_2_servers_same_network(
        cirros_image,
        flavor,
        security_group,
        net_subnet_router,
        server,
        hypervisor_steps,
        server_steps):
    """Function fixture to prepare environment with 2 servers.

    This fixture creates router, network and subnet, connects network
    to router, boot 2 nova server on different computes.

    All created resources are to be deleted after test.

    Args:
        cirros_image (obj): cirros image
        flavor (obj): nova flavor
        security_group (obj): nova security group
        net_subnet_router (tuple): network, subnet, router
        server (obj): nova server
        hypervisor_steps (obj): instantiated nova hypervisor steps
        server_steps (obj): instantiated nova server steps

    Returns:
        attrdict.AttrDict: created resources
    """

    network, subnet, router = net_subnet_router

    server_2_hypervisor = hypervisor_steps.get_another_hypervisor(server)

    server_2 = server_steps.create_servers(
        image=cirros_image,
        flavor=flavor,
        networks=[network],
        availability_zone='nova:{}'.format(
            server_2_hypervisor.hypervisor_hostname),
        security_groups=[security_group],
        username=config.CIRROS_USERNAME,
        password=config.CIRROS_PASSWORD)[0]

    return attrdict.AttrDict(
        servers=(server, server_2),
        network=network,
        router=router)
