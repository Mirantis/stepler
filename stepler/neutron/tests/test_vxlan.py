"""
-------------------
Neutron VxLAN tests
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

from stepler import config

pytestmark = [
    pytest.mark.requires("vxlan", "l3_agent_nodes_count >= 3")
]


@pytest.mark.idempotent_id('af35d15d-b021-4f88-8055-963051b890e7')
def test_vni_matching_network_segmentation_id(
        network,
        router,
        server,
        server_steps,
        port_steps,
        agent_steps,
        os_faults_steps):
    """**Scenario:** Check that VNI matching the segmentation_id of a network.

    **Setup:**

    #. Create cirros image
    #. Create flavor
    #. Create security group
    #. Create network with subnet and router
    #. Create server

    **Steps:**

    #. Get L3 agent with ACTIVE ha_state for router
    #. Check that vxlan is enabled on node with L3 agent
    #. Check that vxlan is enabled on server's compute
    #. Start tcpdump on compute
    #. Ping server's fixed ip from L3 agent node with qrouter namespace
    #. Stop tcpdump
    #. Check that VXLAN packets has same VNI that network segmentation_id

    **Teardown:**

    #. Delete server
    #. Delete network, subnet, router
    #. Delete security group
    #. Delete flavor
    #. Delete cirros image
    """
    agent = agent_steps.get_l3_agents_for_router(router)[0]
    agent_node = os_faults_steps.get_nodes_for_agents([agent])
    os_faults_steps.check_vxlan_enabled(agent_node)

    compute_host_name = getattr(server, config.SERVER_ATTR_HOST)
    compute_node = os_faults_steps.get_nodes(fqdns=[compute_host_name])
    os_faults_steps.check_vxlan_enabled(compute_node)

    tcpdump_files = os_faults_steps.start_tcpdump(
        compute_node, args="-vvni any port 4789")

    fixed_ip = server_steps.get_fixed_ip(server)
    os_faults_steps.ping_ip_with_router_namescape(agent_node, fixed_ip, router)

    os_faults_steps.stop_tcpdump(compute_node, tcpdump_files)
    pcap_files = os_faults_steps.download_tcpdump_results(compute_node,
                                                          tcpdump_files)

    os_faults_steps.check_vni_segmentation(pcap_files, network)
