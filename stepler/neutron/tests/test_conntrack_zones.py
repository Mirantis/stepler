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
from stepler.third_party import utils


@pytest.mark.idempotent_id('3e21c239-c95a-49ea-b518-9b38ca7ad3ea')
def test_ssh_unavailable_after_detach_floating_ip(
        floating_ip,
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
    server_steps.attach_floating_ip(server, floating_ip)
    server_ssh = server_steps.get_server_ssh(server, ssh_timeout=10)
    with server_ssh:
        server_steps.check_active_ssh_connection(server_ssh)
        server_steps.detach_floating_ip(server, floating_ip)
        server_steps.check_active_ssh_connection(
            server_ssh,
            must_operable=False,
            timeout=config.FLOATING_IP_DETACH_TIMEOUT)
    utils.check_ssh_connection_establishment(
        server_ssh, must_work=False)


@pytest.mark.idempotent_id('036633a6-b6e0-44da-bd85-748eaf846e39')
def test_ssh_unavailable_after_deleting_tcp_rule(
        net_subnet_router,
        flavor,
        cirros_image,
        neutron_create_security_group,
        floating_ip,
        neutron_security_group_rule_steps,
        server_steps):
    """**Scenario:** Check ssh for server after deleting tcp rule.

    **Setup:**

    #. Create network, subnet and router
    #. Create flavor
    #. Create cirros image
    #. Create floating ip

    **Steps:**

    #. Create security group
    #. Add icmp and tcp rules to security group
    #. Create server with security group
    #. Assign floating ip to server
    #. Open ssh connection to server, check that it operable
    #. Delete tcp rule from security group
    #. Check that opened SSH connection is not operable
    #. Check that new SSH connection can't be established
    #. Add tcp rule to security group again
    #. Check that new SSH connection can be established

    **Teardown:**

    #. Delete server
    #. Delete security group
    #. Delete floating ip
    #. Delete image
    #. Delete flavor
    #. Delete network, subnet and router
    """
    security_group = neutron_create_security_group(next(utils.generate_ids()))
    neutron_security_group_rule_steps.add_rules_to_group(
        security_group['id'], config.SECURITY_GROUP_PING_RULES)
    ssh_rule = neutron_security_group_rule_steps.add_rules_to_group(
        security_group['id'], config.SECURITY_GROUP_SSH_RULES)[0]

    server = server_steps.create_servers(
        image=cirros_image,
        flavor=flavor,
        networks=[net_subnet_router[0]],
        security_groups=[security_group],
        username=config.CIRROS_USERNAME,
        password=config.CIRROS_PASSWORD)[0]
    server_steps.attach_floating_ip(server, floating_ip)

    server_ssh = server_steps.get_server_ssh(server, ssh_timeout=10)
    with server_ssh:
        server_steps.check_active_ssh_connection(server_ssh)
        neutron_security_group_rule_steps.delete_rule_from_group(
            ssh_rule['id'], security_group['id'])
        server_steps.check_active_ssh_connection(
            server_ssh, must_operable=False, timeout=config.SSH_CLIENT_TIMEOUT)
    utils.check_ssh_connection_establishment(
        server_ssh, must_work=False)

    neutron_security_group_rule_steps.add_rules_to_group(
        security_group['id'], config.SECURITY_GROUP_SSH_RULES)
    utils.check_ssh_connection_establishment(server_ssh)


@pytest.mark.idempotent_id('d8eb0e19-a3b0-4c14-a1b5-087a4e9c8c96')
def test_ping_unavailable_after_deleting_icmp_rule(
        net_subnet_router,
        flavor,
        cirros_image,
        floating_ip,
        neutron_create_security_group,
        neutron_security_group_rule_steps,
        server_steps):
    """**Scenario:** Check ping from server after deleting icmp rule.

    **Setup:**

    #. Create network, subnet and router
    #. Create flavor
    #. Create cirros image
    #. Create floating ip

    **Steps:**

    #. Create security group
    #. Remove all rules from security group (if it's not empty)
    #. Add icmp and tcp rules to security group
    #. Create server with security group
    #. Assign floating ip to server
    #. Open ssh connection to server
    #. Check ping to 8.8.8.8
    #. Delete icmp rule from security group
    #. Check that ping doesn't work
    #. Add icmp rule again
    #. Check ping to 8.8.8.8

    **Teardown:**

    #. Delete server
    #. Delete security group
    #. Delete floating ip
    #. Delete image
    #. Delete flavor
    #. Delete network, subnet and router
    """
    security_group = neutron_create_security_group(next(utils.generate_ids()))
    # Nova client has restricted functionality with security group rules:
    # it allows create and delete only => neutron client is used for security
    # group rules here
    rules = neutron_security_group_rule_steps.get_rules({
        'security_group_id': security_group['id']
    })
    # By default group is created with 2 egress rules:
    # Egress  IPv6  Any  Any  ::/0
    # Egress  IPv4  Any  Any  0.0.0.0/0
    # These rules allow ping from server => need to remove them
    for rule in rules:
        neutron_security_group_rule_steps.delete_rule_from_group(
            rule['id'], security_group['id'])

    # Add ssh ingress rule
    neutron_security_group_rule_steps.add_rules_to_group(
        security_group['id'], config.SECURITY_GROUP_SSH_RULES)

    # Add icmp egress rule
    icmp_rule_params = config.SECURITY_GROUP_EGRESS_PING_RULE
    icmp_rule = neutron_security_group_rule_steps.add_rule_to_group(
        security_group['id'], **icmp_rule_params)

    server = server_steps.create_servers(
        image=cirros_image,
        flavor=flavor,
        networks=[net_subnet_router[0]],
        security_groups=[security_group],
        username=config.CIRROS_USERNAME,
        password=config.CIRROS_PASSWORD)[0]
    server_steps.attach_floating_ip(server, floating_ip)

    with server_steps.get_server_ssh(server) as server_ssh:
        server_steps.check_ping_for_ip(
            config.GOOGLE_DNS_IP,
            server_ssh,
            timeout=config.NEUTRON_UPDATE_SEC_GROUP_RULES_TIMEOUT)
        neutron_security_group_rule_steps.delete_rule_from_group(
            icmp_rule['id'], security_group['id'])
        server_steps.check_ping_for_ip(
            config.GOOGLE_DNS_IP,
            server_ssh,
            must_be_success=False,
            timeout=config.NEUTRON_UPDATE_SEC_GROUP_RULES_TIMEOUT)
        neutron_security_group_rule_steps.add_rule_to_group(
            security_group['id'], **icmp_rule_params)
        server_steps.check_ping_for_ip(
            config.GOOGLE_DNS_IP,
            server_ssh,
            timeout=config.NEUTRON_UPDATE_SEC_GROUP_RULES_TIMEOUT)


@pytest.mark.idempotent_id('bf8d9694-4fbb-416f-b5b8-a073c3739b15')
def test_connectivity_with_different_projects(
        neutron_conntrack_2_projects_resources,
        os_faults_steps):
    """**Scenario:** Check connectivity between servers in different projects.

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


@pytest.mark.idempotent_id('6bf26f12-cc33-4aad-bb58-8461c8268808')
def test_connectivity_by_floating_diff_projects(
        neutron_2_servers_2_nets_diff_projects):
    """**Scenario:** Check connectivity between servers in different projects.

    This test checks connectivity between servers in different projects by
    floating ips.

    **Setup:**

    #. Create 2 projects
    #. Create net, subnet, router in each project
    #. Create security groups in each project
    #. Add ping + ssh rules for each security group
    #. Create instance in each project on the same compute
    #. Add floating ip for instance in each project

    **Steps:**

    #. Ping server in 2'nd project from server in 1'st project by floating ip
    #. Ping server in 1'st project from server in 2'nd project by floating ip

    **Teardown:**

    #. Delete floating ips
    #. Delete servers
    #. Delete security groups
    #. Delete networks, subnets, routers
    #. Delete projects
    """
    (prj_1_resources,
     prj_2_resources) = neutron_2_servers_2_nets_diff_projects.resources
    server1 = prj_1_resources.server
    server2 = prj_2_resources.server
    prj_1_server_steps = prj_1_resources.server_steps
    prj_2_server_steps = prj_2_resources.server_steps
    server1_floating_ip = prj_1_server_steps.get_floating_ip(server1)
    server2_floating_ip = prj_2_server_steps.get_floating_ip(server2)

    with prj_1_server_steps.get_server_ssh(server1) as server_ssh:
        prj_1_server_steps.check_ping_for_ip(
            server2_floating_ip, server_ssh,
            timeout=config.PING_BETWEEN_SERVERS_TIMEOUT)

    with prj_2_server_steps.get_server_ssh(server2) as server_ssh:
        prj_2_server_steps.check_ping_for_ip(
            server1_floating_ip, server_ssh,
            timeout=config.PING_BETWEEN_SERVERS_TIMEOUT)


@pytest.mark.idempotent_id('f5208ee0-6285-42e5-a6ac-537466f5b958')
def test_connectivity_by_fixed_ip_on_shared_net_between_2_projects(
        neutron_2_servers_2_projects_with_shared_net):
    """**Scenario:** Check connectivity between servers in different projects.

    This test checks connectivity between servers in different projects by
    fixed ips in case of shared network.

    **Setup:**

    #. Create admin and non-admin projects
    #. Create security groups in each project
    #. Add ping + ssh rules for each security group
    #. Create shared net with subnet and router in admin project
    #. Create instance in each project
    #. Add floating ip for instance in each project

    **Steps:**

    #. Ping server in 2'nd project from server in 1'st project by fixed ip
    #. Ping server in 1'st project from server in 2'nd project by fixed ip

    **Teardown:**

    #. Delete floating ips
    #. Delete servers
    #. Delete security groups
    #. Delete network, subnet, router
    #. Delete projects
    """
    (prj_1_resources,
     prj_2_resources) = neutron_2_servers_2_projects_with_shared_net.resources
    server1 = prj_1_resources.server
    server2 = prj_2_resources.server
    prj_1_server_steps = prj_1_resources.server_steps
    prj_2_server_steps = prj_2_resources.server_steps
    server1_fixed_ip = prj_2_server_steps.get_fixed_ip(server1)
    server2_fixed_ip = prj_2_server_steps.get_fixed_ip(server2)

    with prj_1_server_steps.get_server_ssh(server1) as server_ssh:
        prj_1_server_steps.check_ping_for_ip(
            server2_fixed_ip, server_ssh,
            timeout=config.PING_BETWEEN_SERVERS_TIMEOUT)

    with prj_2_server_steps.get_server_ssh(server2) as server_ssh:
        prj_2_server_steps.check_ping_for_ip(
            server1_fixed_ip, server_ssh,
            timeout=config.PING_BETWEEN_SERVERS_TIMEOUT)
