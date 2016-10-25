"""
-----------------------------
Dispatch an external event tests
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

# import stepler.conftest as con
from stepler.third_party.utils import generate_ids


def test_dispatch_external_event(cirros_image, create_network, create_subnet,
                                 flavor, security_group, create_server,
                                 os_faults_steps):
    """**Scenario:** Dispatch an external event

    **Setup:**

        #. Create cirros image
        #. Create network
        #. Create subnet
        #. Create server

    **Steps:**

        #. Check in nova-api log that the external event "network-vif-plugged"
        have been created for this instance and got "status": "completed":

    **Teardown:**

        #. Delete server
        #. Delete subnet
        #. Delete network
        #. Delete cirros image
    """
    my_network = create_network('net01')
    create_subnet(subnet_name='net01__subnet', network=my_network,
                  cidr='192.168.1.0/24')

    server_name = next(generate_ids('server'))
    server = create_server(
        server_name,
        image=cirros_image,
        flavor=flavor,
        networks=[my_network],
        security_groups=[security_group])

    nodes = os_faults_steps.get_nodes_for_service('nova-api')
    nova_log = '/var/log/nova/nova-api.log'

    s = 'server_external_events.*status.*completed' + \
        '.*name.*network-vif-plugged.*server_uuid.*' + server.id

    os_faults_steps.check_file_contains_line(nodes, nova_log, s, all=False)
