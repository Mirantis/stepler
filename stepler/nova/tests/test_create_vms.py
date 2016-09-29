"""
---------------------
Create VMs tests
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

from stepler.third_party.utils import generate_ids


@pytest.mark.testrail_id('1680616')
def test_launch_vm_from_image_using_all_flavors(
        security_group, create_server, cirros_image, keypair,
        flavor_steps, neutron_steps, server_steps):
    """Launch a VM from image using all standard flavors.

    Steps:
    1. Get list of all flavors.
    2. Create one VM for each flavor.

    https://mirantis.testrail.com/index.php?/cases/view/1680616
    """
    flavors = flavor_steps.findall()
    # TODO(akoryagin) net name may be different
    network = neutron_steps.find(name='admin_internal_net')

    for flavor in flavors:
        server_name = next(generate_ids(prefix='server', postfix=flavor.name))

        server = create_server(
            server_name, cirros_image, flavor, network, keypair,
            [security_group])

        server_steps.delete_server(server)
