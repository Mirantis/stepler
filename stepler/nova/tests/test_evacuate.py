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


pytestmark = pytest.mark.requires("computes_count >= 2")
# TODO(akholkin): mark fails before skipping. doing todo not to lose the mark
# pytestmark = pytest.mark.destructive


@pytest.mark.idempotent_id('7c22590a-bde4-4137-9cc3-47de74d1ac1f',
                           servers_to_evacuate={'boot_from_volume': False})
@pytest.mark.idempotent_id('cce58032-5c04-4546-a52b-9a5607148ab7',
                           servers_to_evacuate={'boot_from_volume': True})
@pytest.mark.parametrize('servers_to_evacuate', [{'boot_from_volume': False},
                                                 {'boot_from_volume': True}
                                                 ],
                         ids=['boot_from_image', 'boot_from_volume'],
                         indirect=['servers_to_evacuate'])
def test_evacuate_servers(servers_to_evacuate,
                          nova_api_node,
                          server_steps,
                          os_faults_steps):
    """**Scenario:** Evacuate servers from the "failed" host to other hosts.

    **Setup:**

    #. Upload cirros image
    #. Create network with subnet and router
    #. Create security group with allowed ping and ssh rules
    #. Create flavor
    #. Boot two servers from image or volume on the same hypervisor
    #. Create two floating IPs and attach them to servers

    **Steps:**

    #. Set the hypervisor where servers are scheduled to "failed" state
    #. Start evacuation for all servers
    #. Check that every server is rescheduled to other hypervisor
    #. Check that every evacuated server has an ACTIVE status
    #. Send pings between all servers to check network connectivity

    **Teardown:**

    #. Delete all servers
    #. Delete flavor
    #. Delete security group
    #. Delete network, subnet, router
    #. Delete floating IPs
    #. Delete cirros image
    """
    failed_compute_node = os_faults_steps.get_node(
        fqdns=[getattr(servers_to_evacuate[0],
                       config.SERVER_ATTR_HYPERVISOR_HOSTNAME)])
    os_faults_steps.terminate_service(config.NOVA_COMPUTE,
                                      nodes=failed_compute_node)
    os_faults_steps.nova_compute_force_down(
        nova_api_node,
        getattr(servers_to_evacuate[0], config.SERVER_ATTR_HOST))
    server_steps.evacuate_servers(servers_to_evacuate)

    server_steps.check_ping_between_servers_via_floating(
        servers_to_evacuate,
        timeout=config.PING_BETWEEN_SERVERS_TIMEOUT)


@pytest.mark.idempotent_id('7a676445-4b55-445c-98c2-8744b3cdbd9f',
                           servers_to_evacuate={'boot_from_volume': False})
@pytest.mark.idempotent_id('0378f5ee-9092-40e3-9c71-9423c7190db6',
                           servers_to_evacuate={'boot_from_volume': True})
@pytest.mark.parametrize('servers_to_evacuate', [{'boot_from_volume': False},
                                                 {'boot_from_volume': True}
                                                 ],
                         ids=['boot_from_image', 'boot_from_volume'],
                         indirect=['servers_to_evacuate'])
