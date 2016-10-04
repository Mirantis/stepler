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

from stepler.third_party import utils

__all__ = [
    'ovs_restart_resources',
]


@pytest.fixture
def ovs_restart_resources(
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
    """Function fixture to prepare environment for OVS restart tests.

    This fixture creates router, 2 networks with 2 subnets, connects networks
    to router, boot 1 nova server on each network on different computes.

    All created resources deletes after test.

    Args:
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

    server_hypervisor = getattr(server, 'OS-EXT-SRV-ATTR:hypervisor_hostname')

    server_2_hypervisor = next(
        hypervisor.hypervisor_hostname
        for hypervisor in hypervisor_steps.get_hypervisors()
        if hypervisor.hypervisor_hostname != server_hypervisor)

    server_2 = server_steps.create_servers(
        image=cirros_image,
        flavor=flavor,
        networks=[network_2],
        availability_zone='nova:{}'.format(server_2_hypervisor),
        security_groups=[security_group])[0]

    return attrdict.AttrDict(
        servers=(server, server_2),
        networks=(network, network_2),
        router=router)
