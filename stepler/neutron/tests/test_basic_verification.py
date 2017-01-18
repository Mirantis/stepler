"""
--------------------------------
Neutron basic verification tests
--------------------------------
"""

# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import pytest

from stepler.third_party import utils


@pytest.mark.idempotent_id('5a3a0b95-20c7-403a-9b2b-4d26fc10669a')
def test_networks_list(network_steps):
    """**Scenario:** Request list of networks.

    **Steps:**

    #. Get list of networks
    """
    network_steps.get_networks()


@pytest.mark.idempotent_id('e05e3a60-14ff-4a12-8d09-0762f5ceffa1')
def test_agents_list(agent_steps):
    """**Scenario:** Request list of neutron agents.

    **Steps:**

    #. Get list of neutron agents
    #. Check that all agents are up and running
    """
    agents = agent_steps.get_agents()
    agent_steps.check_alive(agents)


@pytest.mark.idempotent_id('0a600480-ec27-4742-ab13-819017fb0dae')
@pytest.mark.parametrize('change_neutron_quota', [dict(network=5)],
                         indirect=True)
def test_neutron_networks_quota(create_network, network_steps,
                                change_neutron_quota):
    """**Scenario:** Negative create of networks more than quota allows.

    **Setup:**

    #. Increase neutron quota for networks

    **Steps:**

    #. Create max possible count of networks
    #. Check that unable to create extra network

    **Teardown:**

    #. Delete networks
    #. Restore original quota
    """
    for _ in range(change_neutron_quota['network']):
        create_network(next(utils.generate_ids()))
    network_steps.check_negative_create_extra_network()


@pytest.mark.idempotent_id('7728c3ed-16f7-4fbd-ba90-cca8b2dfc718')
@pytest.mark.parametrize('change_neutron_quota', [dict(router=5)],
                         indirect=True)
def test_neutron_routers_quota(create_router, router_steps,
                               change_neutron_quota):
    """**Scenario:** Negative create of routers more than quota allows.

    **Setup:**

    #. Increase neutron quota for routers

    **Steps:**

    #. Create max possible count of routers
    #. Check that unable to create extra router

    **Teardown:**

    #. Delete routers
    #. Restore original quota
    """
    for _ in range(change_neutron_quota['router']):
        create_router(next(utils.generate_ids()))
    router_steps.check_negative_create_extra_router()


@pytest.mark.idempotent_id('0b44fd3d-434e-49d4-b0ba-92b1e6ef6196')
@pytest.mark.parametrize('change_neutron_quota', [dict(floatingip=5)],
                         indirect=True)
def test_neutron_floating_ips_quota(public_network,
                                    create_floating_ip,
                                    floating_ip_steps,
                                    change_neutron_quota):
    """**Scenario:** Negative create of floating ips more than quota allows.

    **Setup:**

    #. Increase neutron quota for floating ips
    #. Create public network

    **Steps:**

    #. Create max possible count of floating ips
    #. Check that unable to create extra floating ip

    **Teardown:**

    #. Delete floating ips
    #. Delete public network
    #. Restore original quota
    """
    for _ in range(change_neutron_quota['floatingip']):
        create_floating_ip(public_network)
    floating_ip_steps.check_negative_create_extra_floating_ip(public_network)


@pytest.mark.idempotent_id('2d02b6a6-9c04-43b6-893d-7c9c6a50de7c')
@pytest.mark.parametrize('change_neutron_quota', [dict(subnet=5)],
                         indirect=True)
def test_neutron_subnets_quota(network, create_subnet, subnet_steps,
                               change_neutron_quota):
    """**Scenario:** Negative create of routers more than quota allows.

    **Setup:**

    #. Increase neutron quota for subnets
    #. Create network

    **Steps:**

    #. Create max possible count of subnets for network
    #. Check that unable to create extra subnet

    **Teardown:**

    #. Delete subnets
    #. Delete network
    #. Restore original quota
    """
    for i in range(change_neutron_quota['subnet']):
        create_subnet(subnet_name=next(utils.generate_ids()),
                      network=network,
                      cidr='10.0.{0}.0/24'.format(i))
    subnet_steps.check_negative_create_extra_subnet(network)


@pytest.mark.idempotent_id('328e3efe-41c8-403b-ae21-0fd015f29f52')
@pytest.mark.parametrize('change_neutron_quota', [dict(port=5)],
                         indirect=True)
def test_neutron_ports_quota(network,
                             port_steps,
                             create_port,
                             change_neutron_quota):
    """**Scenario:** Negative create of ports more than quota allows.

    **Setup:**

    #. Increase neutron quota for ports
    #. Create network

    **Steps:**

    #. Create max possible count of ports for network
    #. Check that unable to create extra ports

    **Teardown:**

    #. Delete ports
    #. Delete network
    #. Restore original quota
    """
    for _ in range(change_neutron_quota['port']):
        create_port(network)
    port_steps.check_negative_create_extra_port(network)


@pytest.mark.idempotent_id('3fa69371-40eb-426c-96d1-044f9ddbdaa4')
@pytest.mark.parametrize('change_neutron_quota', [dict(security_group=5)],
                         indirect=True)
def test_neutron_security_groups_quota(current_project,
                                       neutron_security_group_steps,
                                       change_neutron_quota):
    """**Scenario:** Negative create of security groups more than quota allows.

    **Setup:**

    #. Increase neutron quota for security groups

    **Steps:**

    #. Create max possible count of security groups
    #. Check that unable to create extra security group

    **Teardown:**

    #. Delete security groups
    #. Restore original quota
    """
    sec_groups_count = len(neutron_security_group_steps.get_security_groups(
        tenant_id=current_project.id))
    count_to_create = change_neutron_quota['security_group'] - sec_groups_count
    for _ in range(count_to_create):
        neutron_security_group_steps.create()
    neutron_security_group_steps.check_negative_create_extra_security_group()


@pytest.mark.idempotent_id('1687d7ad-25da-4c18-8c90-73bdd58e1a5e')
@pytest.mark.parametrize('change_neutron_quota',
                         [dict(security_group_rule=10)],
                         indirect=True)
def test_neutron_sec_group_rules_quota(current_project,
                                       neutron_security_group_steps,
                                       neutron_security_group_rule_steps,
                                       create_security_group,
                                       change_neutron_quota):
    """**Scenario:** Negative create of security group rules more than quota.

    **Setup:**

    #. Increase neutron quota for security group rules

    **Steps:**

    #. Create security group to add rules
    #. Get count of security group rules for project to calculate
    #. Create security group rules in order to have max possible count
    #. Check that unable to create extra security group rule

    **Teardown:**

    #. Delete security group with rules
    #. Restore original quota
    """
    sec_group = create_security_group(next(utils.generate_ids()))
    params_template = {'direction': 'egress',
                       'protocol': 'icmp',
                       'port_range_min': None,
                       'port_range_max': None,
                       'security_group_id': sec_group.id}

    rules_count = len(neutron_security_group_rule_steps.get_rules(
        tenant_id=current_project.id))
    count_to_create = change_neutron_quota['security_group_rule'] - rules_count
    for i in range(count_to_create):
        params_template['remote_ip_prefix'] = '0.0.{0}.0/0'.format(i)
        neutron_security_group_rule_steps.add_rule_to_group(
            group_id=sec_group.id, **params_template)

    params_template['remote_ip_prefix'] = '0.0.{0}.0/0'.format(count_to_create)
    neutron_security_group_rule_steps.check_negative_create_extra_group_rule(
        sec_group.id, **params_template)