def test_evacuate_servers_with_volumes(servers_with_volumes_to_evacuate,
                                       nova_api_node,
                                       server_steps,
                                       os_faults_steps,
                                       volume_steps):
    """**Scenario:** Evacuate servers with volumes attached from the "failed"
                     host to other hosts.

    **Setup:**

    #. Upload cirros image
    #. Create network with subnet and router
    #. Create security group with allowed ping and ssh rules
    #. Create flavor
    #. Boot two servers from image or volume on the same hypervisor
    #. Create two floating IPs and attach them to servers
    #. Create two volumes and attach them to servers

    **Steps:**

    #. Set the hypervisor where servers are scheduled to "failed" state
    #. Start evacuation for all servers
    #. Check that every server is rescheduled to other hypervisor
    #. Check that every evacuated server has an ACTIVE status
    #. Check that all volumes are in 'in-use' state
    #. Send pings between all servers to check network connectivity

    **Teardown:**

    #. Delete all servers
    #. Delete flavor
    #. Delete security group
    #. Delete network, subnet, router
    #. Delete floating IPs
    #. Delete volumes
    #. Delete cirros image
    """
    servers, volumes = servers_with_volumes_to_evacuate
    failed_compute_node = os_faults_steps.get_node(
        fqdns=[getattr(servers[0],
                       config.SERVER_ATTR_HYPERVISOR_HOSTNAME)])
    os_faults_steps.terminate_service(config.NOVA_COMPUTE,
                                      nodes=failed_compute_node)
    os_faults_steps.nova_compute_force_down(
        nova_api_node, getattr(servers[0], config.SERVER_ATTR_HOST))
    server_steps.evacuate_servers(servers)

    for volume in volumes:
        volume_steps.check_volume_status(volume,
                                         statuses=[config.STATUS_INUSE])

    server_steps.check_ping_between_servers_via_floating(
        servers,
        timeout=config.PING_BETWEEN_SERVERS_TIMEOUT)


@pytest.mark.idempotent_id('66b2103d-683c-440d-b94f-c4cbb23d6ab2',
                           servers_to_evacuate={'boot_from_volume': False})
@pytest.mark.idempotent_id('7c7db151-fda0-4324-94a8-156a0eb7cf9a',
                           servers_to_evacuate={'boot_from_volume': True})
@pytest.mark.parametrize('servers_to_evacuate', [{'boot_from_volume': False},
                                                 {'boot_from_volume': True}
                                                 ],
                         ids=['boot_from_image', 'boot_from_volume'],
                         indirect=['servers_to_evacuate'])
def test_evacuate_locked_servers(servers_to_evacuate,
                                 nova_api_node,
                                 server_steps,
                                 os_faults_steps):
    """**Scenario:** Evacuate locked servers from the "failed" host
                     to other hosts.

    **Setup:**

    #. Upload cirros image
    #. Create network with subnet and router
    #. Create security group with allowed ping and ssh rules
    #. Create flavor
    #. Boot two servers from image or volume on the same hypervisor
    #. Create two floating IPs and attach them to servers

    **Steps:**

    #. Lock previously created servers
    #. Set the hypervisor where servers are scheduled to "failed" state
    #. Start evacuation for all servers
    #. Check that every server is rescheduled to other hypervisor
    #. Check that every evacuated server has an ACTIVE status and locked=True
    #. Send pings between all servers to check network connectivity

    **Teardown:**

    #. Delete all servers
    #. Delete flavor
    #. Delete security group
    #. Delete network, subnet, router
    #. Delete floating IPs
    #. Delete cirros image
    """
    locked_servers = []
    for server in servers_to_evacuate:
        server_steps.lock_server(server)
        locked_servers.append(server)

    failed_compute_node = os_faults_steps.get_node(
        fqdns=[getattr(locked_servers[0],
                       config.SERVER_ATTR_HYPERVISOR_HOSTNAME)])
    os_faults_steps.terminate_service(config.NOVA_COMPUTE,
                                      nodes=failed_compute_node)
    os_faults_steps.nova_compute_force_down(
        nova_api_node,
        getattr(locked_servers[0], config.SERVER_ATTR_HOST))
    server_steps.evacuate_servers(locked_servers)

    for server in locked_servers:
        server_steps.check_server_attribute(server,
                                            attr=config.SERVER_ATTR_LOCKED,
                                            value=True)

    server_steps.check_ping_between_servers_via_floating(
        locked_servers,
        timeout=config.PING_BETWEEN_SERVERS_TIMEOUT)


