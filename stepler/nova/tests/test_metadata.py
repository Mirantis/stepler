"""
---------------------
Server metadata tests
---------------------
"""

#    Copyright 2016 Mirantis, Inc.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

import pytest

from stepler.third_party import utils

TEST_METADATA_INFO = {'key': str(next(utils.generate_ids('test_meta')))}

SET_META_CMD_TEMPLATE = (
    '. /root/openrc ; nova host-meta {host} set {key}={value}'.format(
        host='{host}',
        key=TEST_METADATA_INFO.keys()[0],
        value=TEST_METADATA_INFO.values()[0]))
DEL_META_CMD_TEMPLATE = (
    '. /root/openrc ; nova host-meta {host} del {key}'.format(
        host='{host}',
        key=TEST_METADATA_INFO.keys()[0]))


@pytest.mark.idempotent_id('fb831027-2663-4b76-b81f-868a85ca08fe')
def test_metadata_reach_all_booted_vm(
        security_group,
        nova_floating_ip,
        ubuntu_image,
        keypair,
        create_server_context,
        flavor_steps,
        network_steps,
        server_steps):
    """**Scenario:** Verify that image can be connected with SSH.

    **Setup:**

    #. Create security group
    #. Create floating IP
    #. Get or create ubuntu image
    #. Create keypair

    **Steps:**

    #. Get flavor ``m1.small``
    #. Get admin internal network
    #. Create nova server
    #. Attach floating IP to nova server
    #. Check that server is available via SSH
    #. Detach floating IP
    #. Delete nova server

    **Teardown:**

    #. Delete keypair
    #. Release floating IP
    #. Delete security group
    """
    flavor = flavor_steps.get_flavor(name='m1.small')
    network = network_steps.get_network_by_name('admin_internal_net')

    server_name = next(utils.generate_ids('server'))
    with create_server_context(server_name,
                               image=ubuntu_image,
                               flavor=flavor,
                               networks=[network],
                               keypair=keypair,
                               security_groups=[security_group],
                               username='ubuntu') as server:

        server_steps.attach_floating_ip(server, nova_floating_ip)
        server_steps.get_server_ssh(server)
        server_steps.detach_floating_ip(server, nova_floating_ip)


# TODO(akoryagin) need to add check that we have 2 or more computes
@pytest.mark.idempotent_id('2af40022-a2ca-4615-aff3-2c07354ce983')
def test_put_metadata_on_instances_on_single_compute(
        security_group, ubuntu_image, keypair, network, subnet,
        nova_zone_hosts, create_servers, flavor_steps, server_steps,
        os_faults_client, os_faults_steps, exec_cmd_with_rollback):
    """**Scenario:** Put metadata on all instances scheduled on a single
    compute node.

    **Setup:**

    #. Create security group
    #. Get or create ubuntu image
    #. Create keypair
    #. Create network and subnetwork

    **Steps:**

    #. Get flavor ``m1.small``
    #. Get FQDNs of nova hosts
    #. Create 2 nova servers on host 1
    #. Create 2 nova servers on host 2
    #. From controller node add new 'key=value' to metadata of servers,
        located on host 1.
    #. Check that servers from host 1 have 'key=value' in their metadata
    #. Check that servers from host 2 do NOT have 'key=value' in their metadata
    #. From controller node delete 'key=value' from metadata of servers,
        located on host 1.
    #. Check that servers from host 1 and host 2 do NOT have 'key=value' in
        their metadata

    **Teardown:**

    #. Delete servers
    #. Delete keypair
    #. Delete security group
    #. Delete network and subnetwork
    """

    flavor = flavor_steps.get_flavor(name='m1.small')
    host1 = nova_zone_hosts[0]
    host2 = nova_zone_hosts[1]
    controller_node = (os_faults_client.get_service('nova-api')
                       .get_nodes().pick())

    cmd_set_meta = SET_META_CMD_TEMPLATE.format(host=host1)
    cmd_del_meta = DEL_META_CMD_TEMPLATE.format(host=host1)

    host1_servers = create_servers(
        server_names=list(utils.generate_ids('server_host1', count=2)),
        image=ubuntu_image,
        flavor=flavor,
        networks=[network],
        keypair=keypair,
        security_groups=[security_group],
        availability_zone='nova:{}'.format(host1))

    host2_servers = create_servers(
        server_names=list(utils.generate_ids('server_host2', count=2)),
        image=ubuntu_image,
        flavor=flavor,
        networks=[network],
        keypair=keypair,
        security_groups=[security_group],
        availability_zone='nova:{}'.format(host2))

    with exec_cmd_with_rollback(
            nodes=controller_node,
            cmd=cmd_set_meta,
            rollback_cmd=cmd_del_meta):

        server_steps.check_metadata_presence(
            host1_servers, TEST_METADATA_INFO)

        server_steps.check_metadata_presence(
            host2_servers, TEST_METADATA_INFO, present=False)

    server_steps.check_metadata_presence(
        host1_servers + host2_servers, TEST_METADATA_INFO, present=False)
