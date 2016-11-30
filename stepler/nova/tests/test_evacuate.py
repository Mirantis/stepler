"""
-----------------------
Nova evacuate tests
-----------------------
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


pytestmark = [pytest.mark.requires("computes_count_gte(2)"),
              pytest.mark.destructive]


@pytest.mark.idempotent_id('df839312-db9d-4a8d-8bff-f6df0ca963c4')
def test_evacuate_ephemeral_instances_on_lvm(cirros_image,
                                             network,
                                             subnet,
                                             router,
                                             security_group,
                                             flavor,
                                             add_router_interfaces,
                                             keypair,
                                             nova_api_node,
                                             hypervisor_steps,
                                             server_steps,
                                             nova_create_floating_ip,
                                             os_faults_steps):
    """**Scenario:** Evacuate instances from the "failed" host to other hosts.

    **Setup:**

    #. Upload cirros image
    #. Create network
    #. Create subnet
    #. Create router
    #. Create security group with allowed ping and ssh rules
    #. Create flavor

    **Steps:**

    #. Set router default gateway to public network
    #. Add router interface to created network
    #. Boot 2 servers on the same hypervisor
    #. Set this hypervisor to "failed" state
    #. Start evacuation for all servers
    #. Check that every instance is rescheduled to other hypervisor
    #. Check that every evacuated instance has an ACTIVE status
    #. Assign floating ip for all servers
    #. Send pings between all servers to check network connectivity

    **Teardown:**

    #. Delete all servers
    #. Delete flavor
    #. Delete security group
    #. Delete router
    #. Delete subnet
    #. Delete network
    #. Delete cirros image
    """
    add_router_interfaces(router, [subnet])
    hypervisor = hypervisor_steps.get_hypervisors()[0]

    servers = server_steps.create_servers(
        count=2,
        image=cirros_image,
        flavor=flavor,
        networks=[network],
        keypair=keypair,
        security_groups=[security_group],
        availability_zone='nova:' + hypervisor.hypervisor_hostname,
        username=config.CIRROS_USERNAME)

    failed_node = os_faults_steps.get_node(
        fqdns=[hypervisor.hypervisor_hostname])
    os_faults_steps.terminate_service(config.NOVA_COMPUTE, nodes=failed_node)
    os_faults_steps.execute_cmd(nodes=nova_api_node,
                                cmd='bash -c '
                                    '"%s && nova service-force-down %s %s "' %
                                    (config.OPENRC_ACTIVATE_CMD,
                                     hypervisor.hypervisor_hostname,
                                     config.NOVA_COMPUTE))
    server_steps.evacuate_servers(servers, on_shared_storage=False)

    for server in servers:
        floating_ip = nova_create_floating_ip()
        server_steps.attach_floating_ip(server, floating_ip)

    server_steps.check_ping_between_servers_via_floating(
        servers,
        ip_types=(config.FLOATING_IP,),
        timeout=config.PING_BETWEEN_SERVERS_TIMEOUT)


@pytest.mark.requires("nova_ceph")
@pytest.mark.idempotent_id('4dabdb64-d014-4923-a452-06063fcabe4b')
def test_evacuate_ephemeral_instances_on_ceph(cirros_image,
                                              network,
                                              subnet,
                                              router,
                                              security_group,
                                              flavor,
                                              add_router_interfaces,
                                              keypair,
                                              nova_api_node,
                                              hypervisor_steps,
                                              server_steps,
                                              nova_create_floating_ip,
                                              os_faults_steps):
    """**Scenario:** Evacuate instances from the "failed" host to other hosts.

    **Setup:**

    #. Upload cirros image
    #. Create network
    #. Create subnet
    #. Create router
    #. Create security group with allowed ping and ssh rules
    #. Create flavor

    **Steps:**

    #. Set router default gateway to public network
    #. Add router interface to created network
    #. Boot 2 servers on the same hypervisor
    #. Set this hypervisor to "failed" state
    #. Start evacuation for all servers
    #. Check that every instance is rescheduled to other hypervisor
    #. Check that every evacuated instance has an ACTIVE status
    #. Assign floating ip for all servers
    #. Send pings between all servers to check network connectivity

    **Teardown:**

    #. Delete all servers
    #. Delete flavor
    #. Delete security group
    #. Delete router
    #. Delete subnet
    #. Delete network
    #. Delete cirros image
    """
    add_router_interfaces(router, [subnet])
    hypervisor = hypervisor_steps.get_hypervisors()[0]

    servers = server_steps.create_servers(
        count=2,
        image=cirros_image,
        flavor=flavor,
        networks=[network],
        keypair=keypair,
        security_groups=[security_group],
        availability_zone='nova:' + hypervisor.hypervisor_hostname,
        username=config.CIRROS_USERNAME)

    failed_node = os_faults_steps.get_node(
        fqdns=[hypervisor.hypervisor_hostname])
    os_faults_steps.terminate_service(config.NOVA_COMPUTE, nodes=failed_node)
    os_faults_steps.execute_cmd(nodes=nova_api_node,
                                cmd='bash -c '
                                    '"%s && nova service-force-down %s %s "' %
                                    (config.OPENRC_ACTIVATE_CMD,
                                     hypervisor.hypervisor_hostname,
                                     config.NOVA_COMPUTE))
    server_steps.evacuate_servers(servers, on_shared_storage=True)

    for server in servers:
        floating_ip = nova_create_floating_ip()
        server_steps.attach_floating_ip(server, floating_ip)

    server_steps.check_ping_between_servers_via_floating(
        servers,
        ip_types=(config.FLOATING_IP,),
        timeout=config.PING_BETWEEN_SERVERS_TIMEOUT)
