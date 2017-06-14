"""
----------------------------
Ironic multitenancy fixtures
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

import functools

import attrdict
import pytest

from stepler import config
from stepler.third_party import utils

__all__ = [
    'multitenancy_networks',
    'multitenancy_resources',
]


@pytest.fixture
def multitenancy_networks(request, network_steps,
                          neutron_nets_for_projects):
    """Function fixture to prepare multitenancy networks.

    Can be parametrized with dict {'shared_network': True}.
    If `shared_network` is True - fixture returns shared network, otherwise it
    returns 2 networks for each of projects.

    Args:
        request (obj): py.test SubRequest
        network_steps (obj): instantiated network steps
        neutron_nets_for_projects (obj): networks for different projects
            fixture

    Returns:
        attrdict.AttrDict: created resources
    """
    params = dict(shared_network=False)
    params.update(getattr(request, 'param', {}))

    if not params['shared_network']:
        return neutron_nets_for_projects
    else:
        net, subnet, router = request.getfixturevalue('net_subnet_router')
        network_steps.update(net, shared=True)
        return attrdict.AttrDict(resources=[{
            'net_router': (net, router)
        }, {
            'net_router': (net, router)
        }])


@pytest.fixture
def multitenancy_resources(request, projects, multitenancy_networks,
                           get_neutron_security_group_steps,
                           get_neutron_security_group_rule_steps,
                           get_server_steps, get_keypair_steps, glance_steps,
                           baremetal_flavor, baremetal_ubuntu_image,
                           port_steps, create_floating_ip, public_network):
    """Function fixture to prepare environment for ironic multitenancy tests.

    This fixture:
            * creates projects;
            * creates net, subnet, router in each project;
            * creates security groups in each project;
            * add ping + ssh rules for 1'st project's security group;
            * add ssh rules for 2'nd project security group;
            * creates 2 servers in 1'st project;
            * creates 2 servers in 2'nd project with same fixed ip as for 1'st
                project;
            * add floating ips for one of servers in each project.

        All created resources are to be deleted after test.

    Args:
        request (obj): py.test SubRequest
        projects (obj): projects fixture
        multitenancy_networks (obj): multitenancy tests networks fixture
        get_neutron_security_group_steps (function): function to get neutron
            security group steps
        get_neutron_security_group_rule_steps (function): function to get
            neutron security group rule steps
        get_server_steps (function): function to get server steps
        get_keypair_steps (function): function to get keypair steps
        glance_steps (obj): instantiated glance steps
        baremetal_flavor (obj): baremetal flavor
        baremetal_ubuntu_image (oobj): baremetal ubuntu image
        port_steps (obj): instantiated port steps
        create_floating_ip (function): function to create floating ip
        public_network (dict): neutron public network

    Returns:
        attrdict.AttrDict: created resources
    """
    base_name, = utils.generate_ids()

    resources = []
    fixed_ip_1, fixed_ip_2 = config.LOCAL_IPS[20:22]

    glance_steps.update_images(
        [baremetal_ubuntu_image], visibility=config.IMAGE_VISIBILITY_PUBLIC)

    for i, project_resources in enumerate(projects.resources):
        name = "{}_{}".format(base_name, i)
        servers = []
        credentials = project_resources.credentials
        network, router = multitenancy_networks.resources[i].net_router

        security_group_steps = get_neutron_security_group_steps(**credentials)
        security_group_rule_steps = get_neutron_security_group_rule_steps(
            **credentials)
        security_group_name = "{}_{}".format(base_name, i)
        security_group = security_group_steps.create(security_group_name)
        request.addfinalizer(
            functools.partial(security_group_steps.delete, security_group))
        security_group_rule_steps.add_rules_to_group(
            security_group['id'], config.SECURITY_GROUP_SSH_PING_RULES)

        server_steps = get_server_steps(**credentials)
        project_resources.server_steps = server_steps

        keypair_steps = get_keypair_steps(**credentials)
        keypair = keypair_steps.create_keypairs()[0]
        request.addfinalizer(
            functools.partial(keypair_steps.delete_keypairs, [keypair]))

        server1 = server_steps.create_servers(
            server_names=[name + "_1"],
            image=baremetal_ubuntu_image,
            flavor=baremetal_flavor,
            networks=[network],
            security_groups=[security_group],
            keypair=keypair,
            username=config.UBUNTU_USERNAME)[0]
        request.addfinalizer(
            functools.partial(server_steps.delete_servers, [server1]))
        servers.append(server1)

        server1_port = port_steps.get_port(
            device_owner=config.PORT_DEVICE_OWNER_SERVER, device_id=server1.id)
        floating_ip = create_floating_ip(
            public_network,
            port=server1_port,
            project_id=project_resources.project_id)
        server_steps.check_server_ip(
            server1,
            floating_ip['floating_ip_address'],
            timeout=config.FLOATING_IP_BIND_TIMEOUT)

        if i == 0:
            server2 = server_steps.create_servers(
                server_names=[name + "_2"],
                image=baremetal_ubuntu_image,
                flavor=baremetal_flavor,
                networks=[network],
                security_groups=[security_group],
                keypair=keypair,
                username=config.UBUNTU_USERNAME)[0]
            request.addfinalizer(
                functools.partial(server_steps.delete_servers, [server2]))
            servers.append(server2)
        project_resources.servers = servers
        resources.append(project_resources)
    return attrdict.AttrDict(resources=resources)
