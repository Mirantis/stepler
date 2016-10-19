"""
---------------------------
Nova Rebuild Negative tests
---------------------------
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


def test_rebuild_in_paused_state(cirros_image, flavor_steps, flavor,
                                 network_steps, network, subnet, server_steps):
    """**Scenario:** Try to rebuild an instance in Paused state.

    **Setup:**

        #. Upload cirros image
        #. Create flavor
        #. Create network
        #. Create subnet

    **Steps:**

        #. Boot server from cirros image
        #. Pause server
        #. Try to rebuild server
        #. Check that rebuild fails and exception is called

    **Teardown:**

        #. Delete server
        #. Delete flavor
        #. Delete subnet
        #. Delete network
        #. Delete cirros image
    """
    for server_name in generate_ids('server', count=1):
        server = server_steps.create_server(server_name,
                                            image=cirros_image,
                                            flavor=flavor,
                                            networks=[network]
                                            )

        server_steps.pause_server(server)
        pytest.raises(Exception, "server_steps.rebuild_server(server)")

def test_rebuild_in_rescued_state(cirros_image, flavor_steps, flavor,
                                  network_steps, network, subnet, server_steps):
    """**Scenario:** Try to rebuild an instance in Rescued state.

    **Setup:**

        #. Upload cirros image
        #. Create flavor
        #. Create network
        #. Create subnet

    **Steps:**

        #. Boot server from cirros image
        #. Rescue server
        #. Try to rebuild server
        #. Check that rebuild fails and exception is called

    **Teardown:**

        #. Delete server
        #. Delete flavor
        #. Delete subnet
        #. Delete network
        #. Delete cirros image
    """
    for server_name in generate_ids('server', count=1):
        server = server_steps.create_server(server_name,
                                            image=cirros_image,
                                            flavor=flavor,
                                            networks=[network]
                                            )

        server_steps.rescue_server(server)
        pytest.raises(Exception, "server_steps.rebuild_server(server)")
