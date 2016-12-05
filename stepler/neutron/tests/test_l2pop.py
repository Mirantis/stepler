"""
---------------------------
Neutron L2 population tests
---------------------------
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

pytestmark = [
    pytest.mark.requires("l2pop", "l3_agent_nodes_count >= 3")
]


@pytest.mark.requires("computes_count >= 3")
@pytest.mark.idempotent_id('11436a6d-2554-4f0d-9624-a9f8a9a64b30')
def test_tunnels_establishing(
        cirros_image,
        flavor,
        network,
        server,
        server_steps,
        agent_steps,
        hypervisor_steps,
        os_faults_steps):
    """**Scenario:** Check tunnels establishing between nodes.

    **Setup:**

    #. Create cirros image
    #. Create flavor
    #. Create security group
    #. Create network with subnet and router
    #. Create server_1

    **Steps:**

    #. Check that compute_1 has tunnels to controllers
    #. Check that compute_1 has no tunnels to other computes
    #. Check that other computes have no tunnels to compute_1
    #. Boot server on compute_2
    #. Check that compute_2 has tunnels to controllers and compute_1
    #. Check that compute_1 has tunnel to compute_2
    #. Check that other computes have no tunnels to compute_1, compute_2 and
        controllers
    #. Boot server on compute_3
    #. Check that compute_3 has tunnels to controllers, compute_1 and compute_2
    #. Check that compute_1 has tunnel to compute_3
    #. Check that compute_2 has tunnel to compute_3

    **Teardown:**

    #. Delete servers
    #. Delete network, subnet, router
    #. Delete security group
    #. Delete flavor
    #. Delete cirros image
    """
    server_1 = server
    compute_1_fqdn = getattr(server_1, config.SERVER_ATTR_HOST)
    compute_1 = os_faults_steps.get_nodes(fqdns=[compute_1_fqdn])
    computes = os_faults_steps.get_nodes(service_names=[config.NOVA_COMPUTE])

    dhcp_agents = agent_steps.get_dhcp_agents_for_net(network)

    controllers = os_faults_steps.get_nodes_for_agents(dhcp_agents)
    os_faults_steps.check_ovs_tunnels(compute_1, controllers)
    os_faults_steps.check_ovs_tunnels(
        compute_1, computes - compute_1, must_established=False)
    os_faults_steps.check_ovs_tunnels(
        computes - compute_1, computes | controllers, must_established=False)

    compute_2_fqdn = hypervisor_steps.get_another_hypervisor(
        [server_1]).hypervisor_hostname
    compute_2 = os_faults_steps.get_nodes(fqdns=[compute_2_fqdn])

    server_2 = server_steps.create_servers(
        image=cirros_image,
        flavor=flavor,
        networks=[network],
        availability_zone='nova:{}'.format(compute_2_fqdn))[0]

    os_faults_steps.check_ovs_tunnels(compute_1, compute_2)
    os_faults_steps.check_ovs_tunnels(compute_2, compute_1)

    os_faults_steps.check_ovs_tunnels(
        computes - compute_1 - compute_2,
        computes | controllers,
        must_established=False)

    compute_3_fqdn = hypervisor_steps.get_another_hypervisor(
        [server_1, server_2]).hypervisor_hostname

    compute_3 = os_faults_steps.get_nodes(fqdns=[compute_3_fqdn])

    server_steps.create_servers(
        image=cirros_image,
        flavor=flavor,
        networks=[network],
        availability_zone='nova:{}'.format(compute_3_fqdn))[0]

    os_faults_steps.check_ovs_tunnels(compute_3, compute_1 | compute_2)
    os_faults_steps.check_ovs_tunnels(compute_1 | compute_2, compute_3)