@pytest.mark.idempotent_id('92e34b40-2f30-4da0-9dbf-76eebeec1fc5')
def test_evacuate_rescue_servers(servers_to_evacuate,
                                 nova_api_node,
                                 server_steps,
                                 os_faults_steps):
    """**Scenario:** Try to evacuate servers in Rescue state.

    **Setup:**

    #. Upload cirros image
    #. Create network with subnet and router
    #. Create security group with allowed ping and ssh rules
    #. Create flavor
    #. Boot two servers from image or volume on the same hypervisor
    #. Create two floating IPs and attach them to servers

    **Steps:**

    #. Rescue previously created servers
    #. Set the hypervisor where servers are scheduled to "failed" state
    #. Start evacuation for all servers
    #. Check that evacuation fails and exception is called

    **Teardown:**

    #. Delete all servers
    #. Delete flavor
    #. Delete security group
    #. Delete network, subnet, router
    #. Delete floating IPs
    #. Delete cirros image
    """
    rescue_servers = []
    for server in servers_to_evacuate:
        server_steps.rescue_server(server)
        rescue_servers.append(server)

    failed_compute_node = os_faults_steps.get_node(
        fqdns=[getattr(rescue_servers[0],
                       config.SERVER_ATTR_HYPERVISOR_HOSTNAME)])
    os_faults_steps.terminate_service(config.NOVA_COMPUTE,
                                      nodes=failed_compute_node)
    os_faults_steps.nova_compute_force_down(
        nova_api_node,
        getattr(rescue_servers[0], config.SERVER_ATTR_HOST))
    server_steps.check_servers_not_evacuated_in_rescue_state(rescue_servers)


@pytest.mark.idempotent_id('c50b0758-3f61-422f-a0bd-ab030da4edd4')
def test_evacuate_shelved_servers(servers_to_evacuate,
                                  nova_api_node,
                                  server_steps,
                                  os_faults_steps):
    """**Scenario:** Try to evacuate servers in Shelved state.

    **Setup:**

    #. Upload cirros image
    #. Create network with subnet and router
    #. Create security group with allowed ping and ssh rules
    #. Create flavor
    #. Boot two servers from image or volume on the same hypervisor
    #. Create two floating IPs and attach them to servers

    **Steps:**

    #. Shelve previously created servers
    #. Set the hypervisor where servers are scheduled to "failed" state
    #. Start evacuation for all servers
    #. Check that evacuation fails and exception is called

    **Teardown:**

    #. Delete all servers
    #. Delete flavor
    #. Delete security group
    #. Delete network, subnet, router
    #. Delete floating IPs
    #. Delete cirros image
    """
    shelved_servers = []
    for server in servers_to_evacuate:
        server_steps.shelve_server(server)
        shelved_servers.append(server)

    failed_compute_node = os_faults_steps.get_node(
        fqdns=[getattr(shelved_servers[0],
                       config.SERVER_ATTR_HYPERVISOR_HOSTNAME)])
    os_faults_steps.terminate_service(config.NOVA_COMPUTE,
                                      nodes=failed_compute_node)
    os_faults_steps.nova_compute_force_down(
        nova_api_node,
        getattr(shelved_servers[0], config.SERVER_ATTR_HOST))
    server_steps.check_servers_not_evacuated_in_shelved_state(shelved_servers)


@pytest.mark.idempotent_id('a56bfab5-23d9-405f-9e2e-dd861d863233')
def test_evacuate_paused_servers(servers_to_evacuate,
                                 nova_api_node,
                                 server_steps,
                                 os_faults_steps):
    """**Scenario:** Try to evacuate servers in Paused state.

    **Setup:**

    #. Upload cirros image
    #. Create network with subnet and router
    #. Create security group with allowed ping and ssh rules
    #. Create flavor
    #. Boot two servers from image or volume on the same hypervisor
    #. Create two floating IPs and attach them to servers

    **Steps:**

    #. Pause previously created servers
    #. Set the hypervisor where servers are scheduled to "failed" state
    #. Start evacuation for all servers
    #. Check that evacuation fails and exception is called

    **Teardown:**

    #. Delete all servers
    #. Delete flavor
    #. Delete security group
    #. Delete network, subnet, router
    #. Delete floating IPs
    #. Delete cirros image
    """
    paused_servers = []
    for server in servers_to_evacuate:
        server_steps.pause_server(server)
        paused_servers.append(server)

    failed_compute_node = os_faults_steps.get_node(
        fqdns=[getattr(paused_servers[0],
                       config.SERVER_ATTR_HYPERVISOR_HOSTNAME)])
    os_faults_steps.terminate_service(config.NOVA_COMPUTE,
                                      nodes=failed_compute_node)
    os_faults_steps.nova_compute_force_down(
        nova_api_node,
        getattr(paused_servers[0], config.SERVER_ATTR_HOST))
    server_steps.check_servers_not_evacuated_in_paused_state(paused_servers)


