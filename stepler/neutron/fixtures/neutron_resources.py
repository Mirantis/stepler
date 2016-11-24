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
    'neutron_2_networks',
    'neutron_2_servers_different_networks',
    'neutron_2_servers_diff_nets_with_floating',
    'neutron_2_servers_same_network',
    'neutron_2_servers_iperf_different_networks',
]


@pytest.fixture
def neutron_2_networks(
        request,
        net_subnet_router,
        public_network,
        create_network,
        create_subnet,
        create_router,
        add_router_interfaces,
        router_steps):
    """Function fixture to prepare environment with 2 networks.

    This fixture creates router(s), 2 networks and 2 subnets and connects
    networks to router(s). By default, both networks will be connected to
    single router.

    All created resources are to be deleted after test.

    Can be parametrized with 'different_routers' to create 2 routers and
    connect each of networks to different router.

    Example:
        @pytest.mark.parametrize('neutron_2_networks',
                                 ['different_routers'],
                                 indirect=True)
        def test_foo(neutron_2_networks):
            # Will be created 2 routers, each of them will be linked with one
            # of the subnets.

    Args:
        request (obj): py.test SubRequest
        net_subnet_router (tuple): network, subnet, router
        public_network (dict): neutron public network
        create_network (function): function to create network
        create_subnet (function): function to create subnet
        create_router (function): function to create router
        add_router_interfaces (function): function to add subnet interface to
            router
        router_steps (obj): instantiated router steps

    Returns:
        attrdict.AttrDict: created resources
    """
    network, subnet, router = net_subnet_router
    network_2 = create_network(next(utils.generate_ids()))

    subnet_2 = create_subnet(
        subnet_name=next(utils.generate_ids()),
        network=network_2,
        cidr='192.168.2.0/24')
    routers = [router]
    if getattr(request, 'param', None) == 'different_routers':
        router_2 = create_router(next(utils.generate_ids()))
        router_steps.set_gateway(router_2, public_network)
        routers.append(router_2)
        add_router_interfaces(router_2, [subnet_2])
    else:
        add_router_interfaces(router, [subnet_2])

    return attrdict.AttrDict(
        networks=[network, network_2],
        subnets=[subnet, subnet_2],
        routers=routers)


