"""
-----------------------------
Nova basic verification tests
-----------------------------
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


def test_boot_instance_from_volume_bigger_than_flavor(
        security_group, nova_floating_ip, cirros_image, flavor_steps,
        neutron_steps, cinder_steps, server_steps, create_server):
    """[Bug 1517671] Boot instance from volume bigger than flavor size."""
    flavor = flavor_steps.get_flavor(name='m1.tiny')
    volume_size = flavor.disk + 1
    volume = cinder_steps.create_volume(
        next(generate_ids('volume')),
        size=volume_size,
        image=cirros_image)
    block_device_mapping = {'vda': volume.id}
    network = neutron_steps.get_network(name='admin_internal_net')

    server_name = next(generate_ids('server', count=1))
    server = create_server(server_name,
                           image=None,
                           flavor=flavor,
                           network=network,
                           security_groups=[security_group],
                           block_device_mapping=block_device_mapping)

    server_steps.attach_floating_ip(server, nova_floating_ip)
    server_steps.check_ping_to_server_floating(server, timeout=5 * 60)
