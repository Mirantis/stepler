"""
--------------------------------
Dispatch an external event tests
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

from stepler import config
from stepler.third_party import utils

EVENT_RECORD = 'server_external_events.*status.*completed' + \
               '.*name.*network-vif-plugged.*server_uuid.*'


def test_dispatch_external_event(
        cirros_image,
        flavor,
        security_group,
        create_network,
        create_subnet,
        server_steps,
        os_faults_steps):
    """**Scenario:** Dispatch an external event.

    **Setup:**

    #. Create cirros image
    #. Create network
    #. Create subnet
    #. Create server

    **Steps:**

    #. Check in nova-api log that the external event "network-vif-plugged"
       have been created for this instance and got "status": "completed"

    **Teardown:**

    #. Delete server
    #. Delete subnet
    #. Delete network
    #. Delete cirros image
    """
    network_name = next(utils.generate_ids('network'))
    network = create_network(network_name)
    subnet_name = next(utils.generate_ids('subnet'))
    create_subnet(subnet_name, network=network, cidr='192.168.1.0/24')

    server = server_steps.create_servers(
        image=cirros_image,
        flavor=flavor,
        networks=[network],
        security_groups=[security_group])[0]

    nodes = os_faults_steps.get_nodes(service_names=[config.NOVA_API])

    os_faults_steps.check_file_contains_line(nodes,
                                             config.NOVA_API_LOG_FILE,
                                             EVENT_RECORD + server.id,
                                             all=False)
