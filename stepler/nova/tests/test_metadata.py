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

from stepler.third_party.utils import generate_ids


def test_metadata_reach_all_booted_vm(security_group, nova_floating_ip,
                                      ubuntu_image, keypair, flavor_steps,
                                      network_steps, server_steps):
    """Verify that image can be connected with SSH."""
    flavor = flavor_steps.get_flavor(name='m1.small')
    network = network_steps.get_network_by_name('admin_internal_net')

    for server_name in generate_ids('server', count=1):
        server = server_steps.create_server(server_name,
                                            image=ubuntu_image,
                                            flavor=flavor,
                                            networks=[network],
                                            keypair=keypair,
                                            security_groups=[security_group])

        server_steps.attach_floating_ip(server, nova_floating_ip)
        server_steps.check_ssh_connect(server, keypair, username='ubuntu',
                                       timeout=600)

        server_steps.detach_floating_ip(server, nova_floating_ip)
        server_steps.delete_server(server)
