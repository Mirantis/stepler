"""
-----------------------------------
Ironic baremetal multitenancy tests
-----------------------------------
"""

# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

from hamcrest import assert_that, only_contains, has_property  # noqa: H301
import pytest

pytestmark = pytest.mark.requires("ironic_nodes_count >= 1")


@pytest.mark.idempotent_id('caec6869-91c6-41ca-8386-ef84711a885f',
                           neutron_2_nets_diff_projects={'same_cidr': False})
@pytest.mark.idempotent_id('3a0bcbb9-2a53-405e-a80f-d087d8b30b5f',
                           neutron_2_nets_diff_projects={'same_cidr': True})
@pytest.mark.parametrize(
    'neutron_2_nets_diff_projects', [{
        'same_cidr': False
    }, {
        'same_cidr': True
    }],
    indirect=True,
    ids=['different_cidrs', 'same_cidr'])
def test_per_project_l3_isolation(multitenancy_resources):
    """Check user can't get access to other project's instance.

    **Setup:**

    #. Create 2 projects and 2 users
    #. Create network, subnet, router on each project
    #. Upload public baremetal ubuntu image
    #. Create baremetal flavor
    #. Create keypairs
    #. Boot 2 servers on 1'st project and 1 server on 2'nd project
    #. Assign Floating IPs to one server from 1'st project and server from 2'nd
        project

    **Steps:**

    #. Check that users can see only own project's servers
    #. Check that 1'nd user can't ping 2'st project server via fixed IP
    #. Check that 1'nd user can ping 2'st project server via floating IP
    #. Check ping between 1'st project servers

    **Teardown:**

    #. Delete servers
    #. Delete floating ips
    #. Delete networks, subnets, routers
    #. Delete image
    #. Delete flavor
    #. Delete keypairs
    #. Delete projects and users
    """
    # Check cross-projects servers visibility
    for resource in multitenancy_resources.resources:
        server_steps = resource.server_steps
        servers = server_steps.get_servers()
        assert_that(servers,
                    only_contains(*[
                        has_property('name', server.name)
                        for server in resource.servers
                    ]))  # checker: disable

    server_steps_1 = multitenancy_resources.resources[0].server_steps
    server_1_1, server_1_2 = multitenancy_resources.resources[0].servers
    server_1_2_fixed_ip = server_steps_1.get_fixed_ip(server_1_2)
    server_steps_2 = multitenancy_resources.resources[1].server_steps
    server_2 = multitenancy_resources.resources[1].servers[0]
    server_2_fixed_ip = server_steps_2.get_fixed_ip(server_2)
    server_2_floating_ip = server_steps_2.get_floating_ip(server_2)

    # Check l3 isolation
    with server_steps_1.get_server_ssh(server_1_1) as server_ssh:
        server_steps_1.check_ping_for_ip(
            server_2_fixed_ip, remote_from=server_ssh, must_be_success=False)
        server_steps_1.check_ping_for_ip(
            server_2_floating_ip, remote_from=server_ssh)
        server_steps_1.check_ping_for_ip(
            server_1_2_fixed_ip, remote_from=server_ssh)


@pytest.mark.idempotent_id('b8a62c00-99ce-476f-b34e-3c73311a93eb')
@pytest.mark.parametrize(
    'multitenancy_networks', [{
        'shared_network': True
    }],
    indirect=True,
    ids=['shared_network'])
def test_shared_network(multitenancy_resources):
    """Check different projects with shared network connectivity.

    **Setup:**

    #. Create 2 projects and 2 users
    #. Create shared network, subnet, router
    #. Upload public baremetal ubuntu image
    #. Create baremetal flavor
    #. Boot 2 servers on 1'st project and 1 server on 2'nd project
    #. Assign Floating IPs to one server from 1'st project and server from 2'nd
        project

    **Steps:**

    #. Check that 1'nd user can ping 2'st project server via fixed IP

    **Teardown:**

    #. Delete servers
    #. Delete floating ips
    #. Delete network, subnet, router
    #. Delete image
    #. Delete flavor
    #. Delete keypairs
    #. Delete projects and users
    """

    server_steps_1 = multitenancy_resources.resources[0].server_steps
    server_1_1, server_1_2 = multitenancy_resources.resources[0].servers
    server_steps_2 = multitenancy_resources.resources[1].server_steps
    server_2 = multitenancy_resources.resources[1].servers[0]
    server_2_fixed_ip = server_steps_2.get_fixed_ip(server_2)
    with server_steps_1.get_server_ssh(server_1_1) as server_ssh:
        server_steps_1.check_ping_for_ip(
            server_2_fixed_ip, remote_from=server_ssh, must_be_success=True)