@pytest.fixture
def neutron_2_servers_different_networks(
        request,
        cirros_image,
        flavor,
        security_group,
        server,
        neutron_2_networks,
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
        server (obj): nova server
        neutron_2_networks (obj): neutron networks, subnets, router(s)
            resources AttrDict instance
        hypervisor_steps (obj): instantiated nova hypervisor steps
        server_steps (obj): instantiated nova server steps

    Returns:
        attrdict.AttrDict: created resources
    """

    network_1, network_2 = neutron_2_networks.networks

    if getattr(request, 'param', None) == 'same_host':
        server_2_hypervisor = getattr(server, config.SERVER_HOST_ATTR)
    else:
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
        networks=(network_1, network_2),
        routers=neutron_2_networks.routers)


@pytest.fixture
def neutron_2_servers_diff_nets_with_floating(
        neutron_2_servers_different_networks,
        nova_create_floating_ip,
        server_steps):
    """Function fixture to prepare environment with 2 servers.

    This fixture creates resources using neutron_2_servers_different_networks
    fixture, creates and attaches floating ips for all servers.

    All created resources are to be deleted after test.

    Args:
        neutron_2_servers_different_networks (obj): neutron networks,
            subnets, router(s) and servers resources AttrDict instance
        nova_create_floating_ip (function): function to create floating IP
        server_steps (obj): instantiated nova server steps

    Returns:
        attrdict.AttrDict: created resources
    """
    servers = neutron_2_servers_different_networks.servers

    for server in servers:
        floating_ip = nova_create_floating_ip()
        server_steps.attach_floating_ip(server, floating_ip)

    return neutron_2_servers_different_networks


@pytest.fixture
def neutron_2_servers_same_network(
        request,
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

    Can be parametrized with 'same_host'.

    Example:
        @pytest.mark.parametrize('neutron_2_servers_same_network',
                                 ['same_host'],
                                 indirect=True)
        def test_foo(neutron_2_servers_same_network):
            # Instances will be created on the same compute

    Args:
        request (obj): py.test SubRequest
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

    if getattr(request, 'param', None) == 'same_host':
        server_2_hypervisor = getattr(server, config.SERVER_HOST_ATTR)
    else:
        server_2_hypervisor = hypervisor_steps.get_another_hypervisor(server)
        server_2_hypervisor = server_2_hypervisor.hypervisor_hostname

    network, subnet, router = net_subnet_router

    server_2 = server_steps.create_servers(
        image=cirros_image,
        flavor=flavor,
        networks=[network],
        availability_zone='nova:{}'.format(server_2_hypervisor),
        security_groups=[security_group],
        username=config.CIRROS_USERNAME,
        password=config.CIRROS_PASSWORD)[0]

    return attrdict.AttrDict(
        servers=(server, server_2),
        network=network,
        router=router)


@pytest.fixture
def neutron_2_servers_iperf_different_networks(
        ubuntu_image,
        flavor,
        keypair,
        security_group,
        neutron_2_networks,
        hypervisor_steps,
        security_group_steps,
        server_steps):
    """Function fixture to prepare environment with 2 ubuntu servers.

    This fixture creates router, 2 networks and 2 subnets, connects networks
    to router, boots nova server with ubuntu on each network on different
    computes, installs iperf to both servers, starts TCP and UDP iperf servers.

    All created resources are to be deleted after test.

    Args:
        ubuntu_image (obj): ubuntu image
        flavor (obj): nova flavor
        keypair (obj): nova server keypair
        security_group (obj): nova security group
        neutron_2_networks (obj): neutron networks, subnets, router(s)
            resources AttrDict instance
        hypervisor_steps (obj): instantiated nova hypervisor steps
        security_group_steps (obj): instantiated nova security group steps
        server_steps (obj): instantiated nova server steps

    Returns:
        attrdict.AttrDict: created resources
    """

    network_1, network_2 = neutron_2_networks.networks
    router = neutron_2_networks.routers[0]

    rules = [
        {
            # iprf tcp
            'ip_protocol': 'tcp',
            'from_port': config.IPERF_TCP_PORT,
            'to_port': config.IPERF_TCP_PORT,
            'cidr': '0.0.0.0/0',
        },
        {
            # iperf udp
            'ip_protocol': 'udp',
            'from_port': config.IPERF_UDP_PORT,
            'to_port': config.IPERF_UDP_PORT,
            'cidr': '0.0.0.0/0',
        }
    ]
    security_group_steps.add_group_rules(security_group, rules)

    hypervisors = hypervisor_steps.get_hypervisors()[:2]
    servers = []

    for hypervisor, network in zip(hypervisors, [network_1, network_2]):
        server = server_steps.create_servers(
            image=ubuntu_image,
            flavor=flavor,
            keypair=keypair,
            networks=[network],
            userdata=config.START_IPERF_USERDATA,
            availability_zone='nova:{}'.format(hypervisor.hypervisor_hostname),
            security_groups=[security_group],
            username=config.UBUNTU_USERNAME,
            check=False)[0]
        servers.append(server)

    for server in servers:

        server_steps.check_server_status(
            server,
            expected_statuses=[config.STATUS_ACTIVE],
            transit_statuses=[config.STATUS_BUILD],
            timeout=config.SERVER_ACTIVE_TIMEOUT)

        server_steps.check_server_log_contains_record(
            server,
            config.USERDATA_DONE_MARKER,
            timeout=config.USERDATA_EXECUTING_TIMEOUT)

    return attrdict.AttrDict(
        servers=servers,
        networks=(network_1, network_2),
        router=router)