@pytest.mark.idempotent_id('5c390bbc-84f1-44a5-a7ec-4183afd961e6')
def test_evacuate_resized_servers(servers_to_evacuate,
                                  small_flavor,
                                  nova_api_node,
                                  server_steps,
                                  os_faults_steps):
    """**Scenario:** Try to evacuate servers in Resized state.

    **Setup:**

    #. Upload cirros image
    #. Create network with subnet and router
    #. Create security group with allowed ping and ssh rules
    #. Create flavor
    #. Boot two servers from image or volume on the same hypervisor
    #. Create two floating IPs and attach them to servers

    **Steps:**

    #. Resize previously created servers with m1.small flavor
    #. Set the hypervisor where servers are scheduled to "failed" state
    #. Start evacuation for all servers
    #. Check that evacuation fails and exception is called

    **Teardown:**

    #. Delete all servers
    #. Delete flavors
    #. Delete security group
    #. Delete network, subnet, router
    #. Delete floating IPs
    #. Delete cirros image
    """
    resized_servers = []
    for server in servers_to_evacuate:
        server_steps.resize(server, small_flavor)
        resized_servers.append(server)

    failed_compute_node = os_faults_steps.get_node(
        fqdns=[getattr(resized_servers[0],
                       config.SERVER_ATTR_HYPERVISOR_HOSTNAME)])
    os_faults_steps.terminate_service(config.NOVA_COMPUTE,
                                      nodes=failed_compute_node)
    os_faults_steps.nova_compute_force_down(
        nova_api_node,
        getattr(resized_servers[0], config.SERVER_ATTR_HOST))
    server_steps.check_servers_not_evacuated_in_resized_state(resized_servers)


@pytest.mark.idempotent_id('a4731b82-9a7c-4bd7-a4ce-c12f01b693d8')
def test_evacuate_servers_to_initial_compute(servers_to_evacuate,
                                             nova_api_node,
                                             server_steps,
                                             os_faults_steps):
    """**Scenario:** Try to evacuate servers to initial "failed" compute node.

    **Setup:**

    #. Upload cirros image
    #. Create network with subnet and router
    #. Create security group with allowed ping and ssh rules
    #. Create flavor
    #. Boot two servers from image or volume on the same hypervisor
    #. Create two floating IPs and attach them to servers

    **Steps:**

    #. Set the hypervisor where servers are scheduled to "failed" state
    #. Start evacuation for all servers to their "native" compute node
    #. Check that evacuation fails and exception is called

    **Teardown:**

    #. Delete all servers
    #. Delete flavor
    #. Delete security group
    #. Delete network, subnet, router
    #. Delete floating IPs
    #. Delete cirros image
    """
    failed_compute_node = os_faults_steps.get_node(
        fqdns=[getattr(servers_to_evacuate[0],
                       config.SERVER_ATTR_HYPERVISOR_HOSTNAME)])
    os_faults_steps.terminate_service(config.NOVA_COMPUTE,
                                      nodes=failed_compute_node)
    os_faults_steps.nova_compute_force_down(
        nova_api_node,
        getattr(servers_to_evacuate[0], config.SERVER_ATTR_HOST))
    server_steps.check_servers_not_evacuated_to_initial_compute(
        servers_to_evacuate,
        getattr(servers_to_evacuate[0], config.SERVER_ATTR_HOST))
