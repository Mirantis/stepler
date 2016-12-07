"""
-----------------------------
Neutron conntrack zones tests
-----------------------------
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

import time

import pytest

from stepler import config


@pytest.mark.idempotent_id('3e21c239-c95a-49ea-b518-9b38ca7ad3ea')
def test_ssh_unavailable_after_detach_floating_ip(
        nova_floating_ip,
        server,
        server_steps):
    """**Scenario:** Check ssh by floating ip for server after deleting ip.

    **Setup:**

    #. Create floating ip
    #. Create server

    **Steps:**

    #. Assign floating ip to server
    #. Open ssh connection to server, check that it operable
    #. Detach floating IP address from server
    #. Check that opened SSH connection is not operable
    #. Check that new SSH connection can't be established

    **Teardown:**

    #. Delete server
    #. Delete floating ip
    """
    server_steps.attach_floating_ip(server, nova_floating_ip)
    server_ssh = server_steps.get_server_ssh(server)
    with server_ssh:
        server_steps.check_active_ssh_connection(server_ssh)
        server_steps.detach_floating_ip(server, nova_floating_ip)
        server_steps.check_active_ssh_connection(
            server_ssh,
            must_operable=False,
            timeout=config.FLOATING_IP_DETACH_TIMEOUT)
    server_steps.check_ssh_connection_establishment(
        server_ssh, must_work=False)


@pytest.mark.idempotent_id('bf8d9694-4fbb-416f-b5b8-a073c3739b15')
def test_connectivity_with_different_tenants(
        neutron_conntrack_2_projects_resources,
        os_faults_steps):
    """**Scenario:** Check connectivity between servers in different tenants.

    **Setup:**

    #. Create 2 projects
    #. Create net, subnet, router in each project
    #. Create secutiry groups in each project
    #. Add ping + ssh rules for 1'st project security group
    #. Add ssh rules for 2'nd project security group
    #. Create 2 servers in 1'st project
    #. Create 2 servers in 2'nd project with same fixed ip as for 1'st project
    #. Add floating ips for one of servers in each project

    **Steps:**

    #. Start ping with fixed ICMP id from server with floating ip to another
        server in 1'st project
    #. Start ping with fixed ICMP id from server with floating ip to another
        server in 2'nd project
    #. Check that iptables contains rules that assign zones for tap and qvb
        devices
    #. wait few seconds
    #. Stop pings
    #. Check that pings in 1'st project is success
    #. Check that pings in 2'nd project is not success

    **Teardown:**

    #. Delete floating ips
    #. Delete servers
    #. Delete security groups
    #. Delete networks, subnets, routers
    #. Delete projects
    """
    icmp_id = 12358
    (project_1_resources,
     project_2_resources) = neutron_conntrack_2_projects_resources.resources
    proj_1_server_steps = project_1_resources.server_steps
    proj_2_server_steps = project_2_resources.server_steps
    proj_1_server_2_ip = proj_1_server_steps.get_fixed_ip(
        project_1_resources.servers[1])
    proj_2_server_2_ip = proj_2_server_steps.get_fixed_ip(
        project_2_resources.servers[1])
    compute = os_faults_steps.get_nodes(
        fqdns=[neutron_conntrack_2_projects_resources.hostname])
    with proj_1_server_steps.check_fixed_id_ping_loss_context(
            proj_1_server_2_ip,
            icmp_id=icmp_id,
            server=project_1_resources.servers[0]):

        with proj_1_server_steps.check_no_fixed_id_ping_context(
                proj_2_server_2_ip,
                icmp_id=icmp_id,
                server=project_2_resources.servers[0]):
            time.sleep(2)
            os_faults_steps.check_zones_assigment_to_devices(compute)
