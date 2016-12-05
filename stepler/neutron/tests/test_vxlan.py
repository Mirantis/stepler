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
from stepler.third_party import tcpdump

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

    os_faults_steps.check_vni_segmentation(pcap_files[compute_host_name],
                                           network,
                                           add_filters=[tcpdump.filter_icmp])


@pytest.mark.requires("computes_count >= 2")
@pytest.mark.idempotent_id('39dfeb67-a179-4bb9-8019-5f184a4a302d')
def test_vni_matching_network_segmentation_id_for_different_computes(
        neutron_2_servers_diff_nets_with_floating,
        server_steps,
        port_steps,
        agent_steps,
        os_faults_steps):
    """**Scenario:** Check that VNI matching the segmentation_id of a networks.

    **Setup:**

    #. Create cirros image
    #. Create flavor
    #. Create security group
    #. Create network_1 with subnet_1 and router_1
    #. Create network_2 with subnet_2 and router_2
    #. Create server_1
    #. Create server_2 on another compute and connect it to network_2
    #. Create and attach floating IP for each server

    **Steps:**

    #. Start tcpdump on computes
    #. Ping each server's fixed ip from other servers
    #. Stop tcpdump
    #. Check that VXLAN packets has same VNI value that corresponding server
        network's segmentation_id

    **Teardown:**

    #. Delete servers
    #. Delete floating IPs
    #. Delete networks, subnets, router
    #. Delete security group
    #. Delete flavor
    #. Delete cirros image
    """
    servers = neutron_2_servers_diff_nets_with_floating.servers
    computes_fqdns = []
    fixed_ips = []
    for server in servers:
        computes_fqdns.append(getattr(server, config.SERVER_ATTR_HOST))
        fixed_ips.append(server_steps.get_fixed_ip(server))

    computes = os_faults_steps.get_nodes(fqdns=computes_fqdns)

    tcpdump_files = os_faults_steps.start_tcpdump(
        computes, args="-vvni any port 4789")

    ping_plan = {
        servers[0]: [(servers[1], config.FIXED_IP)],
        servers[1]: [(servers[0], config.FIXED_IP)],
    }

    server_steps.check_ping_by_plan(
        ping_plan, timeout=config.PING_BETWEEN_SERVERS_TIMEOUT)

    os_faults_steps.stop_tcpdump(computes, tcpdump_files)
    pcap_files = os_faults_steps.download_tcpdump_results(computes,
                                                          tcpdump_files)

    networks = neutron_2_servers_diff_nets_with_floating.networks

    compute_1_pcap = pcap_files[computes_fqdns[0]]
    compute_2_pcap = pcap_files[computes_fqdns[1]]
    os_faults_steps.check_vni_segmentation(
        compute_1_pcap, networks[0], add_filters=[tcpdump.filter_icmp])
    os_faults_steps.check_vni_segmentation(
        compute_2_pcap, networks[1], add_filters=[tcpdump.filter_icmp])
