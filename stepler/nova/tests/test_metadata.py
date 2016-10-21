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

from hamcrest import assert_that, has_entries, is_not  # noqa
import pytest

from stepler.third_party import utils


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
        os_faults_client, os_faults_steps):

    metadata_info = {'key': 'stepler_test'}
    flavor = flavor_steps.get_flavor(name='m1.small')
    host1 = nova_zone_hosts[0]
    host2 = nova_zone_hosts[1]
    controller_node = (os_faults_client.get_service('nova-api')
                       .get_nodes().pick())

    cmd = (
        '. /root/openrc ; nova host-meta {0} set {1}={2}'.format(
            host1, metadata_info.keys()[0], metadata_info.values()[0]))
    rollback_cmd = (
        '. /root/openrc ; nova host-meta {0} delete key'.format(
            host1, metadata_info.keys()[0]))

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

    with os_faults_steps.execute_cmd_with_rollback(
            nodes=controller_node,
            cmd=cmd,
            rollback_cmd=rollback_cmd):

        server_steps.check_servers_metadata_contains(
            host1_servers, metadata_info)

        server_steps.check_servers_metadata_contains(
            host2_servers, metadata_info, contains=False)

    server_steps.check_servers_metadata_contains(
        host1_servers + host2_servers, metadata_info, contains=False)
