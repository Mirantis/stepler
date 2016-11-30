"""
-------------------
Nova evacuate tests
-------------------
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

from stepler import config


pytestmark = [pytest.mark.requires("computes_count >= 2"),
              pytest.mark.destructive]


@pytest.mark.idempotent_id('7c22590a-bde4-4137-9cc3-47de74d1ac1f',
                           boot_from_volume=False)
@pytest.mark.idempotent_id('cce58032-5c04-4546-a52b-9a5607148ab7',
                           boot_from_volume=True)
@pytest.mark.parametrize('evacuated_servers', [{'boot_from_volume': False},
                                               {'boot_from_volume': True}
                                               ],
                         ids=['boot_from_image', 'boot_from_volume'],
                         indirect=['evacuated_servers'])
def test_evacuate_servers(evacuated_servers,
                          nova_api_node,
                          nova_create_floating_ip,
                          server_steps,
                          os_faults_steps):
    """**Scenario:** Evacuate servers from the "failed" host to other hosts.

    **Setup:**

    #. Upload cirros image
    #. Create network with subnet and router
    #. Create security group with allowed ping and ssh rules
    #. Create flavor
    #. Boot two servers from image or volume on the same hypervisor

    **Steps:**

    #. Set the hypervisor where servers are scheduled to "failed" state
    #. Start evacuation for all servers
    #. Check that every server is rescheduled to other hypervisor
    #. Check that every evacuated server has an ACTIVE status
    #. Assign floating ip for all servers
    #. Send pings between all servers to check network connectivity

    **Teardown:**

    #. Delete all servers
    #. Delete flavor
    #. Delete security group
    #. Delete network, subnet, router
    #. Delete cirros image
    """
    failed_compute_node = os_faults_steps.get_node(
        fqdns=[getattr(evacuated_servers[0], config.SERVER_ATTR_HOST)])
    os_faults_steps.terminate_service(config.NOVA_COMPUTE,
                                      nodes=failed_compute_node)
    os_faults_steps.nova_compute_force_down(
        nova_api_node,
        getattr(evacuated_servers[0], config.SERVER_ATTR_HOST))
    server_steps.evacuate_servers(evacuated_servers)

    for server in evacuated_servers:
        floating_ip = nova_create_floating_ip()
        server_steps.attach_floating_ip(server, floating_ip)

    server_steps.check_ping_between_servers_via_floating(
        evacuated_servers,
        ip_types=(config.FLOATING_IP,),
        timeout=config.PING_BETWEEN_SERVERS_TIMEOUT)
